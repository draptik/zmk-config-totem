# Prospector – Dongle with Display

The stock Totem dongle (XIAO nRF52840 in a closed 3D-printed case) gives no feedback about the
battery level of the two halves: its onboard LED is hidden by the case, and over USB the computer
does not get any battery information from the halves.

[Prospector](https://github.com/carrefinho/prospector) is an open-source ZMK dongle with a 1.69"
round color LCD that solves this.

## Advantages

- **Battery level of both halves** on screen, permanently visible
- **Connection status** of each half
- **Active layer** (shown by name if `display-name` is set in the keymap) and a **Caps Word** indicator
- **Same controller** as the stock dongle (XIAO nRF52840), so the role in this config stays the same:
  the dongle remains the central, the halves stay peripherals
- **Supports ZMK v0.3**, the version this config uses
- Standard kit has an **ambient light sensor** that adapts the screen brightness
- Only small config changes needed (see below)

## Where to buy

- [Keycapsss – Prospector Kit](https://keycapsss.com/Prospector-Kit-ZMK-dongle-with-full-color-LCD-screen/KC10254-ECO)
  (Leipzig, Germany, ~€39). **Kit – wires must be soldered.**
  - *Standard*: with ambient light sensor, MJF-printed case
  - *Eco*: without light sensor, simpler case
- [Beekeeb – Pre-soldered Prospector](https://shop.beekeeb.com/products/pre-soldered-prospector-zmk-dongle)
  (~$68, ships from outside the EU) – no soldering needed

In both cases the firmware has to be built from this config.

## Required config changes

According to the [prospector-zmk-module README](https://github.com/carrefinho/prospector-zmk-module):

- `config/west.yml`: add the `carrefinho` remote and the `prospector-zmk-module` project (revision `main`)
- `build.yaml`: dongle build becomes `shield: totem_dongle prospector_adapter`
- `config/boards/shields/totem/totem_dongle.conf`: optionally set
  `CONFIG_PROSPECTOR_FIXED_BRIGHTNESS` and, for the Eco kit, `CONFIG_PROSPECTOR_USE_AMBIENT_LIGHT_SENSOR=n`
- Pair the **left half first, then the right half**, so the screen shows them in the right order
