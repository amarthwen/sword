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

# xml attributes: 'document:config'
cfg_XmlAttrDocumentConfig = config.DocumentConfigXmlAttribs

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

  print('Processing file: "{}"'.format(tmp_Args.OptInput))

  # get input file name
  tmp_InputFileName = tmp_Args.OptInput

  # get output folder name
  tmp_OutputFolderName = tmp_Args.OptOutput

  # try to create output folder, if doesn't exist
  if os.path.exists(tmp_OutputFolderName):
    if not os.path.isdir(tmp_OutputFolderName):
      raise Exception
  else:
    os.mkdir(tmp_OutputFolderName)

  # get file name
  tmp_InputFileNameWithExt = os.path.basename(tmp_InputFileName)
  tmp_InputFileName = os.path.splitext(tmp_InputFileNameWithExt)[0]
  tmp_OutputFileName = os.path.join(tmp_OutputFolderName, tmp_InputFileName + u'.xml')

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

  # add document configuration
  tmp_XmlNodeDocumentConfig = tmp_Modules['Document'].GetXmlNodeConfig(tmp_XmlNodeRoot)

  # add document body
  tmp_XmlNodeDocumentBody = tmp_Modules['Document'].GetXmlNodeBody(tmp_XmlNodeRoot)

  tmp_XmlNodeFirstParagraph = None
  tmp_XmlNodeFirstSection = None

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

    tmp_XmlNodeSection = tmp_XmlNodeParagraph.find(tmp_Modules['Sectioning'].GetXmlTagName(u'section'))
    if tmp_XmlNodeSection is not None and tmp_XmlNodeSection.get(cfg_XmlAttrSectioningSection['Level'], None) == '0':
      tmp_XmlNodeFirstParagraph = tmp_XmlNodeParagraph
      tmp_XmlNodeFirstSection = tmp_XmlNodeSection

      tmp_DocumentTitle = tmp_XmlNodeFirstSection.get(cfg_XmlAttrSectioningSection['Title'], None)
      if tmp_DocumentTitle is not None:
        tmp_Modules['Document'].SetTitle(tmp_DocumentTitle)
    else:
      if tmp_XmlNodeParagraph.find('*') is not None and tmp_Mods.GetModules():
        for tmp_Module in tmp_Mods.GetModules().values():
          tmp_Module.HandleObject(tmp_XmlNodeParagraph)

  # sanity check
  if tmp_XmlNodeFirstParagraph is None or tmp_XmlNodeFirstSection is None:
    raise Exception

  # add first paragraph (including section with level '0') to document body
  tmp_XmlNodeDocumentBody.append(tmp_XmlNodeFirstParagraph)

  # assign document title, if set
  tmp_DocumentTitle = tmp_Modules['Document'].GetTitle()
  if tmp_DocumentTitle is not None:
    tmp_XmlNodeDocumentConfig.set(cfg_XmlAttrDocumentConfig['Title'], tmp_DocumentTitle)

  # assign document subtitle, if set
  tmp_DocumentSubTitle = tmp_Modules['Document'].GetSubTitle()
  if tmp_DocumentSubTitle is not None:
    tmp_XmlNodeDocumentConfig.set(cfg_XmlAttrDocumentConfig['SubTitle'], tmp_DocumentSubTitle)

  # assign document emblem, if set
  tmp_DocumentEmblem = tmp_Modules['Document'].GetEmblem()
  if tmp_DocumentEmblem is not None:
    tmp_XmlNodeDocumentConfig.set(cfg_XmlAttrDocumentConfig['Emblem'], tmp_DocumentEmblem)

  # assign document quote, if set
  tmp_DocumentQuote = tmp_Modules['Document'].GetQuote()
  if tmp_DocumentQuote is not None:
    tmp_XmlNodeDocumentConfigQuote = tmp_Modules['Document'].GetXmlNodeConfigQuote(tmp_XmlNodeDocumentConfig, tmp_Modules['Scripture'].GetText(tmp_DocumentQuote))

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

