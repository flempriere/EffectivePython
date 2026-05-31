# cli_faster.py
# Improves the cli load time by using lazy imports

import parser


def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        import enhance  # lazy import module

        enhance.do_enhance(args.file, args.amount)

    elif args.command == "adjust":
        import adjust  # lazy import module

        adjust.do_adjust(args.file, args.brightness, args.contrast)

    else:
        raise RuntimeError


if __name__ == "__main__":
    main()
