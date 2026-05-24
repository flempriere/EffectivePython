# cli.py

import adjust
import enhance
import parser


def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        enhance.do_enhance(args.file, args.amount)
    elif args.command == "adjust":
        adjust.do_adjust(args.file, args.brightness, args.contrast)
    else:
        raise RuntimeError("Not reachable!")


if __name__ == "__main__":
    main()
