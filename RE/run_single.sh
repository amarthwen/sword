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
  tmp_Study=$(basename "$1" | cut -d. -f1)

  # convert studies
  for tmp_FileName in "$Cfg_StudiesDir/$tmp_Study.$Cfg_StudiesFilenameExt"; do
    

    tmp_Rslt=`python3 -B convert.py "$tmp_FileName" "$Cfg_ConvertedStudiesOutputDir"`

    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi

    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done
}

function cmd_GenerateOutputFiles() {
  tmp_Study=$(basename "$1" | cut -d. -f1)

  # generate output files
  for tmp_FileName in "$Cfg_ConvertedStudiesOutputDir/$tmp_Study.$Cfg_ConvertedStudiesFilenameExt"; do
    tmp_Rslt=`python3 -B generate.py "$tmp_FileName" "$Cfg_OutputDir"`

    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi

    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done
}

function cmd_GeneratePDFFilesFromLATEXSources() {
  tmp_Study=$(basename "$1" | cut -d. -f1)

  # create output directory for generated LATEX files (if doesn't exist)
  mkdir -p $Cfg_OutputDir/tex

  # create output directory for generated PDF files (if doesn't exist) and clean it
  mkdir -p $Cfg_OutputDir/pdf && rm -rf "$Cfg_OutputDir/pdf/$tmp_Study.pdf"

  # create temporary directory for LATEX sources (if doesn't exist) and clean it
  mkdir -p $Cfg_TmpDir/tex && rm -rf $Cfg_TmpDir/tex

  # copy LATEX sources to temporary directory
  cp -r $Cfg_OutputDir/tex $Cfg_TmpDir/tex

  # enter temporary directory
  pushd $Cfg_TmpDir/tex

  # generate PDF files from LATEX sources
  for tmp_FileName in "./$tmp_Study.tex"; do
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

  # move generated PDF file to output directory
  mv "$Cfg_TmpDir/tex/$tmp_Study.pdf" $Cfg_OutputDir/pdf
}

function cmd_GeneratePDFFilesFromFODTSources() {
  tmp_Study=$(basename "$1" | cut -d. -f1)

  # create output directory for generated PDF files (if doesn't exist) and clean it
  mkdir -p $Cfg_OutputDir/pdf && rm -rf "$Cfg_OutputDir/pdf/$tmp_Study.pdf"

  # generate PDF files from FODT sources
  for tmp_FileName in "$Cfg_OutputDir/fodt/$tmp_Study.fodt"; do
    tmp_Rslt=`libreoffice --headless --convert-to pdf --outdir $Cfg_OutputDir/pdf "$tmp_FileName" 2>&1`

    if (( $? == 0 )); then
      echo -e -n "[${COL_2} OK ${COL_X}]"
    else
      echo -e -n "[${COL_1}FAIL${COL_X}]"
    fi

    echo -e " Processing study: \"${COL_4}${tmp_Study}${COL_X}\""
  done
}

# step 2 - convert files
# if [ -z "$1" ] || [ "$1" != "-g" ]; then
cmd_PrintWithColor ${COL_1} "Converting studies:"
cmd_ConvertStudies "$1"
# fi

# step 3 - generate output files
cmd_PrintWithColor ${COL_1} "Generating output files:"
cmd_GenerateOutputFiles "$1"

# step 4 - generate PDF files from LATEX sources
# cmd_PrintWithColor ${COL_1} "Generating PDF files from LATEX sources:"
# cmd_GeneratePDFFilesFromLATEXSources

# step 5 - generate PDF files from FODT sources
cmd_PrintWithColor ${COL_1} "Generating PDF files from FODT sources:"
cmd_GeneratePDFFilesFromFODTSources "$1"

# step 6 - add styles to generated web pages
if [ -d "$Cfg_OutputDir/htm" ]; then
  cmd_PrintWithColor ${COL_1} "Adding styles to generated web pages"
  cp -r $Cfg_TmpDir/generators/htm/styles $Cfg_OutputDir/htm
  if (( $? == 0 )); then
    echo -e "[${COL_2} OK ${COL_X}]"
  else
    echo -e "[${COL_1}FAIL${COL_X}]"
  fi
fi

