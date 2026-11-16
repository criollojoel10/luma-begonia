# Install / recover

## Never

- never write the Luma ARM **ISO** to a phone (the guide says it twice: it is the laptop installer);
- never repartition, relock the bootloader, write `vbmeta`, or touch modem storage;
- never flash a boot image you have not built and read the header of.

## Before

- bootloader unlocked, `fastboot` (this phone's bootloader works with platform-tools 30.x);
- factory images at hand (`begonia` `V12.5.8.0.RGGMIXM`, Android 11 base) and their hashes;
- the Luma sparse image + its published sha256 (`docs/PORT.md`).

## Order

```sh
# 1. Luma ARM image to userdata (sparse image, never to system/vendor)
fastboot flash userdata luma.sparse

# 2. the boot image built by .github/workflows/bootimg.yml
fastboot flash boot boot.img
fastboot reboot
```

If it does not boot: back to fastboot (power + volume-down), restore the vendor `boot.img` from the factory
image, then `fastboot reboot`. There is no second slot.
