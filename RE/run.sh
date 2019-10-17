#!/bin/bash

source colors.sh

Cfg_StudiesDir='studies'
Cfg_StudiesFilenameExt='txt'
Cfg_OutputDir='output'
Cfg_ConvertedStudiesOutputDir=$Cfg_OutputDir'/xml'
Cfg_ConvertedStudiesFilenameExt='xml'
Cfg_TmpDir="./tmp"

# wrapper for pushd
pushd () {
  command pushd "$@" > /dev/null
}

# wrapper for popd
popd () {
  command popd "$@" > /dev/null
}

function cmd_ConvertStudies() {
  # convert studies
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

function cmd_GenerateOutputFiles() {
  # generate output files
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

function cmd_GeneratePDFFilesFromLATEXSources() {
  # create output directory for generated LATEX files (if doesn't exist)
  mkdir -p $Cfg_OutputDir/tex

  # create output directory for generated PDF files (if doesn't exist) and clean it
  mkdir -p $Cfg_OutputDir/pdf && rm -rf $Cfg_OutputDir/pdf/*

  # create temporary directory for LATEX sources (if doesn't exist) and clean it
  mkdir -p $Cfg_TmpDir/tex && rm -rf $Cfg_TmpDir/tex

  # copy LATEX sources to temporary directory
  cp -r $Cfg_OutputDir/tex $Cfg_TmpDir/tex

  # enter temporary directory
  pushd $Cfg_TmpDir/tex

  # generate PDF files from LATEX sources
  for tmp_FileName in ./*.tex; do
    tmp_Study=$(basename "$tmp_FileName" | cut -d. -f1)

    tmp_Rslt=`pdflatex "$tmp_FileName"`

    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi

    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done

  # leave temporary directory
  popd

  # move all generated PDF files to output directory
  mv $Cfg_TmpDir/tex/*.pdf $Cfg_OutputDir/pdf
}

# step 1 - remove all generated files
rm -rf $Cfg_OutputDir/*

# step 2 - convert files
if [ -z "$1" ] || [ "$1" != "-g" ]; then
  cmd_PrintWithColor ${COL_1} "Converting studies:"
  cmd_ConvertStudies
fi

# step 3 - generate output files
cmd_PrintWithColor ${COL_1} "Generating output files:"
cmd_GenerateOutputFiles

# step 4 - generate PDF files from LATEX sources
cmd_PrintWithColor ${COL_1} "Generating PDF files from LATEX sources:"
cmd_GeneratePDFFilesFromLATEXSources

# step 5 - add styles to generated web pages
if [ -d "$Cfg_OutputDir/htm" ]; then
  cmd_PrintWithColor ${COL_1} "Adding styles to generated web pages"
  cp -r $Cfg_TmpDir/generators/htm/styles $Cfg_OutputDir/htm
fi
