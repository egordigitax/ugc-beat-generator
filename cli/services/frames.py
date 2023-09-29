from typing import List

from PIL import ImageDraw

from .graphics import GraphicsGeneratorInterface, GraphicsGeneratorParams, GraphicsGenerator
from .waveforms import WaveformGeneratorInterface, WaveformGeneratorParams
from dataclasses import dataclass
from PIL import Image, ImageFilter
import blend_modes
import numpy as np
import math
from joblib import Parallel, delayed


@dataclass
class FrameGeneratorParams:
    shade_path: str
    output_path: str
    waveform_generator: WaveformGeneratorInterface
    graphics_generator: GraphicsGenerator
    jobs: int


@dataclass
class UGCParams:
    avatar_path: str
    avatar_size: int
    framerate: int
    width: int
    height: int
    blur_radius: int
    waveform_generator_params: WaveformGeneratorParams
    graphics_generator_params: GraphicsGeneratorParams


@dataclass
class ProcessingCache:
    avatar: Image.Image = None
    background: Image.Image = None
    shade: Image.Image = None
    total_frames_count: int = None
    scene_sequence: List[Image.Image] = None
    user_info_sequence: List[Image.Image] = None
    overlay_sequence: List[Image.Image] = None
    intensities: np.ndarray = None
    max_digits: int = None


class BaseFrameGenerator:
    def process(self):
        pass


class FrameGeneratorLegacy(BaseFrameGenerator):
    def __init__(self,
                 generator_params: FrameGeneratorParams,
                 ugc_params: UGCParams,
                 verbose: bool) -> None:
        self.__generator_params = generator_params
        self.__ugc_params = ugc_params
        self.__shade = Image.open(self.__generator_params.shade_path)
        self.__verbose = verbose
        self.__logger("generator created")

    def __logger(self, msg: str):
        if self.__verbose:
            print(msg)

    def __make_corners(self, avatar: Image, rad: int) -> Image:
        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
        alpha = Image.new('L', avatar.size, 255)
        w, h = avatar.size

        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        avatar.putalpha(alpha)
        return avatar

    def create_frame(self, intensity: float, avatar: Image, background: Image) -> Image:
        return self.__create_save_frame_img_proto(intensity, avatar, background)

    def __create_save_frame_img_proto(self,
                                      intensity: float, avatar: Image, background: Image) -> Image:

        reds = np.zeros([self.__ugc_params.height, self.__ugc_params.width, 4], dtype=np.float32)

        frame = Image.fromarray((reds * 255).astype(np.uint8), "RGBA")

        def new_size():
            return int(self.__ugc_params.height * (intensity + 1.))

        def new_offset():
            x_offset = int((self.__ugc_params.width - new_size()) / 2.0)
            y_offset = int((self.__ugc_params.height - new_size()) / 2.0)

            return x_offset, y_offset

        blurred_resized = background.resize((new_size(), new_size()))

        frame.paste(blurred_resized, new_offset())

        frame = Image.alpha_composite(frame, self.__shade)

        frame.paste(avatar, (160, 246), avatar)

        return frame

    def __create_save_frame_img(self,
                                frame_num: int, max_digits: int, intensity: float, avatar: Image, background: Image):

        new_img = self.__create_save_frame_img_proto(intensity, avatar, background)
        new_img.save('{}/img{}.png'
                     .format(self.__generator_params.output_path, str(frame_num).zfill(max_digits)))

    def generator(self, cache: ProcessingCache, frame_num: int):

        frame_to_time = float(frame_num) / float(self.__ugc_params.framerate)
        audio_time_sample = int(frame_to_time * self.__generator_params.waveform_generator.sample_rate())

        if audio_time_sample < len(cache.intensities):
            intensity = cache.intensities[audio_time_sample]

            self.__logger("generator: FTT {} ATS {} I {}".format(frame_to_time, audio_time_sample, intensity))

            self.__create_save_frame_img(
                frame_num, cache.max_digits, intensity,
                cache.avatar, cache.background)

    def process(self):
        cache = ProcessingCache()

        self.__logger("opening avatar")

        avatar = Image.open(self.__ugc_params.avatar_path)
        avatar = avatar.convert("RGBA")
        avatar = avatar.resize((self.__ugc_params.avatar_size, self.__ugc_params.avatar_size))
        avatar.putalpha(255)

        self.__logger("opened {}".format(avatar.mode))

        self.__logger("opening background")

        cache.background = Image.open(self.__ugc_params.avatar_path)
        cache.background = cache.background.convert("RGBA")
        cache.background.putalpha(255)

        self.__logger("resizing background")

        cache.background = cache.background.resize((self.__ugc_params.height, self.__ugc_params.height))

        self.__logger("filtering background")

        cache.background = cache.background.filter(ImageFilter.GaussianBlur(self.__ugc_params.blur_radius))

        self.__logger("make corners")

        cache.avatar = self.__make_corners(avatar, 40)

        self.__logger("forming duration")

        duration = math.ceil(self.__generator_params.waveform_generator.duration())

        total_frames_count = duration * self.__ugc_params.framerate

        cache.max_digits = int(math.log10(total_frames_count)) + 1
        cache.intensities = \
            self.__generator_params.waveform_generator.process(self.__ugc_params.waveform_generator_params)

        Parallel(n_jobs=self.__generator_params.jobs, verbose=0 if not self.__verbose else total_frames_count)(
            delayed(self.generator)(cache, i) for i in range(total_frames_count))


