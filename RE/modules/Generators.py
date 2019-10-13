# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, os, xml.etree.ElementTree as ET
from modules import config, Modules

# ================================================================ #
# configuration
# ================================================================ #
# xml attributes: 'scripture:extract'
cfg_XmlAttrScriptureExtract = config.ScriptureExtractXmlAttribs

# xml attributes: 'scripture:extract/verset'
cfg_XmlAttrScriptureExtractVerset = config.ScriptureExtractVersetXmlAttribs

# xml attributes: 'sectioning:section'
cfg_XmlAttrSectioningSection = config.SectioningSectionXmlAttribs

# ================================================================ #
# configuration of generator TXT
# ================================================================ #
cfg_ChrGenTXTQuote = config.GenTXTQuoteChr
cfg_StrGenTXTVersetDelimiterStr = config.GenTXTVersetDelimiterStr

# ================================================================ #
# implementation of generator interface
# ================================================================ #
class iGenerator:
  def __init__(self):
    self.atr_Modules = {}

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def GetTagName(self, arg_Namespace, arg_TagName):
    self.GetXmlNamespaces['sectioning']

  def HandleTagUnknown(self, arg_XmlNode):
    # raise Exception
    return None

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    self.WriteContents(arg_FileName, u'Generated with generator: "' + self.GetName() + '"', arg_OutputFolderName)

  def Register(self, arg_Module):
    tmp_ModuleName = str(arg_Module)

    if tmp_ModuleName not in self.atr_Modules:
      self.atr_Modules[tmp_ModuleName] = arg_Module

  def GetXmlNamespaces(self):
    tmp_XmlNamespaces = {}

    for tmp_Module in self.atr_Modules.values():
      tmp_XmlNamespaces.update(tmp_Module.GetXmlNamespaces())

    return tmp_XmlNamespaces

  def WriteContents(self, arg_FileName, arg_Contents, arg_OutputFolderName):
    tmp_Name = self.GetName()

    tmp_OutputFolderName = os.path.join(arg_OutputFolderName, tmp_Name)
    tmp_OutputFileName = arg_FileName + u'.' + tmp_Name

    if os.path.exists(tmp_OutputFolderName):
      if not os.path.isdir(tmp_OutputFolderName):
        raise Exception
    else:
      os.mkdir(tmp_OutputFolderName)

    with codecs.open(os.path.join(tmp_OutputFolderName, tmp_OutputFileName), 'w+', 'utf-8') as tmp_File:
      tmp_File.write(arg_Contents)

# ================================================================ #
# implementation of generator: TXT
# ================================================================ #
# generator
class TXT(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

    self.atr_Modules = {
      'Scripture' : Modules.Scripture(),
      'Sectioning' : Modules.Sectioning(),
      'Translations' : Modules.Translations()
    }

    self.atr_SectioningLevels = [0 for tmp_Level in Modules.Sectioning.atr_Levels.items()]

  def GetName(self):
    return self.__class__.__name__.lower()

  def HandleTagText(self, arg_XmlNode):
    return arg_XmlNode.text

  def HandleTagScriptureExtract(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrTranslationName = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['TranslationName'], None)
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], None)
    tmp_Origin = u''

    # sanity check
    if tmp_AtrTranslationName is None:
      raise Exception

    # sanity check
    if tmp_AtrOrigin is None:
      raise Exception

    # get translation
    tmp_Translation = Modules.Translations.Get(tmp_AtrTranslationName)

    # sanity check
    if tmp_Translation is None:
      raise Exception

    # get versets contents
    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_VersetRef = tmp_XmlNodeChild.get(cfg_XmlAttrScriptureExtractVerset['Reference'], None)

      # sanity check
      if tmp_VersetRef is None:
        raise Exception

      tmp_Contents.append(u' '.join(tmp_Translation.GetVersetByReference(tmp_VersetRef)))

    # add extract origin if is not inlined
    if tmp_AtrInline is None or tmp_AtrInline.lower() == u'false':
      tmp_Origin = u' (' + tmp_AtrOrigin + u')'

    return cfg_ChrGenTXTQuote + cfg_StrGenTXTVersetDelimiterStr.join(filter(None, tmp_Contents)) + cfg_ChrGenTXTQuote + tmp_Origin

  def HandleTagObject(self, arg_XmlNode):
    tmp_Contents = []

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(
        {
          'text' : self.HandleTagText,
          self.atr_Modules['Scripture'].GetXmlTagName('extract') : self.HandleTagScriptureExtract
        }.get(tmp_XmlNodeChild.tag, self.HandleTagUnknown)(tmp_XmlNodeChild)
      )

    return u''.join(filter(None, tmp_Contents))

  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)

    # increase current level
    self.atr_SectioningLevels[tmp_Level] = self.atr_SectioningLevels[tmp_Level] + 1

    # clear all levels below current one
    for tmp_SectioningLevel in Modules.Sectioning.atr_Levels.values():
      if tmp_SectioningLevel > tmp_Level:
        self.atr_SectioningLevels[tmp_SectioningLevel] = 0

    tmp_Prefixes = []
    for tmp_SectioningLevel in self.atr_SectioningLevels[1:]:
      if tmp_SectioningLevel > 0:
        tmp_Prefixes.append(str(tmp_SectioningLevel))
      else:
        break

    tmp_Header = u'.'.join(tmp_Prefixes)

    if tmp_AtrTitle is not None:
      if tmp_Level > 0:
        tmp_Header = tmp_Header + u'. '
      tmp_Header = tmp_Header + tmp_AtrTitle

    tmp_Contents.append(tmp_Header)

    return u''.join(filter(None, tmp_Contents))

  def HandleTag(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(
      {
        'object' : self.HandleTagObject,
        self.atr_Modules['Sectioning'].GetXmlTagName(u'section') : self.HandleTagSectioningSection,
      }.get(arg_XmlNode.tag, self.HandleTagUnknown)(arg_XmlNode)
    )

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    return u'\n'.join(filter(None, tmp_Contents))

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    tmp_XmlNamespaces = self.GetXmlNamespaces()
    tmp_XmlNodeDocument = arg_XmlNodeRoot.find(self.atr_Modules['Sectioning'].GetXmlTagName(u'section'), tmp_XmlNamespaces)

    if tmp_XmlNodeDocument is None:
      raise Exception

    tmp_Contents = self.HandleTag(tmp_XmlNodeDocument)

    self.WriteContents(arg_FileName, tmp_Contents, arg_OutputFolderName)

# ================================================================ #
# implementation of generator: HTML
# ================================================================ #
# generator
class HTML(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return self.__class__.__name__.lower()

# ================================================================ #
# implementation of generator: FODT
# ================================================================ #
# generator
class FODT(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return self.__class__.__name__.lower()

# ================================================================ #
# implementation of generator: PDF
# ================================================================ #
# generator
class PDF(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return self.__class__.__name__.lower()

# ================================================================ #
# implementation of generators container
# ================================================================ #
# container
class Generators:
  def __init__(self):
    self.atr_Generators = {}

  def Register(self, arg_Generator):
    tmp_GeneratorName = str(arg_Generator)

    if tmp_GeneratorName not in self.atr_Generators:
      self.atr_Generators[tmp_GeneratorName] = arg_Generator

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    for tmp_Generator in self.atr_Generators.values():
      tmp_Contents = tmp_Generator.Process(arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName)

