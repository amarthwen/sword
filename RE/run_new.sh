#!/bin/bash

source colors.sh

Cfg_StudiesDir='studies'
Cfg_StudiesFilenameExt='txt'

for tmp_FileName in $Cfg_StudiesDir/*.$Cfg_StudiesFilenameExt; do
  tmp_Study=$(basename "$tmp_FileName" | cut -d. -f1)
  tmp_Rslt=`python generators.py "$tmp_FileName"`
  if (( $? == 0 )); then
    echo -e -n "[${COL_2} OK ${COL_X}]"
  else
    echo -e -n "[${COL_1}FAIL${COL_X}]"
  fi
  echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
done

