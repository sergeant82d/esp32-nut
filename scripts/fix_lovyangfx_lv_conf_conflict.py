"""
Ensures LVGL always uses this project's own include/lv_conf.h,
unambiguously.

Background: LVGL's normal way of finding lv_conf.h relies on the
preprocessor's __has_include() plus a plain quoted #include "lv_conf.h",
searched via the compiler's include path. In practice that's fragile here:
- Some libraries (LovyanGFX, and sometimes lvgl itself) bundle example
  projects inside their own library folders that include their own
  lv_conf.h, which can get found instead of ours.
- The include-path search order used for the lvgl *library's* own .c
  files can differ from the one used for *our* source files (like
  lib/LcdDisplay/src/LcdDisplay.cpp), so the same project can compile
  correctly in one and silently fall back to LVGL's built-in defaults in
  the other -- with no hard error, just an easy-to-miss
  "Possible failure to include lv_conf.h" compiler note, and mysterious
  "not declared in this scope" errors for anything the real lv_conf.h
  would have enabled (extra fonts, etc.).

Fix: first remove any stray lv_conf.h bundled inside library examples
under .pio/libdeps (belt and suspenders), then explicitly define
LV_CONF_PATH as an absolute path straight to this project's
include/lv_conf.h. LVGL checks LV_CONF_PATH first, before any
__has_include-based searching, so this bypasses the ambiguity entirely.
"""

import glob
import os

Import("env")

project_dir = env.subst("$PROJECT_DIR")

# Belt and suspenders: remove any stray bundled copies.
stray_pattern = os.path.join(project_dir, ".pio", "libdeps", "**", "lv_conf.h")
for path in glob.glob(stray_pattern, recursive=True):
    try:
        os.remove(path)
        print("[fix_lv_conf] Removed conflicting file: %s" % path)
    except OSError as e:
        print("[fix_lv_conf] Could not remove %s: %s" % (path, e))

# Force LVGL to use our copy directly, unambiguously. NOTE: do not
# manually quote this value -- lv_conf_internal.h stringizes LV_CONF_PATH
# itself via the preprocessor's # operator, so a pre-quoted value here
# would end up double-quoted and break the resulting #include.
lv_conf_path = os.path.join(project_dir, "include", "lv_conf.h").replace("\\", "/")
env.Append(CPPDEFINES=[("LV_CONF_PATH", lv_conf_path)])
print("[fix_lv_conf] Forcing LV_CONF_PATH=%s" % lv_conf_path)