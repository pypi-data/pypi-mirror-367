#!/usr/bin/env bash
# Usage: _add_to_pythonpath.sh <dir_to_add> <command> [cmd-arg1 cmd-arg2 …]
#
# Adds <dir_to_add> to the front of PYTHONPATH (only if it is not already
# present) and then executes the given <command>.

# Set up the environment for the script
set -euo pipefail

# Parse arguments
if [[ "$#" -lt 2 ]]; then
    echo "Usage: $0 <dir_to_add> <command> [args...]" >&2
    exit 1
fi
dir_to_add=$1
shift

# Check if the directory to add exists and is a directory
if [[ ! -d "$dir_to_add" ]]; then
    echo "Error: '$dir_to_add' is not a directory." >&2
    exit 2
fi

# Resolve the absolute path of the directory to add
dir_to_add=$(realpath "$dir_to_add")

# Update PYTHONPATH
export PYTHONPATH="$dir_to_add${PYTHONPATH:+:$PYTHONPATH}"

# Execute the subsequent command
exec "$@"
