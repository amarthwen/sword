# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import argparse, codecs, os, sys, xml.etree.ElementTree as ET
from modules import config, Helpers, Modules

# ================================================================ #
# configuration
# ================================================================ #
Cfg_ChrComment = u'#'

# xml attributes: 'sectioning:section'
cfg_XmlAttrSectioningSection = config.SectioningSectionXmlAttribs

# paragraph name
cfg_StrParagraphName = config.ParagraphName

# text name
cfg_StrTextName = config.TextName

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
    'Object' : Modules.Object(),
    'Sectioning' : Modules.Sectioning(),
    'SWORD' : Modules.SWORD(),
    'Translations' : Modules.Translations()
  }

  # create structure
  tmp_Modules['Document'].Register(tmp_Modules['Sectioning'])
  tmp_Modules['Document'].Register(tmp_Modules['Object'])
  tmp_Modules['Scripture'].Register(tmp_Modules['Translations'])
  tmp_Modules['SWORD'].Register(tmp_Modules['Scripture'])

  # create instance of modules
  tmp_Mods = Modules.Modules()

  # register modules
  tmp_Mods.Register(tmp_Modules['SWORD'])
  tmp_Mods.Register(tmp_Modules['Document'])

  # process file contents
  tmp_XmlNodeRoot = ET.Element(tmp_Modules['Document'].GetXmlTagName(u'document'))
  tmp_XmlNodeDocumentBody = ET.SubElement(tmp_XmlNodeRoot, tmp_Modules['Document'].GetXmlTagName(u'body'))

  # process file contents
  for tmp_Line in tmp_FileContents:
    tmp_XmlNodeParagraph = ET.Element(tmp_Modules['Object'].GetXmlTagName(cfg_StrParagraphName))
    # tmp_XmlNodeParagraph = ET.Element(cfg_StrParagraphName)
    tmp_Items = Helpers.Entry(tmp_Line).GetItems()

    for tmp_Item in tmp_Items:
      tmp_Module = None

      if tmp_Mods.GetModules():
        try:
          tmp_Module = tmp_Mods.GetModules().get(tmp_Item['elements'][0], None)
        except:
          tmp_Module = None

      if tmp_Module is not None:
        tmp_XmlNodeChild = tmp_Module.Process(tmp_Item['elements'][1:], tmp_Item['params'])
        if tmp_XmlNodeChild is not None:
          tmp_XmlNodeParagraph.append(tmp_XmlNodeChild)
      else:
        # regular text
        tmp_XmlNodeText = ET.SubElement(tmp_XmlNodeParagraph, tmp_Modules['Object'].GetXmlTagName(cfg_StrTextName))
        # tmp_XmlNodeText = ET.SubElement(tmp_XmlNodeParagraph, cfg_StrTextName)

        try:
          tmp_XmlNodeText.text = tmp_Item['text']
        except:
          tmp_XmlNodeText.text = tmp_Item

    tmp_XmlNodeDocument = tmp_XmlNodeParagraph.find(tmp_Modules['Sectioning'].GetXmlTagName(u'section'))
    if tmp_XmlNodeDocument is not None and tmp_XmlNodeDocument.get(cfg_XmlAttrSectioningSection['Level'], None) == '0':
      tmp_XmlNodeDocumentBody.append(tmp_XmlNodeParagraph)
    else:
      if tmp_XmlNodeParagraph.find('*') is not None and tmp_Mods.GetModules():
        for tmp_Module in tmp_Mods.GetModules().values():
          tmp_Module.HandleObject(tmp_XmlNodeParagraph)

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