class FrameGenerator(BaseFrameGenerator):
    def __init__(self,
                 generator_params: FrameGeneratorParams,
                 ugc_params: UGCParams,
                 verbose: bool) -> None:
        self.__generator_params = generator_params
        self.__ugc_params = ugc_params
        self.__verbose = verbose
        self.__logger("generator created")

    def __logger(self, msg: str):
        if self.__verbose:
            print(msg)

    def create_frame(self, intensity: float, avatar: Image.Image, background: Image.Image) -> Image.Image:
        raise NotImplemented

    @staticmethod
    def img_to_np(image: Image.Image):
        np_arr = np.array(image)
        np_float = np_arr.astype(float)
        return np_float

    @staticmethod
    def np_to_img(np_float):
        img_decode = np.uint8(np_float)
        image = Image.fromarray(img_decode)
        return image

    def __create_save_frame_img_proto(self,
                                      intensity: float,
                                      scene_sequence_frame: Image.Image,
                                      user_info_frame: Image.Image,
                                      overlay_frame: Image.Image) -> Image.Image:

        self.__logger('compositing...')

        frame = Image.new("RGBA", (self.__ugc_params.width, self.__ugc_params.height), (255, 255, 255, 255))
        frame.paste(scene_sequence_frame, None, scene_sequence_frame)
        frame.paste(user_info_frame, None, user_info_frame)

        if not overlay_frame:
            return frame

        frame = self.np_to_img(blend_modes.overlay(self.img_to_np(frame), self.img_to_np(overlay_frame), 0.1))  # можно использовать intensity
        return frame

    def __create_save_frame_img(self,
                                frame_num: int,
                                max_digits: int,
                                intensity: float,
                                scene_sequence_frame: Image.Image,
                                user_info_frame: Image.Image,
                                overlay_frame: Image.Image
                                ):

        new_img = self.__create_save_frame_img_proto(intensity, scene_sequence_frame, user_info_frame, overlay_frame)
        new_img.save('{}/img{}.png'
                     .format(self.__generator_params.output_path, str(frame_num).zfill(max_digits)))

    def generator(self, cache: ProcessingCache, frame_num: int):

        def get_user_info_frame(_frame_num, _cache):
            if _frame_num < len(_cache.user_info_sequence):
                return _cache.user_info_sequence[_frame_num]
            else:
                return _cache.user_info_sequence[-1]

        def get_overlay_frame(_frame_num, _cache):
            if _cache.overlay_sequence:
                return _cache.overlay_sequence[_frame_num % len(_cache.overlay_sequence)]
            else:
                return None

        def get_main_scene_frames(_intensity, _cache):
            return _cache.scene_sequence[round(_intensity * (len(cache.scene_sequence) - 1))]

        frame_to_time = float(frame_num) / float(self.__ugc_params.framerate)
        audio_time_sample = int(frame_to_time * self.__generator_params.waveform_generator.sample_rate())

        if audio_time_sample < len(cache.intensities):
            chunks = np.array_split(cache.intensities, cache.total_frames_count)
            intensity = np.mean(chunks[frame_num])

            self.__logger("generator: FTT {} ATS {} I {}".format(frame_to_time, audio_time_sample, intensity))

            scene_sequence_frame = get_main_scene_frames(intensity, cache)
            user_info_frame = get_user_info_frame(frame_num, cache)
            overlay_frame = get_overlay_frame(frame_num, cache)

            self.__logger(f'all graphics prepared for {frame_num} frame')

            self.__create_save_frame_img(
                frame_num=frame_num,
                max_digits=cache.max_digits,
                intensity=intensity,
                scene_sequence_frame=scene_sequence_frame,
                overlay_frame=overlay_frame,
                user_info_frame=user_info_frame
            )

    def process(self):
        cache = ProcessingCache()

        self.__logger("opening avatar")

        avatar = Image.open(self.__ugc_params.avatar_path)
        avatar = avatar.convert("RGBA")
        avatar = avatar.resize((self.__ugc_params.avatar_size, self.__ugc_params.avatar_size))
        avatar.putalpha(255)

        self.__logger("opened {}".format(avatar.mode))

        self.__logger("opening background")

        cache.background = Image.open(self.__ugc_params.avatar_path)
        cache.background = cache.background.convert("RGBA")
        cache.background.putalpha(255)

        self.__logger("resizing background")

        cache.background = cache.background.resize((self.__ugc_params.height, self.__ugc_params.height))

        self.__logger("filtering background")

        cache.background = cache.background.filter(ImageFilter.GaussianBlur(self.__ugc_params.blur_radius))

        self.__logger("make corners")

        cache.avatar = avatar

        self.__logger("forming duration")

        duration = math.ceil(self.__generator_params.waveform_generator.duration())

        total_frames_count = duration * self.__ugc_params.framerate
        cache.total_frames_count = total_frames_count

        cache.max_digits = int(math.log10(total_frames_count)) + 1
        cache.intensities = \
            self.__generator_params.waveform_generator.process(self.__ugc_params.waveform_generator_params)

        cache.scene_sequence = self.__generator_params.graphics_generator.process_scene_frames()
        cache.user_info_sequence = self.__generator_params.graphics_generator.process_user_info_frames()
        cache.overlay_sequence = self.__generator_params.graphics_generator.process_overlay_frames()

        Parallel(n_jobs=self.__generator_params.jobs, verbose=0 if not self.__verbose else total_frames_count)(
            delayed(self.generator)(cache, i) for i in range(total_frames_count))


class FrameGeneratorLoader:
    @staticmethod
    def load(generator_params: FrameGeneratorParams,
             ugc_params: UGCParams, verbose: bool, legacy: bool) -> BaseFrameGenerator:

        if legacy:
            return FrameGeneratorLegacy(generator_params, ugc_params, verbose)
        else:
            return FrameGenerator(generator_params, ugc_params, verbose)
