#!/usr/bin/env bash

set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."

    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install uv but is not installed"
        exit 1
    fi

    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

