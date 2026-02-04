# Totem Keymap Comment Updater

This script automatically updates the ASCII art binding comments in `totem.keymap` file to match the actual key bindings.

## Features

- Parses ZMK keymap bindings and generates accurate ASCII art diagrams
- Handles mod-tap, layer-tap, and various key types
- Supports special characters, media keys, function keys, and more
- Preserves the original file structure and formatting

## Usage

### Basic usage (overwrites original file):
```bash
python update_keymap_comments.py totem.keymap
```

### Save to a different file:
```bash
python update_keymap_comments.py totem.keymap totem_updated.keymap
```

## How It Works

The script:
1. Parses your keymap file to find all layer definitions
2. Extracts the actual bindings from each layer
3. Converts binding codes to human-readable labels (e.g., `&kp LSHFT` → `SHIFT`)
4. Generates new ASCII art comment boxes matching the Totem layout
5. Replaces the old comment boxes with the updated ones

## Supported Key Types

- **Standard keys**: Letters, numbers, symbols
- **Modifiers**: Shift, Control, Alt, GUI
- **Special keys**: Enter, Tab, Space, Backspace, Delete, Escape
- **Navigation**: Arrow keys, Page Up/Down, Home, End
- **Function keys**: F1-F12
- **Media controls**: Volume, Mute, Play/Pause, Next/Previous
- **Bluetooth**: BT_CLR, BT_NXT, BT_PRV
- **Special characters**: Ä, Ö, Ü, ß (using RA() codes)
- **Layer switches**: Momentary and layer-tap
- **Mod-tap**: Combined modifier and key press

## Customization

You can extend the `KEY_MAPPINGS` dictionary in the script to add custom key labels or modify existing ones. For example:

```python
KEY_MAPPINGS = {
    'CUSTOM_KEY': 'MY KEY',
    # ... other mappings
}
```

## Notes

- The script preserves empty cells for `&trans` bindings
- Mod-tap bindings show the base key being pressed
- Layer-tap bindings show the key when tapped
- The script automatically handles the Totem layout (5-5-6-3 key arrangement)

## Example

Before:
```
// ┃     Q     ┃     W     ┃     E     ┃ (incorrect) ┃
```

After:
```
// ┃     Q     ┃     W     ┃     E     ┃     R     ┃
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)
