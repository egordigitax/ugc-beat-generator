import argparse
import sys

import numpy as np
from histos import Histos
from packer import Packer


def initArgParse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        description="Process raw amplitudes to packed-float32 histos"
    )

    required_named = parser.add_argument_group("required named arguments")

    required_named.add_argument("-i", "--input", help="set ups raw amplitudes file path",
                                type=str, required=True)

    required_named.add_argument("-o", "--output",
                                help="resulting packed-float32 histos file path",
                                type=str, required=True)

    parser.add_argument("-c", "--count",
                        help="histos count",
                        type=int, default=90, required=False)

    parser.add_argument(
        "--version", action="version",
        version=f"{parser.prog} version 1.0.0"
    )
    return parser


def main() -> None:
    parser = initArgParse()
    args = parser.parse_args()

    try:
        raw_intensities = np.load(args.input, allow_pickle=True)

        histos = Histos(args.count).process(raw_intensities)
        bytes = Packer().pack(histos)

        with open(args.output, "wb") as handle:
            handle.write(bytes)


    except Exception as err:
        print(err, file=sys.stderr)


if __name__ == "__main__":
    main()
