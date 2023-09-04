import inspect
import os
import sys
from pathlib import Path
from typing import Union, Optional, Callable

from .abstract import BaseEngine, RenderEngine
from .enums import DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_ENGINE, DEFAULT_DEVICE, DEFAULT_TEMP_PATH


class BlenderEngine(BaseEngine):
    """
    BlenderEngine module made for Blender version 3.5.
    """

    def __init__(self, engine_path):
        super().__init__(engine_path)

        if not os.path.exists(DEFAULT_TEMP_PATH):
            with open(DEFAULT_TEMP_PATH, 'w') as file:
                file.write('')

        self._current_path = Path(__file__)
        self._work_path = Path(os.path.abspath(sys._getframe(0).f_back.f_code.co_filename))

    def render(self,
               project_file: Union[Path, str],
               output: Union[Path, str],
               frames: Union[int, range],
               width: Optional[int] = DEFAULT_WIDTH,
               height: Optional[int] = DEFAULT_HEIGHT,
               script: Optional[Callable] = None,
               render_engine: Optional[RenderEngine] = DEFAULT_ENGINE,
               render_device: Optional[bool] = DEFAULT_DEVICE,
               params: Optional[str] = ''
               ):
        """
        Use project file as main scene.
        Pass int in frames for render image, or range for render animation.
        """

        _frames_param = self._get_frames_argv(frames)

        if script is None:
            os.system(f'{str(self.engine_path)} -b {str(project_file)} -E {render_engine} '
                      f'-o {str(Path(output) / "#")} {_frames_param} {params} -- --cycles-device {render_device}')
        else:
            os.system(f'{str(self.engine_path)} -b {str(project_file)} -E {render_engine} '
                      f'--python {str(self._create_temp_code_file(script))} '
                      f'-o {str(Path(output) / "#")} {_frames_param} {params} -- --cycles-device {render_device}')

        self._remove_temp_file()

    def _create_temp_code_file(self, func: Callable) -> Path:
        with open(DEFAULT_TEMP_PATH, 'w') as file:
            file.write(self._func_to_code(func))
        return Path(DEFAULT_TEMP_PATH).absolute()

    def _func_to_code(self, func: Callable) -> str:
        INDENTS = 4

        lines = inspect.getsource(func)
        lines = ':'.join(lines.split(':')[1:])
        lines_arr = lines.split('\n')
        lines_with_normalized_indent = [line[INDENTS:] for line in lines_arr]
        lines_without_first_line_arr = lines_with_normalized_indent[1:]

        imports = f'import bpy\n' \
                  f'import sys\n' \
                  f'sys.path.append("{self._work_path.drive}")\n\n'

        source_code = imports + '\n'.join(lines_without_first_line_arr)

        return source_code

    @staticmethod
    def _get_frames_argv(frames):
        if isinstance(frames, int):
            return f'-f {str(frames)}'
        elif isinstance(frames, range):
            return f'-s {frames.start} -e {frames.stop} -a'
        else:
            raise ValueError('Frames argument needs to be int or range')

    @staticmethod
    def _remove_temp_file():
        os.remove(DEFAULT_TEMP_PATH)
