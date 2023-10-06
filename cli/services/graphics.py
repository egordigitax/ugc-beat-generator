import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
from natsort import natsorted
from PIL import Image, ImageDraw, ImageFont, ImageFilter

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '..'))

from .engine.blender import BlenderEngine
from settings import BLENDER_PATH, SCENE_SOURCE, PROJECT_FILE, SCENE_OUTPUT, USER_SOURCE, USER_OUTPUT, OVERLAY_SOURCE, \
    OVERLAY_OUTPUT, AVATAR_STORE, AVATAR_BLUR, USER_INFO_IMG, USER_INFO_FONT


@dataclass
class GraphicsGeneratorParams:
    scene_template_id: int
    user_info_template_id: int
    overlay_template_id: int
    disable_intro: bool


class GraphicsGeneratorInterface:
    def __init__(self):
        pass

    def render(self):
        pass


class GraphicsGenerator:
    def __init__(self, verbose: bool):
        self.verbose = verbose
        self.blender = BlenderEngine(BLENDER_PATH)

    def __logger(self, msg):
        if self.verbose:
            print(msg)

    def process_scene_frames(self, scene_template_id, width, height) -> List[Path]:

        if not os.path.exists(f"{SCENE_SOURCE}/{scene_template_id}/{PROJECT_FILE}"):
            natsort_files = natsorted(os.listdir(SCENE_SOURCE))
            return [Path(f'{SCENE_SOURCE}/{file}') for file in natsort_files if file.endswith(".png")]

        # если не находит .blend файл в папке темлейта, то импортирует как png sequence

        self.blender.render(f"{SCENE_SOURCE}/{scene_template_id}/{PROJECT_FILE}",
                            SCENE_OUTPUT, range(0, 90), width, height)

        natsort_files = natsorted(os.listdir(SCENE_OUTPUT))
        return [Path(f'{SCENE_OUTPUT}/{file}') for file in natsort_files if file.endswith(".png")]

    def process_user_info_frames(self, user_info_template_id, width, height) -> List[Path]:

        if not os.path.exists(f"{USER_SOURCE}/{user_info_template_id}/{PROJECT_FILE}"):
            natsort_files = natsorted(os.listdir(USER_SOURCE))
            return [Path(f'{USER_SOURCE}/{file}') for file in natsort_files if file.endswith(".png")]

        # если не находит .blend файл в папке темлейта, то импортирует как png sequence

        self.blender.render(f"{USER_SOURCE}/{user_info_template_id}/{PROJECT_FILE}",
                            USER_OUTPUT, range(0, 105), width, height)

        natsort_files = natsorted(os.listdir(USER_OUTPUT))
        return [Path(f'{USER_OUTPUT}/{file}') for file in natsort_files if file.endswith(".png")]

    def process_overlay_frames(self, overlay_template_id, width, height) -> List[Path]:

        if not os.path.exists(f"{OVERLAY_SOURCE}/{overlay_template_id}/{PROJECT_FILE}"):
            natsort_files = natsorted(os.listdir(OVERLAY_SOURCE))
            return [Path(f'{OVERLAY_SOURCE}/{file}') for file in natsort_files if file.endswith(".png")]

        # если не находит .blend файл в папке темлейта, то импортирует как png sequence

        self.blender.render(f"{OVERLAY_SOURCE}/{overlay_template_id}/{PROJECT_FILE}",
                            OVERLAY_OUTPUT, range(0, 30), width, height)
        natsort_files = natsorted(os.listdir(OVERLAY_OUTPUT))
        return [Path(f'{OVERLAY_OUTPUT}/{file}') for file in natsort_files if file.endswith(".png")]

    def save_avatar(self, avatar_path):
        img = Image.open(avatar_path)
        img_blur = img.filter(ImageFilter.GaussianBlur(50))
        img.save(AVATAR_STORE)
        img_blur.save(AVATAR_BLUR)

    @staticmethod
    def save_user_info_png(username, track_name):
        # сборка текстуры для user-info сцены

        def draw_text(ctx, y_offset, text, font, color):
            _, _, w, h = ctx.textbbox((0, 0), text, font=font)
            ctx.text(((width - w) / 2, (height - h) / 2 + y_offset), text, font=font, fill=color)

        width = 1000
        height = 500
        canvas = Image.new("RGBA", (width, height), "#ffffff")

        _username = username if len(username) < 20 else username[:16]+"..."
        _track_name = track_name if len(track_name) < 20 else track_name[:16]+"..."

        main_font_size = 125 if len(username) < 7 else 90

        canvas_draw = ImageDraw.Draw(canvas)
        main_font = ImageFont.truetype(USER_INFO_FONT, main_font_size)
        secondary_font = ImageFont.truetype(USER_INFO_FONT, 65)

        draw_text(canvas_draw, -75, _username, main_font, (0,0,0))
        draw_text(canvas_draw, 25, _track_name, secondary_font, (0,0,0))

        canvas.save(USER_INFO_IMG)

class GraphicsGeneratorLoader:
    @staticmethod
    def load(verbose: bool):
        return GraphicsGenerator(verbose)
