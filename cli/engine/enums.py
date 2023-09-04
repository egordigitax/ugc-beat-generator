import os.path

from .abstract import RenderEngine, RenderDevice

DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 1000

DEFAULT_ENGINE = RenderEngine('CYCLES')
DEFAULT_DEVICE = RenderDevice('CUDA')

DEFAULT_TEMP_PATH = '.temp'


