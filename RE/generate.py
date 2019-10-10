# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import argparse, os, sys
import xml.etree.ElementTree as ET
from modules import Generators

# ================================================================ #
# configuration
# ================================================================ #

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

  # sanity check
  if not os.path.exists(tmp_Args.OptOutput):
    sys.exit(os.EX_OSFILE)

  print 'Processing file: "' + tmp_Args.OptInput + '"'

  # create instance of generators
  tmp_Gens = Generators.Generators()

  # register generators
  tmp_Gens.Register(Generators.TXT())
  tmp_Gens.Register(Generators.HTML())
  tmp_Gens.Register(Generators.FODT())
  tmp_Gens.Register(Generators.PDF())

  # get input file name
  tmp_InputFileName = tmp_Args.OptInput.decode('utf-8')

  # get output folder name
  tmp_OutputFolderName = tmp_Args.OptOutput.decode('utf-8')

  # load xml tree
  tmp_XmlNodeRoot = ET.parse(tmp_InputFileName)

  # get file name
  tmp_FileNameWithExt = os.path.basename(tmp_InputFileName)
  tmp_FileName = os.path.splitext(tmp_FileNameWithExt)[0]

  # process xml tree
  tmp_Gens.Process(tmp_FileName, tmp_XmlNodeRoot, tmp_OutputFolderName)

if __name__ == "__main__":
  main()

