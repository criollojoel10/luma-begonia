# luma-begonia — Luma on the Xiaomi Redmi Note 8 Pro (`begonia`, MT6785)

Work-in-progress port following Luma's own guide (<https://simplyluma.com/download/mobile/generic>):

> Every phone runs the same OS. A port adds two things to it: the **Luma ARM image** (one file for every phone)
> and a **boot image** for your phone — kernel, device tree and an initramfs with Luma's boot resolver — plus a
> **device package** that Luma adds on first start.

## The honest status

| part | state |
|---|---|
| Luma ARM image | exists: `luma-nightly-20261115.2-aarch64-disk.sparse` (CI downloads and verifies it) |
| boot image | CI builds one from the **vendor** MT6785 kernel (`AgentFabulous/begonia`, Linux 4.14.218). This is *not* what Luma asks for: Luma wants a mainline-based kernel per SoC family, and **no mainline `mt6785` exists** (zero `mt6785*` files in `torvalds/linux` and in `denialwm/linux-perpetua`) |
| device package | not started (`devices/xiaomi/begonia/` would hold `device.toml`, `boot.toml`, `firmware.manifest`, `INSTALL.md`, `tests`) |

So this repository is the **bring-up half** of a port: it proves the image, the kernel build and the boot image
packing bits, and it will not produce a daily-driver phone until a mainline `mt6785` tree exists.

## What the CI does (`.github/workflows/bootimg.yml`)

1. checks out the vendor kernel tree at a pinned commit and builds `Image.gz` with `CONFIG_FUSE_FS=y`
   (Luma's requirement for the boot resolver);
2. downloads the Luma ARM disk image and checks its published sha256;
3. packs `boot.img` with the values this phone's bootloader uses (`header v2`, page 2048, base `0x40078000`,
   kernel `0x00008000`, ramdisk `0x07c08000`, tags `0x0bc08000`);
4. uploads `boot.img`, the kernel and the checksum as artifacts.

A workflow run is proof of the chain, not of booting: the phone is not touched by CI.

## Flashing (only after reading `docs/INSTALL.md`)

The phone is A-only (no slots) and its factory images exist (`V12.5.8.0.RGGMIXM`), which is the way back:

```sh
fastboot flash boot boot.img      # boot image from the workflow
# the Luma ARM image goes to userdata, never to system/vendor
```

## Layout

```
.github/workflows/bootimg.yml   the bring-up CI
docs/INSTALL.md                 prerequisites, recovery, what not to do
docs/PORT.md                    the three parts, what is missing, upstream path
devices/xiaomi/begonia/         placeholders for device.toml / boot.toml / INSTALL.md
```

## Licence

MIT for what is written here. The kernel is the vendor's (GPL-2.0), Luma's own files keep their licences.
