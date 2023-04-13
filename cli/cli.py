import argparse
from waveforms import WaveformGenerator, WaveformLoader
import numpy as np
import sys
from frames import FrameGeneratorParams, UGCParams, FrameGeneratorLoader, FrameGenerator

def initArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        description="Forms waveforms in STDIN for futher processing in generative UGC content."
    )


    required_named = parser.add_argument_group("required named arguments")
    experimental = parser.add_argument_group("experimental arguments (caution, fixed layout)")


    required_named.add_argument("-b", "--beat", help="set ups beat path (.wav)", type=str, required=True)

    required_named.add_argument("--shade_path", 
        help="path to shade image (alpha, .png)",
        type=str, default="Shadow.png", required=False)

    required_named.add_argument("-o", "--output_path", 
        help="path to resulting frames path",
        type=str, required=True)

    required_named.add_argument("-a", "--avatar_path", 
        help="path to avatar (.png)",
        type=str, required=True)

    experimental.add_argument("--avatar_size", 
        help="avatar new size",
        type=int, default=400, required=False)

    parser.add_argument("-f", "--framerate", 
        help="target framerate",
        type=int, default=30, required=False)

    parser.add_argument("-j", "--jobs", 
        help="number of parallel jobs",
        type=int, default=8, required=False)

    experimental.add_argument("--width", 
        help="target width",
        type=int, default=720, required=False)
    
    experimental.add_argument("--height", 
        help="target height",
        type=int, default=1280, required=False)


    parser.add_argument("-s", "--smooth", 
        help="set smooth factor by int value\nthe less -- the smoother",
        default=8, type=int, required=False)


   
   
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
        waveform_generator = WaveformLoader.load(args.beat, args.verbose)
        generator_params = FrameGeneratorParams(
            args.shade_path, args.output_path, waveform_generator, args.jobs)

        ugc_params = UGCParams(args.avatar_path, 
            args.avatar_size, args.framerate, args.width, args.height, args.smooth)
        
        FrameGeneratorLoader.load(generator_params, ugc_params, args.verbose).process()

    except Exception as err:
        print(err, file=sys.stderr)


if __name__ == "__main__":
    main()