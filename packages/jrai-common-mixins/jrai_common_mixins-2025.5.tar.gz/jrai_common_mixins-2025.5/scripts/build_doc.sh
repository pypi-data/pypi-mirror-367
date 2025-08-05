#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
DIR=${SELF%/*/*}

cd -- "$DIR"

function show_help()
{
  cat << HELP
USAGE

  ${0##*/} [-h] [-v]

OPTIONS

  -h
    Show this help message and exit.

  -v
    Use a Python virtual environment to build the documentation.

HELP
  exit "$1"
}

in_venv=false
while getopts "hv" opt
do
  case "$opt" in
    h) show_help 0 ;;
    v) in_venv=true ;;
    *) show_help 1 ;;
  esac
done

if command -v uv >/dev/null 2>&1
then
  found_uv=true
  install_cmd=(uv pip install)
else
  found_uv=false
  install_cmd=(pip install)
fi

if "$in_venv"
then
  if "$found_uv"
  then
    uv venv venv
    # shellcheck source=/dev/null
    source venv/bin/activate
  else
    python -m venv venv
    # shellcheck source=/dev/null
    source venv/bin/activate
    "${install_cmd[@]}" -U pip
  fi
elif "$found_uv"
then
  install_cmd+=(--system)
fi

"${install_cmd[@]}" -U -r doc/requirements.txt
sphinx-apidoc -o doc/source -f -H "API Documentation" ./src
sphinx-build -b html doc/source public
# Run again to fix cross-references.
sphinx-build -b html doc/source public
