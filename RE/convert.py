# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import argparse, codecs, os, sys, xml.etree.ElementTree as ET
from modules import Modules

# ================================================================ #
# configuration
# ================================================================ #
Cfg_ChrComment = u'#'

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

  # get input file name
  tmp_InputFileName = tmp_Args.OptInput.decode('utf-8')

  # get output folder name
  tmp_OutputFolderName = tmp_Args.OptOutput.decode('utf-8')

  # try to create output folder, if doesn't exist
  if os.path.exists(tmp_OutputFolderName):
    if not os.path.isdir(tmp_OutputFolderName):
      raise Exception
  else:
    os.mkdir(tmp_OutputFolderName)

  with codecs.open(tmp_Args.OptInput, 'r', 'utf-8') as tmp_File:
    tmp_FileContents = [tmp_Line.strip(u'\n') for tmp_Line in tmp_File.readlines()]

  # remove empty lines and comments
  tmp_FileContents[:] = [tmp_Line for tmp_Line in tmp_FileContents if len(tmp_Line) > 0 and tmp_Line.strip()[0] != Cfg_ChrComment]

  tmp_Modules = {
    'Document' : Modules.Document(),
    'Scripture' : Modules.Scripture(),
    'Sectioning' : Modules.Sectioning(),
    'SWORD' : Modules.SWORD(),
    'Translations' : Modules.Translations()
  }

  # create structure
  tmp_Modules['Document'].Register(tmp_Modules['Sectioning'])
  tmp_Modules['Scripture'].Register(tmp_Modules['Translations'])
  tmp_Modules['SWORD'].Register(tmp_Modules['Scripture'])

  # create instance of modules
  tmp_Mods = Modules.Modules()

  # register modules
  tmp_Mods.Register(tmp_Modules['SWORD'])
  tmp_Mods.Register(tmp_Modules['Document'])

  # process file contents
  tmp_XmlNodeRoot = tmp_Mods.Process(tmp_FileContents, tmp_Modules['Sectioning'].GetXmlTagName(u'section'))

  # get file name
  tmp_FileNameWithExt = os.path.basename(tmp_InputFileName)
  tmp_FileName = os.path.splitext(tmp_FileNameWithExt)[0]
  tmp_OutputFileName = os.path.join(tmp_OutputFolderName, tmp_FileName + u'.xml')

  # store xml tree to output file
  ET.ElementTree(tmp_XmlNodeRoot).write(
    tmp_OutputFileName,
    encoding = 'utf-8',
    xml_declaration = True,
    default_namespace = None,
    method = "xml"
  )

if __name__ == "__main__":
  main()

