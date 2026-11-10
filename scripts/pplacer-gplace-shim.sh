#!/usr/bin/env bash
# Install first on PATH under the name `pplacer`. GTDB-Tk calls
# `pplacer -m WAG -j N -c REFPKG -o OUT.json MSA`; this runs `gplace place` with the same
# arguments and a memory limit. `pplacer --version` goes to the real pplacer (REAL_PPLACER).
set -euo pipefail
if [[ ${1:-} == --version ]]; then exec "${REAL_PPLACER:?set REAL_PPLACER to the real pplacer}" --version; fi
[[ -n ${GPLACE_CALL_LOG:-} ]] && echo "gplace place --max_memory ${GPLACE_MAX_MEMORY:-8.5G} $*" >> "$GPLACE_CALL_LOG"
exec gplace place --max_memory "${GPLACE_MAX_MEMORY:-8.5G}" "$@"
