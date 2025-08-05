# -*- coding: utf-8 -*-
# ssfz2json.py

import argparse
import json
import sys
from pathlib import Path

from jupyter_analysis_tools.readdata import readSSFZ


def main():
    parser = argparse.ArgumentParser(
        description="""
            Reads and parses a .SSFZ file created by Anton Paar SAXSquant software and writes them
            back to disk as .JSON file under the same base name if no other output name was given.

            If two .SSFZ files are provided, a diff-like comparison of metadata is output and the
            *outPath* argument is ignored.
            """
    )
    parser.add_argument(
        "-i",
        "--inPath",
        type=lambda p: Path(p).absolute(),
        help="Path of the input .SSFZ file to read.",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--comparePath",
        type=lambda p: Path(p).absolute(),
        help="Path of a 2nd .SSFZ file to compare its metadata against the 1st one.",
    )
    parser.add_argument(
        "-o",
        "--outPath",
        type=lambda p: Path(p).absolute(),
        help="Output file Path to write the JSON data to.",
    )
    json_args = dict(sort_keys=True, indent=2)
    args = parser.parse_args()
    if not args.inPath.is_file():
        print(f"Provided file '{args.inPath}' not found!")
        return 1
    in_data = readSSFZ(args.inPath)
    if args.comparePath is not None:
        import difflib

        comp_data = readSSFZ(args.comparePath)
        diff = difflib.unified_diff(
            json.dumps(in_data, **json_args).splitlines(keepends=True),
            json.dumps(comp_data, **json_args).splitlines(keepends=True),
            fromfile=str(args.inPath),
            tofile=str(args.comparePath),
        )
        for line in diff:
            print(line, end="")
    else:  # just write JSON to outPath
        if args.outPath is None:
            args.outPath = args.inPath.with_suffix(args.inPath.suffix + ".json")
        with open(args.outPath, "w") as fd:
            json.dump(in_data, fd, **json_args)
        print(f"Wrote '{args.outPath}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
