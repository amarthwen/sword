# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import argparse, codecs, os, sys
import xml.etree.ElementTree as ET
from modules import Modules

# ================================================================ #
# configuration
# ================================================================ #
Cfg_ChrComment = '#'

# ================================================================ #
# main()
# ================================================================ #
def main():
  tmp_Parser = argparse.ArgumentParser()
  tmp_Parser.add_argument('OptInput', metavar='FILE', help='input file to be processed')
  tmp_Parser.add_argument('OptOutput', metavar='FOLDER', help='output folder where the processed data will be stored')
  tmp_Args = tmp_Parser.parse_args()

  # sanity check
  if not os.path.exists(tmp_Args.OptInput):
    sys.exit(os.EX_OSFILE)

  print 'Processing file: "' + tmp_Args.OptInput + '"'

  with codecs.open(tmp_Args.OptInput, 'r', 'utf-8') as tmp_File:
    tmp_FileContents = [tmp_Line.strip() for tmp_Line in tmp_File.readlines()]

  # remove empty lines and comments
  tmp_FileContents[:] = [tmp_Line for tmp_Line in tmp_FileContents if len(tmp_Line) > 0 and tmp_Line[0] != Cfg_ChrComment]

  # create instance of modules
  tmp_Mods = Modules.Modules()

  # register modules
  tmp_Mods.Register(Modules.DOC())
  tmp_Mods.Register(Modules.SWORD())

  # process file contents
  tmp_XmlNodeRoot = tmp_Mods.Process(tmp_FileContents)

  tmp_InputFileName = tmp_Args.OptInput.decode('utf-8')
  tmp_OutputFolderName = tmp_Args.OptOutput.decode('utf-8')

  # get file name
  tmp_FileNameWithExt = os.path.basename(tmp_InputFileName)
  tmp_FileName = os.path.splitext(tmp_FileNameWithExt)[0]
  tmp_OutputFileName = os.path.join(tmp_OutputFolderName, tmp_FileName + u'.xml')

  print 'Write results to file: "' + tmp_OutputFileName.encode('utf-8') + '"'

  # store xml tree to output file
  with codecs.open(tmp_OutputFileName, 'w+', 'utf-8') as tmp_File:
    tmp_File.write(ET.tostring(tmp_XmlNodeRoot))

if __name__ == "__main__":
  main()

