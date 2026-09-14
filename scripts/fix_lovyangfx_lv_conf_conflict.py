"""
LovyanGFX bundles a full example project (examples/Advanced/LVGL_PlatformIO)
inside its own library folder, including its own lv_conf.h. PlatformIO's
dependency scanner can end up finding that copy before this project's real
one (include/lv_conf.h), which silently produces an LVGL build using
default settings instead of ours (missing fonts, wrong tick config, etc.)
with no hard error -- just the easy-to-miss
"Possible failure to include lv_conf.h" compiler note.

This runs before every build and removes any such stray copy so the
project's own include/lv_conf.h is always the one found.
"""

import glob
import os

Import("env")

project_dir = env.subst("$PROJECT_DIR")
pattern = os.path.join(project_dir, ".pio", "libdeps", "*", "LovyanGFX",
                        "examples", "**", "lv_conf.h")

for path in glob.glob(pattern, recursive=True):
    try:
        os.remove(path)
        print("[fix_lovyangfx_lv_conf_conflict] Removed conflicting file: %s" % path)
    except OSError as e:
        print("[fix_lovyangfx_lv_conf_conflict] Could not remove %s: %s" % (path, e))