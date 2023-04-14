from PIL import Image, ImageFont, ImageDraw
from waveforms import WaveformGenerator
from dataclasses import dataclass
from PIL import Image, ImageFilter
import numpy as np
import math
from joblib import Parallel, delayed




@dataclass
class FrameGeneratorParams:
    shade_path: str
    output_path: str
    waveform_generator: WaveformGenerator
    jobs: int

@dataclass
class UGCParams:
    avatar_path: str
    avatar_size: int
    framerate: int
    width: int
    height: int
    smooth: int

@dataclass
class ProcessingCache:
    avatar: Image = None
    background: Image = None
    shade: Image = None
    intensities: np.ndarray = None
    max_digits: int = None




class FrameGenerator:
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
    
        
    def __create_save_frame_img_proto(self, 
        intensity: float, avatar: Image, background: Image) -> Image:

        reds = np.zeros([self.__ugc_params.height, self.__ugc_params.width, 4], dtype=np.float32)
        
        frame = Image.fromarray((reds * 255).astype(np.uint8), "RGBA")

        def new_size():
            return int((1.0 - intensity) * self.__ugc_params.height + (intensity) * self.__ugc_params.height * 2)
        def new_offset(size):
            return int((1.0 - intensity) * (self.__ugc_params.width - self.__ugc_params.height)/2 + (intensity) * (self.__ugc_params.height - size)/2)


        blurred_resized = background.resize((new_size(), new_size()))


        frame.paste(blurred_resized, (new_offset(self.__ugc_params.height * 2), 0))


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

            self.__create_save_frame_img(
                frame_num, cache.max_digits, intensity, 
                cache.avatar, cache.background)
    


    def process(self):
        cache = ProcessingCache()

        self.__logger("opening avatar")


        avatar = Image.open(self.__ugc_params.avatar_path)
        avatar = avatar.resize((self.__ugc_params.avatar_size, self.__ugc_params.avatar_size))
        avatar.putalpha(255)

        self.__logger("opening background")

        
        cache.background = Image.open(self.__ugc_params.avatar_path)
        cache.background.putalpha(255)
    
        cache.background = cache.background.filter(ImageFilter.GaussianBlur(10))
        cache.background = cache.background.resize((self.__ugc_params.height, self.__ugc_params.height))
        
        
        cache.avatar = self.__make_corners(avatar, 40)


        self.__logger("forming duration")

        duration = math.ceil(self.__generator_params.waveform_generator.duration())

        total_frames_count = duration * self.__ugc_params.framerate


        cache.max_digits =  int(math.log10(total_frames_count))+1
        cache.intensities = self.__generator_params.waveform_generator.process(self.__ugc_params.smooth)

        Parallel(n_jobs=self.__generator_params.jobs, verbose=0 if not self.__verbose else total_frames_count)(
            delayed(self.generator)(cache, i) for i in range (total_frames_count))

        


class FrameGeneratorLoader:
    def load(generator_params: FrameGeneratorParams, 
        ugc_params: UGCParams, verbose: bool) -> FrameGenerator:

        return FrameGenerator(generator_params, ugc_params, verbose)
        



