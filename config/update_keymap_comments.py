#!/usr/bin/env python3
"""
Script to update binding comments in totem.keymap file based on actual bindings.
"""

import re
import sys
from typing import List, Optional

# Key code to display name mapping
KEY_MAPPINGS = {
    # Letters
    "Q": "Q",
    "W": "W",
    "E": "E",
    "R": "R",
    "T": "T",
    "Y": "Y",
    "U": "U",
    "I": "I",
    "O": "O",
    "P": "P",
    "A": "A",
    "S": "S",
    "D": "D",
    "F": "F",
    "G": "G",
    "H": "H",
    "J": "J",
    "K": "K",
    "L": "L",
    "Z": "Z",
    "X": "X",
    "C": "C",
    "V": "V",
    "B": "B",
    "N": "N",
    "M": "M",
    # Numbers
    "N0": "0",
    "N1": "1",
    "N2": "2",
    "N3": "3",
    "N4": "4",
    "N5": "5",
    "N6": "6",
    "N7": "7",
    "N8": "8",
    "N9": "9",
    # Modifiers
    "LSHFT": "SHIFT",
    "RSHFT": "SHIFT",
    "LSHIFT": "SHIFT",
    "RSHIFT": "SHIFT",
    "LCTRL": "CTRL",
    "RCTRL": "CTRL",
    "LCONTROL": "CTRL",
    "RCONTROL": "CTRL",
    "LALT": "ALT",
    "RALT": "ALT",
    "LGUI": "GUI",
    "RGUI": "GUI",
    # Special keys
    "SPACE": "SPC",
    "SPC": "SPC",
    "ENTER": "ENTER",
    "RET": "RET",
    "TAB": "TAB",
    "BSPC": "BSPC",
    "BACKSPACE": "BSPC",
    "DEL": "DEL",
    "DELETE": "DEL",
    "ESC": "ESC",
    "ESCAPE": "ESC",
    # Symbols
    "SEMI": ";",
    "COMMA": ",",
    "DOT": ".",
    "FSLH": "/",
    "BSLH": "\\",
    "EXCL": "!",
    "AT": "@",
    "HASH": "#",
    "DLLR": "$",
    "PRCNT": "%",
    "CARET": "ˆ",
    "AMPS": "&",
    "STAR": "*",
    "LPAR": "(",
    "RPAR": ")",
    "LBRC": "{",
    "RBRC": "}",
    "LBKT": "[",
    "RBKT": "]",
    "SQT": "'",
    "DQT": '"',
    "GRAVE": "`",
    "TILDE": "~",
    "MINUS": "-",
    "EQUAL": "=",
    "PLUS": "+",
    "UNDER": "_",
    # Navigation
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "UP": "UP",
    "DOWN": "DOWN",
    "PG_UP": "P UP",
    "PG_DN": "P DOWN",
    "PGUP": "P UP",
    "PGDN": "P DOWN",
    "HOME": "HOME",
    "END": "END",
    # Function keys
    "F1": "F1",
    "F2": "F2",
    "F3": "F3",
    "F4": "F4",
    "F5": "F5",
    "F6": "F6",
    "F7": "F7",
    "F8": "F8",
    "F9": "F9",
    "F10": "F10",
    "F11": "F11",
    "F12": "F12",
    # Special
    "CAPS": "C LOCK",
    "CAPSLOCK": "C LOCK",
    # Keypad
    "KP_PLUS": "+",
    "KP_MINUS": "-",
    "KP_MULTIPLY": "*",
    "KP_DIVIDE": "/",
    # Media
    "C_MUTE": "MUTE",
    "C_VOL_UP": "VOL+",
    "C_VOL_DN": "VOL-",
    "C_PREV": "LAST",
    "C_NEXT": "NEXT",
    "C_PP": "PLAY",
    # Bluetooth
    "BT_CLR": "BT CLEAR",
    "BT_NXT": "BT NEXT",
    "BT_PRV": "BT PREV",
    # Special codes
    "RA(A)": "Ä",
    "RA(O)": "Ö",
    "RA(U)": "Ü",
    "RA(S)": "SZ",
    "RA(N4)": "POUND",
    "RA(N5)": "EURO",
    "LS(RA(N4))": "YEN",
    "RA(F18)": "EMAIL1",
    "RA(F19)": "EMAIL2",
    # Layer switches and special
    "OUT_TOG": "OUT TOG",
}


