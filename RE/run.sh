#!/bin/bash

source colors.sh

Cfg_StudiesDir='studies'
Cfg_StudiesFilenameExt='txt'
Cfg_OutputDir='output'
Cfg_ConvertedStudiesOutputDir=$Cfg_OutputDir'/xml'
Cfg_ConvertedStudiesFilenameExt='xml'

function cmd_ConvertStudies() {
  for tmp_FileName in $Cfg_StudiesDir/*.$Cfg_StudiesFilenameExt; do
    tmp_Study=$(basename "$tmp_FileName" | cut -d. -f1)
    tmp_Rslt=`python -B convert.py "$tmp_FileName" "$Cfg_ConvertedStudiesOutputDir"`
    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi
    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done
}

# step 2 - generate output files
function cmd_GenerateOutputFiles() {
  for tmp_FileName in $Cfg_ConvertedStudiesOutputDir/*.$Cfg_ConvertedStudiesFilenameExt; do
    tmp_Study=$(basename "$tmp_FileName" | cut -d. -f1)
    tmp_Rslt=`python -B generate.py "$tmp_FileName" "$Cfg_OutputDir"`
    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi
    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done
}

# step 1 - remove all generated files
rm -rf $Cfg_OutputDir/*

# step 2 - convert files
if [ -z "$1" ] || [ "$1" != "-g" ]; then
  cmd_PrintWithColor ${COL_1} "Convert studies:"
  cmd_ConvertStudies
fi

# step 3 - generate output files
cmd_PrintWithColor ${COL_1} "Generate output files:"
cmd_GenerateOutputFiles

