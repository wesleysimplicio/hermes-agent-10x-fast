#!/usr/bin/env bash
# Install Rust toolchain + maturin, then build the hermes_fast PyO3
# extension into the active Python environment.
#
# Phase 3 (perf): hermes-agent works without Rust — the pure-Python
# fallback in agent/_hermes_fast.py is a drop-in. This script is
# optional and only needed to unlock the speedup on the streaming
# tool-call parser, token estimator, and message truncator.
#
# Usage:
#   bash scripts/install-rust.sh             # installs rustup + maturin + builds
#   bash scripts/install-rust.sh --build-only  # skip rustup; assume cargo already present

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUST_DIR="$ROOT/rust_ext"

if [[ "${1:-}" != "--build-only" ]]; then
    if ! command -v cargo >/dev/null 2>&1; then
        echo "[install-rust] cargo not found. Installing rustup (non-interactive)..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
        # shellcheck disable=SC1090
        source "$HOME/.cargo/env"
    else
        echo "[install-rust] cargo already present: $(cargo --version)"
    fi
fi

if ! command -v cargo >/dev/null 2>&1; then
    echo "[install-rust] cargo still unavailable after install. Aborting." >&2
    exit 1
fi

PYTHON="${PYTHON:-python3}"
if ! "$PYTHON" -m pip show maturin >/dev/null 2>&1; then
    echo "[install-rust] Installing maturin into $PYTHON ..."
    "$PYTHON" -m pip install --upgrade maturin
fi

cd "$RUST_DIR"
echo "[install-rust] Building hermes_fast (release)..."
"$PYTHON" -m maturin develop --release

echo "[install-rust] Verifying import..."
"$PYTHON" - <<'PY'
import hermes_fast
print("hermes_fast OK:", hermes_fast.estimate_tokens("hello world"))
PY

echo "[install-rust] Done. Rust hot-path active."
