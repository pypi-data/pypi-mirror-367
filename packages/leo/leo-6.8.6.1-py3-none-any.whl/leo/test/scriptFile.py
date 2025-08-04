#@+leo-ver=5-thin
#@+node:ekr.20231107062256.1: * @button check-leoPy.leo
"""Ensure that all expected @<file> nodes exist."""
g.cls()
import glob
import os
join, sep = os.path.join, os.sep

def norm(path):
    return os.path.normpath(path).lower()

# Compute the directories.
leo_dir = norm(join(g.app.loadDir, '..'))  ### '..'))
core_dir = join(leo_dir, 'core')
commands_dir = join(leo_dir, 'commands')
external_dir = join(leo_dir, 'external')
importers_dir = join(leo_dir, 'plugins', 'importers')
plugins_dir = join(leo_dir, 'plugins')
scripts_dir = join(leo_dir, 'scripts')
unittests_dir = join(leo_dir, '..', 'unittests')
writers_dir = join(leo_dir, 'plugins', 'writers')

def make_list(pattern):
    return [norm(z) for z in glob.glob(pattern) if '__init__' not in z]

# Find paths on disk.
core_files = make_list(f"{core_dir}{sep}*.py")
commands_files = make_list(f"{commands_dir}{sep}*.py")
external_files = make_list(f"{external_dir}{sep}*.py")
importer_files = make_list(f"{importers_dir}{sep}*.py")
# plugin_files = make_list(f"{plugins_dir}{sep}*.py")
qt_files = make_list(f"{plugins_dir}{sep}qt*.py")
script_files = make_list(f"{scripts_dir}{sep}*.py")
unittests_files = make_list(f"{unittests_dir}{sep}*.py")
writer_files = make_list(f"{writers_dir}{sep}*.py")

# Compute paths from @<file> nodes.
at_file_paths = sorted([
    norm(c.fullPath(z))
        for z in c.all_unique_positions()
            if z.isAnyAtFileNode()
])

excluded_files = (
    r'plugins\qt_main.py',  # Generated automatically.
    r'plugins\baseNativeTree.py',  # No longer used.
)

def is_excluded(path):
    return any(z in path for z in excluded_files)

if 0:
    for files, kind in (
        (at_file_paths, 'all known paths'),
        (core_files, 'core_files'),
        (qt_files, 'qt_files'),
        (importer_files, 'importer_files'),
        (writer_files, 'writer_files'),
    ):
        g.printObj(files, tag=f"{kind}")

# Ensure that @<file> nodes exist for every file on disk.
missing = []
for z in core_files + external_files + qt_files + importer_files + writer_files:
    if z not in at_file_paths and not is_excluded(z):
        missing.append(z)
if missing:
    g.printObj(missing, tag='missing @<file> nodes')
else:
    print('No missing files!')
print('done')
#@-leo

