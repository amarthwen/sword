#!/bin/bash

source colors.sh

Cfg_StudiesDir='studies'
Cfg_OutputDir='output'

cmd_PrintWithColor ${COL_1} "Updating studies and generated output files"
cp -r -u $Cfg_StudiesDir/ $Cfg_OutputDir/ ../RE/
if (( $? == 0 )); then
  echo -e "[${COL_2} OK ${COL_X}]"
else
  echo -e "[${COL_1}FAIL${COL_X}]"
fi

