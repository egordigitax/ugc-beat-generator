import argparse
from waveforms import WaveformGenerator, WaveformLoader
import numpy as np
import sys

def initArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Forms waveforms in STDIN for futher processing in generative UGC content."
    )

    parser.add_argument("-b", "--beat", help="set ups beat path (.wav)", type=str)
    parser.add_argument("-s", "--smooth", 
        help="set smooth factor by int value\nthe less -- the smoother",
        default=8, type=int, required=False)
    parser.add_argument("-p", "--precision", 
        help="set output float precision", 
        default=2, type=int, required=False)

    parser.add_argument("-d", "--delimiter",
        help="delimiter symbol",
        default=",", type=str, required=False
    )

    parser.add_argument("-v", "--verbose", 
        help="verbose computations", action='store_true', required=False)


    parser.add_argument(
        "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )

    return parser

def main() -> None:
    parser = initArgParse()
    args = parser.parse_args()

    try:
        waveformGenerator = WaveformLoader.load(args.beat, args.verbose)
        result = waveformGenerator.process(args.smooth)

        print(result.shape[0], 
            file=sys.stdout)
        print(args.delimiter.join(map(lambda x: "{}".format(round(x, args.precision)), result)),
            file=sys.stderr)
    except Exception as err:
        print(err, file=sys.stderr)


if __name__ == "__main__":
    main()