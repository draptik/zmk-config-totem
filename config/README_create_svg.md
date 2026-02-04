# Creating SVG images of all layers

The python program [`keymap-drawer`](https://github.com/caksoylar/keymap-drawer) can create SVG images from a given `keymap` file.

## Setup

Install `keymap-drawer` using `uv`.

```bash
pacman -S uv
uv tool install keymap-drawer
uv tool update-shell
```

## Usage

```bash
keymap parse -c 10 -z totem.keymap > totem.yaml
keymap draw totem.yaml > totem.svg
```
