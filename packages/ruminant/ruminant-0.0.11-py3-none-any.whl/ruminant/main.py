from . import modules
from .buf import Buf
import argparse
import sys
import json
import tempfile
import os
import re


def process(file, walk):
    if not walk:
        return json.dumps(modules.chew(file), indent=2, ensure_ascii=False)
        return

    buf = Buf(file)
    unknown = 0

    data = []
    while buf.available():
        entry = None

        with buf:
            try:
                entry = modules.chew(file, True)
                assert entry["type"] != "unknown"
            except Exception:
                entry = None

        if entry is not None:
            if unknown > 0:
                data.append({
                    "type": "unknown",
                    "length": unknown,
                    "offset": buf.tell() - unknown,
                    "blob-id": modules.blob_id
                })
                modules.blob_id += 1
                unknown = 0

            data.append(entry)
            buf.skip(entry["length"])
        else:
            unknown += 1
            buf.skip(1)

    if unknown > 0:
        data.append({
            "type": "unknown",
            "length": unknown,
            "offset": buf.tell() - unknown,
            "blob-id": modules.blob_id
        })

    for entry in data:
        for k, v in modules.to_extract:
            if k == entry["blob-id"]:
                buf.seek(entry["offset"])
                with open(v, "wb") as file:
                    length = entry["length"]

                    while length:
                        blob = buf.read(min(1 << 24, length))
                        file.write(blob)
                        length -= len(blob)

    return json.dumps({
        "type": "walk",
        "length": buf.size(),
        "entries": data
    },
                      indent=2,
                      ensure_ascii=False)


def main():
    if sys.platform == "linux":
        import traceback
        import signal

        def print_stacktrace(sig, frame):
            print("Current stacktrace:\n" +
                  "".join(traceback.format_stack(frame)),
                  file=sys.stderr)

        signal.signal(signal.SIGUSR1, print_stacktrace)

    parser = argparse.ArgumentParser(description="Ruminant parser")

    parser.add_argument("file",
                        default="-",
                        nargs="?",
                        help="File to parse (default: -)")

    parser.add_argument(
        "--extract",
        "-e",
        nargs=2,
        metavar=("ID", "FILE"),
        action="append",
        help="Extract blob with given ID to FILE (can be repeated)")

    parser.add_argument(
        "--walk",
        "-w",
        action="store_true",
        help="Walk the file binwalk-style and look for parsable data")

    parser.add_argument("--extract-all",
                        action="store_true",
                        help="Extract all blobs to blobs/{id}.bin")

    parser.add_argument("--filename-regex",
                        default=".*",
                        nargs="?",
                        help="Filename regex for directory mode")

    args = parser.parse_args()

    if args.file == "-":
        args.file = "/dev/stdin"

    if args.extract_all:
        modules.extract_all = True
        if not os.path.isdir("blobs"):
            os.mkdir("blobs")

    if args.extract is not None:
        for k, v in args.extract:
            try:
                modules.to_extract.append((int(k), v))
            except ValueError:
                print(f"Cannot parse blob ID {k}", file=sys.stderr)
                exit(1)

    if args.file == "/dev/stdin":
        file = tempfile.TemporaryFile()

        try:
            fd = open("/dev/stdin", "rb")
        except Exception:
            fd = open(sys.stdin.fileno(), "rb", closefd=False)

        with fd:
            while True:
                blob = fd.read(1 << 24)
                if len(blob) == 0:
                    break

                file.write(blob)

        file.seek(0)
        with file:
            print(process(file, args.walk))
    else:
        if not os.path.isfile(args.file):
            print("{\n  \"type\": \"directory\",\n  \"files\": [")

            filename_regex = re.compile(args.filename_regex)

            first = True
            for root, _, files in os.walk(args.file):
                for file in files:
                    file = os.path.join(root, file)

                    if filename_regex.match(file) is None:
                        continue

                    try:
                        with open(file, "rb") as fd:
                            if first:
                                first = False
                            else:
                                print(",")

                            print(
                                f"    {{\n      \"path\": {json.dumps(file)},\n      \"data\": {{"  # noqa: E501
                            )

                            print("\n".join([
                                "      " + x for x in process(
                                    fd, args.walk).split("\n")[1:-1]
                            ]))

                            print("      }\n    }", end="")
                    except Exception:
                        pass

            print("\n  ]\n}")
        else:
            with open(args.file, "rb") as file:
                print(process(file, args.walk))
