#!/bin/bash

source colors.sh

Cfg_StudiesDir='studies'
Cfg_StudiesFilenameExt='txt'
Cfg_OutputDir='output/xml'

for tmp_FileName in $Cfg_StudiesDir/*.$Cfg_StudiesFilenameExt; do
  tmp_Study=$(basename "$tmp_FileName" | cut -d. -f1)
  tmp_Rslt=`python -B convert.py "$tmp_FileName" "$Cfg_OutputDir"`
  if (( $? == 0 )); then
    echo -e -n "[${COL_2} OK ${COL_X}]"
  else
    echo -e -n "[${COL_1}FAIL${COL_X}]"
  fi
  echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
done

