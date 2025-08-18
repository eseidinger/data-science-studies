#!/bin/bash
set -x
export GID="$(id -g)"
export UID="$(id -u)"

if [[ "$OSTYPE" == "linux-gnu"* ]]
 then
  docker compose -f docker-compose.yml up
 elif [[ "$OSTYPE" == "darwin"* ]]
 then
  docker compose -f docker-compose.yml up
 elif [[ "$OSTYPE" == "cygwin" ]]; then
  echo "win_emu" # POSIX compatibility layer and Linux environment emulation for Windows
 elif [[ "$OSTYPE" == "msys" ]]; then
   echo "win" # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
 elif [[ "$OSTYPE" == "win32" ]]
 then
    echo "win other"    # I'm not sure this can happen.
elif [[ "$OSTYPE" == "freebsd"* ]]; then
echo "test"
# ...
 # Unknown.
fi
