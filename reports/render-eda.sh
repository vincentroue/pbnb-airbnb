#!/bin/bash
# Render EDA notebook with increased Node memory to avoid JS heap OOM
# Usage: bash render-eda.sh [--all]

export NODE_OPTIONS="--max-old-space-size=8192"

if [ "$1" = "--all" ]; then
    echo "Rendering all website pages..."
    quarto render
else
    echo "Rendering EDA notebook only..."
    quarto render rpt-nbk-bnb-eda-260207.qmd
fi
