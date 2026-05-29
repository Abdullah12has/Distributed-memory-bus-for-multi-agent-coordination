#!/usr/bin/env bash
# Build the thesis PDF from thesis_latex/main.tex.
# Prerequisites: BasicTeX installed via `brew install --cask basictex`
# then `eval "$(/usr/libexec/path_helper)"` to pick up the TeX binaries.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEXDIR="$ROOT/thesis_latex"
OUTDIR="$ROOT/thesis_latex/out"

# ── 1. Check that pdflatex and biber are on PATH ──────────────────────────
if ! command -v pdflatex &>/dev/null; then
  echo "ERROR: pdflatex not found. Install BasicTeX:"
  echo "  brew install --cask basictex"
  echo "  eval \"\$(/usr/libexec/path_helper)\""
  exit 1
fi

# ── 2. Install required TeX packages (BasicTeX ships very few) ────────────
# Only runs if a marker file is missing; subsequent builds skip this.
MARKER="$TEXDIR/.texpackages-installed"
if [ ! -f "$MARKER" ]; then
  echo "→ Updating tlmgr..."
  sudo tlmgr update --self

  echo "→ Installing required TeX packages (one-time)..."
  sudo tlmgr install \
    latexmk \
    newtx txfonts fontaxes boondox tex-gyre \
    titlesec titlecaps ifnextok chngcntr appendix newfile \
    enumitem placeins multirow caption tocloft \
    csquotes xurl algorithm2e ifoddpage relsize \
    biblatex biber logreq \
    pdfx xmpincl colorprofiles \
    hyphsubst babel-finnish babel-english \
    etoolbox xstring ifthen \
    collection-fontsrecommended \
    doclicense xifthen ifmtarg \
    tcolorbox environ pgf trimspaces tikzfill \
    pict2e mdframed needspace zref \
    || echo "Warning: tlmgr install returned non-zero (some packages may already be installed)"
  touch "$MARKER"
  echo "✓ TeX packages installed."
fi

# ── 3. Build with latexmk ─────────────────────────────────────────────────
mkdir -p "$OUTDIR"
cd "$TEXDIR"

echo "→ Building thesis PDF..."
latexmk -pdf \
  -interaction=nonstopmode \
  -halt-on-error \
  -output-directory="$OUTDIR" \
  main.tex

# Copy the PDF to the project root for easy access
cp "$OUTDIR/main.pdf" "$ROOT/thesis.pdf"

echo ""
echo "✓ Thesis built successfully."
echo "  PDF: $ROOT/thesis.pdf"
echo "  open $ROOT/thesis.pdf"
