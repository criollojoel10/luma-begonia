#!/usr/bin/env python3
"""Pack a begonia boot image (header v2, page 2048) and print what the header says."""
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MKBOOTIMG = os.path.join(HERE, "mkbootimg.py")

# Read from this phone's own aboot.img header (v2, page 2048): kernel 0x40080000, ramdisk 0x47c80000.
OFFSETS = {
    "--base": "0x40000000",
    "--kernel_offset": "0x00080000",
    "--ramdisk_offset": "0x07c80000",
    "--second_offset": "0x00f00000",
    "--tags_offset": "0x0bc80000",
}


def main(argv: list[str]) -> int:
    kernel = argv[1] if len(argv) > 1 else "out/Image.gz"
    ramdisk = argv[2] if len(argv) > 2 else "out/initramfs.cpio.gz"
    out = argv[3] if len(argv) > 3 else "out/boot.img"
    cmdline = argv[4] if len(argv) > 4 else ""
    dtb = argv[5] if len(argv) > 5 else "out/begonia.dtb"
    cmd = [sys.executable, MKBOOTIMG, "--kernel", kernel, "--ramdisk", ramdisk, "--dtb", dtb]
    if cmdline:
        cmd += ["--cmdline", cmdline]
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
