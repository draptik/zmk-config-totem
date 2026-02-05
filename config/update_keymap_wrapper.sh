#!/bin/bash

python ./update_keymap_comments.py totem.keymap

keymap parse -c 10 -z totem.keymap >totem.yaml
keymap draw totem.yaml >totem.svg
