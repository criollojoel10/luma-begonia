# Port notes: begonia (MT6785) on Luma

Taken from Luma's guide, minus the optimism.

## The three parts

1. **Luma ARM image** — one file for every phone (`luma-nightly-<date>-aarch64-disk.sparse`). CI verifies its
   published sha256 and never modifies it.
2. **Boot image** — kernel + device tree + an initramfs that carries Luma's boot resolver.
3. **Device package** — kernel modules, firmware (from the phone's own partitions or the vendor factory image;
   never mixed in from elsewhere) and services, installed by Luma on first start.

## Blocker, stated plainly

Luma asks for "a mainline-based work for the phone's SoC and a source device tree, rebased onto the one Luma
kernel". For MT6785 **there is no mainline tree**: `torvalds/linux` has no `mt6785*` file, and neither does
`denialwm/linux-perpetua`. What exists is the vendor 4.14 tree (`AgentFabulous/begonia`, pinned in the
workflow) and Kupfer's 4.19/6.x vendor-derived tree.

Therefore:

- The CI builds a boot image from the vendor tree with `CONFIG_FUSE_FS=y`. That proves the toolchain, the
  offsets and the image format; it does not prove a Luma boot.
- The Luma ARM image goes to **userdata**; the phone has no A/B slots, so a bad boot image means fastboot, not
  "the other slot".
- Bringing `mt6785` to mainline (clock, pinctrl, MDSS/DSI, UFS, PMIC, panfrost for the Mali-G76) is the real
  prerequisite. Until then this stays a bring-up repository.

## What is already known about this phone (measured, not guessed)

- Vendor kernel tree boots with `klog` label 7.1.0; `mediatek-drm` drives `card1` (`DSI-1`, 1080×2340@60) and
  **panfrost binds `13040000.gpu`** (Mali-G76) with Mesa 26.2.6 — so a Wayland session on the vendor kernel is
  plausible even without mainline.
- WiFi is MediaTek `wlan_gen4m` + `wmt_drv`; the same drivers Luma's device package would need to ship.
- The bootloader accepts recovery zips only (the vendor's own format); the factory image is the way back.

## Bring-up boot image from the phone's own kernel (2026-11-16)

Instead of the 4.14 vendor GitHub tree (which fights gcc 14), the boot image was packed from the kernel that
already runs on this phone:

| input | source | size |
|---|---|---|
| `Image.gz` | `/boot/Image.gz` on the phone | 17 069 246 B |
| initramfs | `/boot/initramfs-linux.img` (Kupfer's, finds a `kupfer_root` label) | 17 129 587 B |
| DTB | `/boot/dtbs/mediatek/mt6785-xiaomi-begonia-tianma.dtb` | 62 K |

Packed with `scripts/mkbootimg.py` and the offsets read from the phone's own `aboot.img`
(`base 0x40000000`, kernel `0x40080000`, ramdisk `0x47c80000`, page 2048, header v2):

```
magic b'ANDROID!' kernel 17069246 0x40080000 ramdisk 17129587 0x47c80000 page 2048 ver 2
```

Artifact: `out/luma-begonia-bringup-boot.img` (33 MB), published as a release asset. This image boots the
kernel this phone already runs and drops into Kupfer's initramfs: it proves the packing and is the base on
which Luma's dracut initramfs gets substituted once the device package exists.

## v0.2 — why v0.1 bootlooped on the phone

The v0.1 image was packed with an empty cmdline. Kupfer's initramfs needs the *`kupfer`* argument to load its
early modules (panel, touch, regulators) and find the rootfs; without it the kernel never reaches the root and
the phone reboots in a loop.

`out/luma-begonia-bringup-boot-v0.2.img` (33 MB) carries the cmdline copied from the phone's own `aboot.img`:

```
kupfer earlymodules=lm36274_bl,lm363x-regulator,novatek-nvt-ts-spi,panel-novatek-nt36672a,ti-lmu console=tty0 bootopt=64S3,32N2,64N2
```

Header: kernel 17 069 246 B, page 2048, v2, offsets `0x40000000/0x00080000/0x07c80000` (from `aboot.img`).
Recovery on the phone: `fastboot flash boot aboot-kupfer-backup.img` (34 269 184 B, sha256
`952aa85094f019abab64de0e26a6595fb75608ba7a52e67d0e2aea56a12dc1c4`, also kept at
`/home/joel/aboot-kupfer-backup.img` on the device).
