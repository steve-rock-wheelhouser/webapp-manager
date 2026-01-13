#!/bin/bash
# Launch the Web App Launcher Manager
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Clean environment to prevent "encodings" and "exec_prefix" errors
# usually caused by leftover host/sandbox library conflicts.
unset LD_LIBRARY_PATH
unset PYTHONPATH
unset PYTHONHOME

# Set typelib path to include host libraries if they exist
HOST_TYPELIB="/run/host/usr/lib64/girepository-1.0"
if [ -d "$HOST_TYPELIB" ]; then
    export GI_TYPELIB_PATH="$HOST_TYPELIB:$GI_TYPELIB_PATH"
fi

source "$DIR/.venv/bin/activate"
python "$DIR/app.py"
