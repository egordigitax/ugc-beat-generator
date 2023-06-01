from typing import List
import librosa
import numpy as np
from scipy.signal import hilbert, chirp


class WaveformGeneratorInterface:
    def process(self, smooth_factor: int) -> np.ndarray:
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

    def process(self, smooth_factor: int) -> np.ndarray:
        self.__logger("percussive extraction")
        percussive = librosa.effects.percussive(self.__y)

        self.__logger("normalization")
        normalized = (percussive - np.min(percussive)) / (np.max(percussive) - np.min(percussive))

        self.__logger("making curve")
        curved = np.abs(hilbert(normalized))

        self.__logger("smoothing")
        kernel_size = int(float(self.__sr) / float(smooth_factor))
        kernel = np.ones(kernel_size) / kernel_size

        kernel_offset = int(kernel_size / 2)
        padded = np.concatenate((curved[0:kernel_offset], curved, curved[-kernel_offset:-1]))

        smoothed = np.convolve(padded, kernel, mode='valid')

        self.__logger("removing artifacts")
        smoothed[0:2000] = smoothed[2000:4000]
        smoothed[-2001:-1] = smoothed[-4000:-2000]

        return smoothed

    def duration(self) -> float:
        self.__logger("get duration")

        return librosa.get_duration(y=self.__y, sr=self.__sr)

    def sample_rate(self) -> int:
        return self.__sr


class FakeWaveformGenerator(WaveformGeneratorInterface):
    def __init__(self, verbose: bool = False) -> None:
        self.__verbose = verbose

    def __logger(self, msg: str):
        if self.__verbose:
            print(msg)

    def process(self, smooth_factor: int) -> np.ndarray:
        return np.array([0.0, 1.0])

    def duration(self) -> float:
        return 2.0 / 30

    def sample_rate(self) -> int:
        return 2


class WaveformLoader:
    def load(beat_path: str, verbose: bool) -> WaveformGenerator:
        y, sr = librosa.load(beat_path)
        return WaveformGenerator(y, sr, verbose)

    def load_demo(verbose: bool) -> WaveformGenerator:
        return FakeWaveformGenerator(verbose)
