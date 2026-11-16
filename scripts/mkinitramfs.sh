#!/bin/sh
# Bring-up initramfs: proves the kernel/initramfs pair boots and reports what it sees.
# Luma's own boot resolver replaces this once the device package exists.
set -e
root=out/initramfs-root
rm -rf "$root"
mkdir -p "$root/bin" "$root/dev" "$root/proc" "$root/sys" "$root/newroot"
cat > "$root/init" <<'INIT'
#!/bin/sh
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
printf 'luma-begonia bring-up: kernel is up\n'
cat /proc/version
for p in /dev/block/by-name/userdata /dev/block/platform/bootdevice/by-name/userdata; do
  [ -e "$p" ] && printf 'userdata: %s\n' "$p"
done
printf 'modules: '; ls /lib/modules 2>/dev/null || printf 'none in initramfs\n'
exec sh
INIT
chmod +x "$root/init"
( cd "$root" && find . | cpio -o -H newc 2>/dev/null | gzip -9 ) > out/initramfs.cpio.gz
ls -l out/initramfs.cpio.gz