def parse_binding(binding: str) -> str:
    """Parse a binding and return a human-readable label."""
    binding = binding.strip()

    # Handle transparent bindings
    if binding == "&trans":
        return ""

    # Handle layer switches with layer-tap
    if binding.startswith("&lt "):
        # Format: &lt LAYER KEY
        parts = binding.split()
        if len(parts) >= 3:
            # Show the key that's tapped
            return parse_binding("&kp " + parts[2])
        return ""

    # Handle momentary layer
    if binding.startswith("&mo "):
        return ""  # Momentary layer, show as empty

    # Handle mod-tap
    if binding.startswith("&mt "):
        # Format: &mt MOD KEY
        parts = binding.split()
        if len(parts) >= 3:
            # For mod-tap, show the key being held (not the modifier)
            key = parts[2]
            return KEY_MAPPINGS.get(key, key)
        return ""

    # Handle key press
    if binding.startswith("&kp "):
        key = binding[4:].strip()
        # Handle special key codes with parentheses like RA(A)
        if "(" in key:
            return KEY_MAPPINGS.get(key, key)
        return KEY_MAPPINGS.get(key, key)

    # Handle special cases
    if binding.startswith("&sys_reset"):
        return "RESET"
    if binding.startswith("&bootloader"):
        return "BOOTLOAD"
    if binding.startswith("&bt "):
        bt_cmd = binding.split()[1] if len(binding.split()) > 1 else ""
        return KEY_MAPPINGS.get(bt_cmd, bt_cmd)
    if binding.startswith("&out "):
        out_cmd = binding.split()[1] if len(binding.split()) > 1 else ""
        return KEY_MAPPINGS.get(out_cmd, out_cmd)

    return ""


def extract_bindings_from_layer(content: str, layer_start: int) -> List[List[str]]:
    """Extract bindings from a layer definition."""
    # Find the end of this layer (next closing brace at the same level)
    layer_section = content[layer_start:]
    layer_end = layer_section.find("};")
    if layer_end == -1:
        layer_section = content[layer_start:]
    else:
        layer_section = layer_section[:layer_end]

    # Find the bindings block within this layer
    bindings_match = re.search(r"bindings\s*=\s*<([^>]+)>;", layer_section, re.DOTALL)
    if not bindings_match:
        return []

    bindings_text = bindings_match.group(1)

    # Remove all comments
    bindings_text = re.sub(r"//.*$", "", bindings_text, flags=re.MULTILINE)

    # Parse bindings - they start with &
    # We need to extract complete bindings like "&kp Q", "&mt LGUI A", "&lt NAV ESC"
    all_bindings = []

    # Split by & and process each binding
    parts = bindings_text.split("&")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Add the & back and take the whole binding
        binding = "&" + part
        all_bindings.append(binding)

    if not all_bindings:
        return []

    # For Totem layout: 10, 10, 12, 6 keys per row
    rows = []
    idx = 0
    row_sizes = [10, 10, 12, 6]

    for size in row_sizes:
        if idx + size <= len(all_bindings):
            row = [parse_binding(b) for b in all_bindings[idx : idx + size]]
            rows.append(row)
            idx += size
        else:
            # Not enough bindings left - pad with empty
            remaining = all_bindings[idx:]
            row = [parse_binding(b) for b in remaining]
            row.extend([""] * (size - len(remaining)))
            if row:
                rows.append(row)
            break

    return rows


def create_comment_box(
    labels: List[List[str]], layout_type: str = "totem"
) -> List[str]:
    """Create ASCII art comment box for the bindings."""
    # Totem layout: 5-5-6-3 keys per row
    lines = []

    if len(labels) < 4:
        return lines

    # Top row (10 keys: 5 left, 5 right)
    if len(labels[0]) >= 10:
        left_keys = labels[0][:5]
        right_keys = labels[0][5:10]
    else:
        left_keys = labels[0][:5] if len(labels[0]) >= 5 else labels[0]
        right_keys = labels[0][5:] if len(labels[0]) > 5 else []

    # Second row (10 keys: 5 left, 5 right)
    if len(labels[1]) >= 10:
        left_keys2 = labels[1][:5]
        right_keys2 = labels[1][5:10]
    else:
        left_keys2 = labels[1][:5] if len(labels[1]) >= 5 else labels[1]
        right_keys2 = labels[1][5:] if len(labels[1]) > 5 else []

    # Third row (12 keys: 6 left, 6 right)
    if len(labels[2]) >= 12:
        left_keys3 = labels[2][:6]
        right_keys3 = labels[2][6:12]
    else:
        left_keys3 = labels[2][:6] if len(labels[2]) >= 6 else labels[2]
        right_keys3 = labels[2][6:] if len(labels[2]) > 6 else []

    # Thumb row (6 keys: 3 left, 3 right)
    if len(labels[3]) >= 6:
        left_thumbs = labels[3][:3]
        right_thumbs = labels[3][3:6]
    else:
        left_thumbs = labels[3][:3] if len(labels[3]) >= 3 else labels[3]
        right_thumbs = labels[3][3:] if len(labels[3]) > 3 else []

    # Pad labels to fit in boxes
    def pad_label(label, width=9):
        if not label:
            label = ""
        label = label[:width]  # Truncate if too long
        return label.center(width)

    # Build the comment box
    lines.append(
        "//             ┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓   ┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓"
    )

    # Row 1
    row1_left = "".join(f"┃ {pad_label(k)} " for k in (left_keys + [""] * 5)[:5])
    row1_right = "".join(f"┃ {pad_label(k)} " for k in (right_keys + [""] * 5)[:5])
    lines.append(f"//             {row1_left}┃   {row1_right}┃")

    lines.append(
        "//             ┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫   ┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫"
    )

    # Row 2
    row2_left = "".join(f"┃ {pad_label(k)} " for k in (left_keys2 + [""] * 5)[:5])
    row2_right = "".join(f"┃ {pad_label(k)} " for k in (right_keys2 + [""] * 5)[:5])
    lines.append(f"//             {row2_left}┃   {row2_right}┃")

    lines.append(
        "// ┏━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫   ┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┓"
    )

    # Row 3
    row3_left = "".join(f"┃ {pad_label(k)} " for k in (left_keys3 + [""] * 6)[:6])
    row3_right = "".join(f"┃ {pad_label(k)} " for k in (right_keys3 + [""] * 6)[:6])
    lines.append(f"// {row3_left}┃   {row3_right}┃")

    lines.append(
        "// ┗━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫   ┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━┛"
    )

    # Thumb row
    thumb_left = "".join(f"┃ {pad_label(k)} " for k in (left_thumbs + [""] * 3)[:3])
    thumb_right = "".join(f"┃ {pad_label(k)} " for k in (right_thumbs + [""] * 3)[:3])
    lines.append(
        f"//                                     {thumb_left}┃   {thumb_right}┃"
    )

    lines.append(
        "//                                     ┗━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━┛   ┗━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━┛"
    )

    return lines


