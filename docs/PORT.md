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
