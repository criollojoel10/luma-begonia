# devices/xiaomi/begonia

Placeholders for the device package Luma would install on first start:

| file | content |
|---|---|
| `device.toml` | vendor, codename, SoC, panel, touch, GPU, modem |
| `boot.toml` | the boot image recipe (kernel source, defconfig, offsets) |
| `firmware.manifest` | every firmware file, where it comes from and its sha256 |
| `INSTALL.md` | the phone-specific install and recovery steps |

Not written yet: the port is at the bring-up stage (`docs/PORT.md`).
