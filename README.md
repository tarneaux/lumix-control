> :warning: I started this project not really knowing what I would do, and quickly lost hope for it to be useful. However, there is another project of mine, [studiocontrol](https://github.com/tarneaux/studiocontrol), that aims to be a way to control multiple devices (cameras, microphones, lighting equipment) at once from a single app.

# lumix-control
A python library to control the lumix DMC-GX80W using wifi
> :warning: **lumix-control is still in early stages of development. All features and commands are still subject to changes.**

## Installing
```bash
git clone https://github.com/tarneaux/lumix-control.git
cd lumix-control
pip install .
```

# Usage
See `lumix-control -h`

# Troubleshooting
If the `lumix-control` command is not found, try adding ~/.local/bin/ to your `PATH`.

If this still doesn't work, open an [issue](https://github.com/tarneaux/lumix-control/issues)

# Features
- [x] Copy pictures from camera to computer
  - [ ] Select which pictures to copy
- [ ] Geotag pictures on the computer

# Todo
- [ ] tests
- [ ] auto-build python package
