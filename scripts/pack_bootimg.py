#!/usr/bin/env python3
"""Pack a begonia boot image (header v2, page 2048) and print what the header says."""
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MKBOOTIMG = os.path.join(HERE, "mkbootimg.py")

OFFSETS = {
    "--base": "0x40078000",
    "--kernel_offset": "0x00008000",
    "--ramdisk_offset": "0x07c08000",
    "--second_offset": "0x00f00000",
    "--tags_offset": "0x0bc08000",
}


def main(argv: list[str]) -> int:
    kernel = argv[1] if len(argv) > 1 else "out/Image.gz"
    ramdisk = argv[2] if len(argv) > 2 else "out/initramfs.cpio.gz"
    out = argv[3] if len(argv) > 3 else "out/boot.img"
    cmd = [sys.executable, MKBOOTIMG, "--kernel", kernel, "--ramdisk", ramdisk]
    for key, value in OFFSETS.items():
        cmd += [key, value]
    cmd += ["--pagesize", "2048", "--header_version", "2", "-o", out]
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    raw = open(out, "rb").read(4096)
    ksize = struct.unpack("<I", raw[8:12])[0]
    page = struct.unpack("<I", raw[36:40])[0]
    print(f"{out}: kernel {ksize} B, page {page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