def update_keymap_file(input_file: str, output_file: Optional[str] = None) -> None:
    """Update the keymap file with corrected binding comments."""
    if output_file is None:
        output_file = input_file

    with open(input_file, "r") as f:
        content = f.read()

    # Find all layer definitions
    layer_pattern = r"(\w+_layer)\s*\{"
    layers = list(re.finditer(layer_pattern, content))

    new_content = content
    offset = 0

    for layer_match in layers:
        layer_start = layer_match.start()

        # Find the end of this layer
        layer_end = content.find("};", layer_start)
        if layer_end == -1:
            continue

        # Extract bindings
        bindings = extract_bindings_from_layer(content, layer_start)

        if not bindings:
            continue

        # Create new comment box
        new_comments = create_comment_box(bindings)

        # Find the existing comment box for this layer
        # Look for the pattern between label and bindings
        layer_section = content[layer_start:layer_end]

        # Find where the old comment box starts and ends
        comment_start_pattern = r"//\s+┏━━━━━━━━━━━┳━━━━━━━━━━━┳"
        comment_end_pattern = r"//\s+┗━━━━━━━━━━━┻━━━━━━━━━━━┻"

        comment_start = re.search(comment_start_pattern, layer_section)
        comment_end = re.search(comment_end_pattern, layer_section)

        if comment_start and comment_end:
            # Detect the indentation of the original comment
            # Find the start of the line containing the first comment
            line_start_pos = layer_section.rfind("\n", 0, comment_start.start())
            if line_start_pos == -1:
                line_start_pos = 0
            else:
                line_start_pos += 1  # Move past the newline

            # Get the text from line start to the comment start
            line_before_comment = layer_section[line_start_pos : comment_start.start()]
            # The indent is just the whitespace part
            indent = ""
            for char in line_before_comment:
                if char in " \t":
                    indent += char
                else:
                    break

            # Find where the old comment block truly ends
            # We need to find the line after the last comment line (which ends with ┛)
            end_pos = comment_end.end()
            # Find the newline after this line
            next_newline = layer_section.find("\n", end_pos)
            if next_newline == -1:
                next_newline = len(layer_section)

            # Now check if there are more comment lines after this that are part of the layout
            # (these would be old thumb row comments that should be removed)
            search_pos = next_newline + 1
            while search_pos < len(layer_section):
                next_line_start = search_pos
                next_line_end = layer_section.find("\n", search_pos)
                if next_line_end == -1:
                    next_line_end = len(layer_section)

                next_line = layer_section[next_line_start:next_line_end].strip()

                # Check if this is still a comment line that's part of the layout
                # (starts with // and contains box drawing characters or is the thumb row)
                if next_line.startswith("//") and (
                    "┃" in next_line
                    or "┗" in next_line
                    or "┻" in next_line
                    or "┛" in next_line
                ):
                    # This is part of the old comment block, keep extending
                    search_pos = next_line_end + 1
                else:
                    # This is not a comment or not part of the layout, stop here
                    break

            # IMPORTANT: Start replacement from the beginning of the line (line_start_pos),
            # not from where the comment marker starts (comment_start.start())
            old_comments_start = layer_start + line_start_pos
            old_comments_end = layer_start + search_pos

            # Apply indentation to new comments
            indented_comments = [indent + line for line in new_comments]
            new_comment_block = "\n".join(indented_comments) + "\n"

            new_content = (
                new_content[: old_comments_start + offset]
                + new_comment_block
                + new_content[old_comments_end + offset :]
            )

            offset += len(new_comment_block) - (old_comments_end - old_comments_start)

    # Write the updated content
    with open(output_file, "w") as f:
        f.write(new_content)

    print(f"Updated keymap saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_keymap_comments.py <keymap_file> [output_file]")
        sys.exit(1)

    input_file: str = sys.argv[1]
    output_file: Optional[str] = sys.argv[2] if len(sys.argv) > 2 else None

    update_keymap_file(input_file, output_file)
