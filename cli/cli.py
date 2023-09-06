import argparse
from services.waveforms import WaveformLoader, WaveformGeneratorParams
import sys
from services.frames import FrameGeneratorParams, UGCParams, FrameGeneratorLoader


def initArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        description="Generates frames for UGC",
        add_help=False
    )

    misc = parser.add_argument_group("Misc Options")
    required = parser.add_argument_group("Required Options")
    general = parser.add_argument_group("General Options")
    graphics = parser.add_argument_group("Graphic Rendering Options")
    music_analyzer = parser.add_argument_group("Music Analyzer Options")

    # Misc Options
    def add_misc_arguments() -> None:
        misc.add_argument("-h", "--help", action="help", help="show this help message and exit")

        misc.add_argument("--version", action="version",
                          version=f"{parser.prog} version 1.3.0")

        misc.add_argument("--demo", required=False, default=False,
                          action='store_true',
                          help="for dev purposes (generates test frames or amplitudes)")

    # Required Options
    def add_required_arguments() -> None:
        required.add_argument("-b", "--beat", help="set ups beat path (.wav)", type=str, required=True)

        required.add_argument("-o", "--output_path",
                                    help="path to resulting frames path",
                                    type=str, required=True)

        required.add_argument("-a", "--avatar_path",
                                    help="path to avatar (.png)",
                                    type=str, required=True)

    # Graphics Options
    def add_graphics_arguments() -> None:
        graphics.add_argument("--width",
                              help="target width",
                              type=int, default=720, required=False)

        graphics.add_argument("--height",
                              help="target height",
                              type=int, default=1280, required=False)

        graphics.add_argument("--use-cpu", required=False, default=False,
                              action='store_true', help="use cpu computing device")

        graphics.add_argument("--samples",
                              help="set number of rendering samples. more samples - better quality",
                              required=False, default=64, type=int)

        graphics.add_argument("-t", "--template-id",
                              help="set graphics template id. uses random when not specified",
                              type=int, required=False)

        graphics.add_argument("-ot", "--overlay-template-id",
                              help="applies cyclic overlay footage to video by id, pass -1 for random",
                              type=int, required=False)

        graphics.add_argument("-f", "--framerate",
                            help="target framerate",
                            type=int, default=30, required=False)

        graphics.add_argument("--shade_path",
                            help="required in legacy mode. path to shade image (alpha, .png)",
                            type=str, default=None, required=False)

        graphics.add_argument("--blur_radius",
                                  help="blur radius (intensity)",
                                  type=int, default=50, required=False)

        graphics.add_argument("--avatar_size",
                                  help="avatar new size",
                                  type=int, default=400, required=False)

    # General Options
    def add_general_arguments() -> None:
        general.add_argument("--legacy",
                            help="uses legacy version of generator",
                            required=False, action='store_true')

        general.add_argument("-j", "--jobs",
                            help="number of parallel jobs",
                            type=int, default=8, required=False)

        general.add_argument("-v", "--verbose",
                            help="verbose computations",
                            action='store_true', required=False, default=False)

        general.add_argument("--output_type", help="select output presentation. available types: \n "
                                                  "* frames (--output_type=frames) \n"
                                                  "* raw (--output_type=raw)\n",
                            default="frames", type=str, required=False)

    # Music Analyzer Options
    def add_music_analyzer_arguments() -> None:
        music_analyzer.add_argument("-s", "--smooth",
                            help="set smooth factor by int value\nthe less -- the smoother",
                            default=8, type=int, required=False)

        music_analyzer.add_argument("-w", "--widening",
                            help="set widening factor by float value\nthe less -- the smoother",
                            default=0.5, type=float, required=False)

        music_analyzer.add_argument("--percussive_influence",
                            help="set percussive part influence (0.0 -- 1.0)\n",
                            default=0.5, type=float, required=False)

        music_analyzer.add_argument("--harmonic_influence",
                            help="set harmonic part influence (0.0 -- 1.0)\n",
                            default=0.5, type=float, required=False)

        music_analyzer.add_argument("--percussive_margin",
                            help="set percussive part isolation"
                                 "\n 1.0 -- default, more -- more isolated\n",
                            default=1.0, type=float, required=False)

        music_analyzer.add_argument("--harmonic_margin",
                            help="set harmonic part isolation"
                                 "\n 1.0 -- default, more -- more isolated\n",
                            default=1.0, type=float, required=False)

    add_misc_arguments()
    add_required_arguments()
    add_general_arguments()
    add_graphics_arguments()
    add_music_analyzer_arguments()

    return parser


def main() -> None:
    parser = initArgParse()
    args = parser.parse_args()

    try:
        if args.legacy and not args.shade_path:
            raise Exception('--shade_path required while run in --legacy mode.')

        if args.demo:
            waveform_generator = WaveformLoader.load_demo(args.verbose)
            args.framerate = 2
        else:
            waveform_generator = WaveformLoader.load(args.beat, args.verbose)

        waveform_generator_params = WaveformGeneratorParams(
            args.smooth, args.widening, args.percussive_influence, args.harmonic_influence,
            args.percussive_margin, args.harmonic_margin
        )

        if args.output_type == "frames":
            generator_params = FrameGeneratorParams(
                args.shade_path, args.output_path, waveform_generator, args.jobs)

            ugc_params = UGCParams(args.avatar_path,
                                   args.avatar_size, args.framerate, args.width,
                                   args.height, args.blur_radius, waveform_generator_params)

            FrameGeneratorLoader.load(generator_params, ugc_params, args.verbose, args.legacy).process()

        elif args.output_type == "raw":
            intensities = waveform_generator.process(waveform_generator_params)
            intensities.dump("{}/raw".format(args.output_path))
        else:
            print("unsupported --output_type mode, please read the docs", file=sys.stderr)

    except Exception as err:
        print(err, file=sys.stderr)


if __name__ == "__main__":
    main()
