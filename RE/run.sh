#!/bin/bash
python main_001.py Bible/BW.txt studies output
pushd output/latex
for filename in ./*.tex; do
    echo "Export to PDF: $filename"
    `pdflatex "$filename" 2>&1 >/dev/null`
done
mv *.pdf ../pdf
find . -type f -not -name '*.tex' -delete
popd
