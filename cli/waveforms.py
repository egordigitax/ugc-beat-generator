from typing import List
import librosa
import numpy as np
from scipy.signal import hilbert
from dataclasses import dataclass


@dataclass
class WaveformGeneratorParams:
    smooth_factor: int
    widening_factor: float
    percussive_influence: float
    harmonic_influence: float
    percussive_margin: float
    harmonic_margin: float



class WaveformGeneratorInterface:
    def process(self, params: WaveformGeneratorParams) -> np.ndarray:
        pass

    def duration(self) -> float:
        pass

    def sample_rate(self) -> int:
        pass



class WaveformGenerator(WaveformGeneratorInterface):
    def __init__(self, y: List[float], sr: int, verbose: bool = False) -> None:
        self.__y = y
        self.__sr = sr
        self.__verbose = verbose

    def __logger(self, msg: str):
        if self.__verbose:
            print(msg)

    def process(self, params: WaveformGeneratorParams) -> np.ndarray:
        self.__logger("percussive extraction")
        harmonic, percussive = librosa.effects.hpss(self.__y, margin=(params.harmonic_margin, params.percussive_margin))
        percussive = percussive * params.percussive_influence + harmonic * params.harmonic_influence

        self.__logger("normalization")
        normalized = np.abs(percussive)


        self.__logger("smoothing")
        kernel_size = int(float(self.__sr) / float(params.smooth_factor))
        kernel = np.ones(kernel_size) / kernel_size

        kernel_offset = int(kernel_size / 2)
        padded = np.concatenate((normalized[0:kernel_offset], normalized, normalized[-kernel_offset:-1]))

        smoothed = np.convolve(padded, kernel, mode='valid')

        self.__logger("normalization 2")
        normalized_again = params.widening_factor * ((smoothed - np.min(smoothed)) / (np.max(smoothed) - np.min(smoothed)))

        return normalized_again

    def duration(self) -> float:
        self.__logger("get duration")

        return librosa.get_duration(y=self.__y, sr=self.__sr)

    def sample_rate(self) -> int:
        return self.__sr


class DemoWaveformGenerator(WaveformGeneratorInterface):
    def __init__(self, verbose: bool = False) -> None:
        self.__verbose = verbose

    def __logger(self, msg: str):
        if self.__verbose:
            print(msg)

    def process(self, params: WaveformGeneratorParams) -> np.ndarray:
        return np.array([0.0, 1.0])

    def duration(self) -> float:
        return 2.0 / 30

    def sample_rate(self) -> int:
        return 2

    class DemoWaveformGenerator(WaveformGeneratorInterface):
        def __init__(self, verbose: bool = False) -> None:
            self.__verbose = verbose

        def __logger(self, msg: str):
            if self.__verbose:
                print(msg)

        def process(self, params: WaveformGeneratorParams) -> np.ndarray:
            return np.array([0.0, 1.0])

        def duration(self) -> float:
            return 2.0 / 30

        def sample_rate(self) -> int:
            return 2



class WaveformLoader:

    @staticmethod
    def load(beat_path: str, verbose: bool) -> WaveformGeneratorInterface:
        y, sr = librosa.load(beat_path)
        return WaveformGenerator(y, int(sr), verbose)

    @staticmethod
    def load_demo(verbose: bool) -> WaveformGeneratorInterface:
        return DemoWaveformGenerator(verbose)
