from abc import ABC, abstractmethod
from pathlib import Path
from typing import NewType, Optional, Callable, Union

RenderEngine = NewType('RenderEngine', str)
RenderDevice = NewType('RenderDevice', str)


class BaseEngine(ABC):

    def __init__(self, engine_path: Union[Path, str]):
        super().__init__()
        self.engine_path = str(engine_path)

    @abstractmethod
    def render(self,
               project_file: Union[Path, str],
               output: Union[Path, str],
               frames: Union[int, range],
               width: Optional[int],
               height: Optional[int],
               script: Optional[Callable],
               render_engine: Optional[RenderEngine],
               render_device: Optional[RenderDevice],
               params: Optional[str]
               ):
        raise NotImplemented