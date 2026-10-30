# Totem Geist USB-Dongle

## Table of Contents

- [Purpose of the Dongle](#purpose-of-the-dongle)
- [What do you have to do to use it?](#what-do-you-have-to-do-to-use-it)
  - [The big picture](#the-big-picture)
  - [Step 1 – Build the firmware from this config](#step-1--build-the-firmware-from-this-config)
  - [Step 2 – How to flash a XIAO nRF52840](#step-2--how-to-flash-a-xiao-nrf52840)
  - [Step 3 – Wipe old bonds (settings reset) on all three devices](#step-3--wipe-old-bonds-settings-reset-on-all-three-devices)
  - [Step 4 – Flash the real firmware](#step-4--flash-the-real-firmware)
  - [Step 5 – First start & pairing](#step-5--first-start--pairing)
  - [Day-to-day notes](#day-to-day-notes)
  - [ZMK Studio](#zmk-studio)
  - [Troubleshooting](#troubleshooting)
  - [Going back to "no dongle" mode](#going-back-to-no-dongle-mode)
- [Resources](#resources)

## Purpose of the Dongle

> This wireless dongle features a Seeed Studio XIAO nRF52840 and is housed in a compact, 3D-printed case.
> It includes a 20 cm braided USB-C to C cable for easy connection to your computer.
> Typically, without a dongle, the left half of a wireless split keyboard is responsible for communicating with
> both the right half and the computer, as well as processing keypresses, which leads to higher battery consumption.
> With a dongle, however, both halves connect wirelessly to it instead, offloading processing and
> communication tasks and significantly extending battery life.
> The dongle also makes switching between devices easier, as there is no need to manage multiple Bluetooth profiles
> or pair your keyboard again. Simply plug the dongle into a different device and you're ready to go!
>
> Please note that the dongle requires custom ZMK firmware for your specific keyboard setup.
> Both keyboard halves and the dongle must be configured and flashed accordingly.
> See the ZMK dongle documentation for instructions. You can find the TOTEM dongle firmware below for reference purposes.

Source: [keeb.supply – Wireless Dongle](https://keeb.supply/products/wireless-dongle)

## What do you have to do to use it?

### The big picture

| Device     | Before (no dongle)                              | After (with dongle)                          |
|------------|-------------------------------------------------|----------------------------------------------|
| Left half  | **Central**: holds keymap, talks to the PC      | **Peripheral**: only sends key presses       |
| Right half | Peripheral, connects to the left half           | Peripheral, connects to the dongle           |
| Dongle     | –                                               | **Central**: holds keymap, connected via USB |

This means **all three** XIAO nRF52840 boards have to be flashed: the dongle with the
`totem_dongle` firmware, and **both** halves with new firmware (the left half must stop being the central).
Old Bluetooth bonds must be wiped first (settings reset), otherwise the halves keep trying to reach their old partners.

You need:

- the dongle + USB-C cable, both TOTEM halves (charged)
- a USB-C cable for the halves
- the firmware files (`.uf2`) for dongle, both halves and `settings_reset`, built from this config (Step 1)

### Step 1 – Build the firmware from this config

The firmware is built from this repository, which holds the keymap and can also build the
`settings_reset` file. Current state (all paths relative to the repo root):

- pinned to ZMK `v0.3` ([`config/west.yml`](../../config/west.yml) and
  [`.github/workflows/build.yml`](../../.github/workflows/build.yml)), board `seeeduino_xiao_ble`
- [`Kconfig.defconfig`](../../config/boards/shields/totem/Kconfig.defconfig) makes `totem_left` the central
- the keymap that gets used is [`config/totem.keymap`](../../config/totem.keymap); the copy under
  `config/boards/shields/totem/` is ignored
- no physical layout, just a `zmk,matrix_transform` in [`totem.dtsi`](../../config/boards/shields/totem/totem.dtsi)

ZMK `v0.3` already supports dongles, the mock kscan and `settings_reset`, so **staying on `v0.3`** is the
smallest change. The board name and file names stay the same.
These are the changes to make in `config/boards/shields/totem/`:

1. **`Kconfig.shield`**: register the new shield:

   ```kconfig
   config SHIELD_TOTEM_DONGLE
       def_bool $(shields_list_contains,totem_dongle)
   ```

2. **`Kconfig.defconfig`**: add a block for the dongle and include it in the `ZMK_SPLIT` block.
   The existing `SHIELD_TOTEM_LEFT` block can stay as it is, because `build.yaml` overrides the left
   half's role (item 5 below). That way, going back to no dongle only means reverting `build.yaml`.

   ```kconfig
   if SHIELD_TOTEM_DONGLE

   config ZMK_KEYBOARD_NAME
       default "TOTEM"

   config ZMK_SPLIT_ROLE_CENTRAL
       default y

   endif

   if SHIELD_TOTEM_LEFT || SHIELD_TOTEM_RIGHT || SHIELD_TOTEM_DONGLE

   config ZMK_SPLIT
       default y

   endif
   ```

3. **`totem_dongle.overlay`** (new): the same matrix transform as `totem.dtsi`, but with a mock kscan
   instead of the key matrix. It doesn't include `totem.dtsi`, because that would pull in the GPIO matrix of a half.

   ```dts
   #include <dt-bindings/zmk/matrix_transform.h>

   / {
       chosen {
           zmk,kscan = &mock_kscan;
           zmk,matrix_transform = &default_transform;
       };

       default_transform: keymap_transform_0 {
           compatible = "zmk,matrix-transform";
           columns = <10>;
           rows = <4>;
           map = <
                   RC(0,0) RC(0,1) RC(0,2) RC(0,3) RC(0,4)    RC(0,5) RC(0,6) RC(0,7) RC(0,8) RC(0,9)
                   RC(1,0) RC(1,1) RC(1,2) RC(1,3) RC(1,4)    RC(1,5) RC(1,6) RC(1,7) RC(1,8) RC(1,9)
           RC(3,0) RC(2,0) RC(2,1) RC(2,2) RC(2,3) RC(2,4)    RC(2,5) RC(2,6) RC(2,7) RC(2,8) RC(2,9) RC(3,9)
                                   RC(3,2) RC(3,3) RC(3,4)    RC(3,5) RC(3,6) RC(3,7)
           >;
       };

       mock_kscan: mock_kscan_0 {
           compatible = "zmk,kscan-mock";
           columns = <0>;
           rows = <0>;
           events = <0>;
       };
   };
   ```

4. **`totem_dongle.conf`** (new):

   ```ini
   # two halves connect to the dongle
   CONFIG_ZMK_SPLIT_BLE_CENTRAL_PERIPHERALS=2
   # 2 peripherals + 5 Bluetooth profiles (ZMK's central default of 6 assumes 1 peripheral)
   CONFIG_BT_MAX_CONN=7
   CONFIG_BT_MAX_PAIRED=7
   # USB-powered, never needs to sleep
   CONFIG_ZMK_SLEEP=n
   ```

5. **`build.yaml`** (repo root): add the dongle and `settings_reset`, and turn the left half into a peripheral.
   Also delete the old comment "there is no settingsreset (needed) for the XIAO" – it's wrong.

   ```yaml
   include:
     - board: seeeduino_xiao_ble
       shield: totem_dongle
     - board: seeeduino_xiao_ble
       shield: totem_left
       cmake-args: -DCONFIG_ZMK_SPLIT_ROLE_CENTRAL=n
     - board: seeeduino_xiao_ble
       shield: totem_right
     - board: seeeduino_xiao_ble
       shield: settings_reset
   ```

6. Optionally add `totem_dongle` to `siblings` in `totem.zmk.yml` (metadata only).

Push. The `firmware.zip` from GitHub Actions then contains `totem_dongle-seeeduino_xiao_ble-zmk.uf2`,
`totem_left-…`, `totem_right-…` and `settings_reset-seeeduino_xiao_ble-zmk.uf2`.
The keymap file needs no changes: the dongle build picks up `config/totem.keymap`, because ZMK also tries
the shield name without its last `_…` part (`totem_dongle` → `totem`).

For comparison, [Conor-Burns/zmk-config-totem-dongle](https://github.com/Conor-Burns/zmk-config-totem-dongle)
is a complete dongle config on ZMK `main` (board `xiao_ble//zmk`, physical layout, ZMK Studio).
It is useful as a reference if you later move this config to ZMK `main` or want ZMK Studio (see below).

### Step 2 – How to flash a XIAO nRF52840

The steps are the same for each device:

1. Connect the device via USB-C to the computer (for the halves: one half at a time).
2. **Double-press the reset button** quickly:
   - **Halves:** each TOTEM half has its own reset button on the PCB.
   - **Dongle:** the XIAO's tiny reset button sits next to the USB-C port. Whether the 3D-printed case leaves it
     reachable (e.g. with a paperclip) isn't documented – check your case.
   - Alternatively, on a half that is already running, press the `&bootloader` key. In this keymap it's on the
     *SYSTEM* layer, left column, middle row. To reach it, hold Enter (SYM+NUM) + Backspace, or Space (NAV) + Esc.
     It always acts on the half where you press it, so the dongle itself can only be put into the
     bootloader with its reset button.
3. The `XIAO-SENSE` drive appears. Mount it via the file manager or `udiskie-mount /dev/disk/by-label/XIAO-SENSE`.
4. Copy the `.uf2` file onto that drive. The XIAO reboots automatically once the copy finishes and the drive
   disappears – a "device was not ejected properly" or copy error message at that moment is normal.

### Step 3 – Wipe old bonds (settings reset) on all three devices

**Why this is needed:** ZMK stores Bluetooth bonds (and other settings such as the selected BT profile) in a
separate flash area that survives flashing new firmware. Right now:

- the **right half** is bonded to the left half and will only ever try to connect to it, so it would ignore the dongle,
- the **left half** is bonded to the right half and to every computer it was paired with,
- the **dongle** may carry bonds from whatever firmware it shipped with.

If these old bonds are left in place, the halves won't connect to the dongle. The `settings_reset` firmware
wipes that flash area. It is the same file for all three devices, because they all use the same XIAO board.

**How:**

1. Unzip `settings_reset-seeeduino_xiao_ble-zmk.uf2` from the same `firmware.zip` as the other files.
2. Flash it onto the **left half**, the **right half** and the **dongle**, one after the other (Step 2 each).
3. After the copy, the device reboots and erases its settings within a few seconds. There is no visible
   feedback. Wait a moment before continuing with that device.

**Good to know:**

- A device running `settings_reset` does nothing else: it doesn't type and has no keymap. The `&bootloader`
  key is therefore gone too, so for Step 4 every device has to be put into the bootloader by
  **double-pressing its reset button**.
- The left half also forgets its pairings with your computers. That's intended, see Step 5.4.
- Flash Step 4 right after this step. Don't leave a device running `settings_reset`, since it is unusable
  as a keyboard.

### Step 4 – Flash the real firmware

1. **Dongle** → `totem_dongle-…uf2`
2. **Left half** → `totem_left-…uf2`
3. **Right half** → `totem_right-…uf2`

Flash all three from the same build.

### Step 5 – First start & pairing

1. Unplug the halves from USB and switch them on with their power switches.
2. Plug the dongle into the computer using the supplied cable. It shows up as a USB keyboard named "TOTEM";
   no Bluetooth pairing with the computer is needed.
3. The dongle automatically finds and bonds with both halves. Press a few keys on each half to check.
   If a half doesn't connect, press the reset button (single press) on that half and on the dongle at about
   the same time, or turn the half off and on again.
4. On every computer that was paired with the TOTEM before, **remove the old "TOTEM" Bluetooth device**
   – the left half no longer talks to computers directly.

Done. To use another computer, simply plug the dongle in there.

### Day-to-day notes

- **Keymap changes usually only need the dongle reflashed.** The keymap (incl. combos, layers) is processed on
  the central, i.e. the dongle. Reflash the halves too when you update ZMK or change
  their hardware config.
- The dongle can additionally act as a Bluetooth keyboard (`&bt` / `&out` keys), but in normal use USB output is used.
  Careful: the `OUT TOG` key on the *SYSTEM* layer switches the dongle to Bluetooth output. If typing over USB
  suddenly stops, press it again.

### ZMK Studio

[ZMK Studio](https://zmk.dev/docs/features/studio) lets you edit the keymap live, without reflashing
(similar to VIA/Vial for QMK). It only matters for the dongle, since that's where the keymap lives.

- **Requirement:** dongle firmware built with Studio support (see the Conor-Burns config for a working example).
- **For this config** this is not set up yet. It would need:
  - a physical layout (e.g. copy `totem-layouts.dtsi` from the Conor-Burns repo)
  - replacing the `chosen` `zmk,matrix_transform` with `zmk,physical-layout`
  - adding `snippet: studio-rpc-usb-uart` and `cmake-args: -DCONFIG_ZMK_STUDIO=y` to the dongle entry in `build.yaml`
  - adding a `&studio_unlock` key to the keymap
- **Linux permissions (once):** `sudo usermod -aG uucp $USER` (Arch; `dialout` on Debian/Ubuntu), then log out and back in.
- **Usage:**
  1. Plug in the dongle and open <https://zmk.studio> in Chrome or Edge (or use the [desktop app](https://zmk.studio/download)).
  2. Connect via USB, then press the `&studio_unlock` key.
  3. Edit keys and layers, then click **Save** – changes persist on the dongle.
- **Limits:** combos, macros, tap dance and newly defined behaviors (e.g. custom hold-taps) can't be edited in
  Studio, and you can't add more layers than the keymap file defines – edit `config/totem.keymap` and
  reflash the dongle for those.
- **Watch out:** once you've saved changes in Studio, later edits to `totem.keymap` are *not* applied
  until you run **Restore Stock Settings** in Studio (per the ZMK docs). Tip: add empty `reserved` layers
  to the keymap file if you want spare layers to fill in via Studio.

### Troubleshooting

- **One half doesn't type**: do Step 3 + 4 again for *all three* devices – leftover bonds are the most
  common cause. Make sure the halves are charged and switched on.
- **No `XIAO-SENSE` drive appears**: the double-press was too slow, or the cable is charge-only; try another cable.
- **GitHub Actions build fails**: this config is pinned to ZMK `v0.3`, so upstream changes shouldn't break it.
  Don't bump it to `main` without also switching the board to `xiao_ble//zmk`. The Zephyr 4.1 update
  (announced Dec 2025) renamed `seeeduino_xiao_ble`, and `xiao_ble//zmk` is the new name.

### Going back to "no dongle" mode

In `build.yaml`, remove the `cmake-args` line of `totem_left` (the dongle entry can stay).
Push, flash `settings_reset` on both halves, then flash the new `totem_left`/`totem_right` and pair the left half
with the computer via Bluetooth again.

## Resources

- [Product Page](https://keeb.supply/products/wireless-dongle)
- [ZMK Documentation](https://zmk.dev/docs/hardware-integration/dongle)
- [Reference dongle config (Conor-Burns)](https://github.com/Conor-Burns/zmk-config-totem-dongle)
- [ZMK Settings Reset](https://zmk.dev/docs/troubleshooting/connection-issues#building-a-reset-firmware)
- [ZMK Studio](https://zmk.dev/docs/features/studio)
