# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, os, xml.etree.ElementTree as ET
from modules import config, Helpers, Modules

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
# configuration of generator: TXT
# ================================================================ #
cfg_ChrGenTXTQuote = config.GenTXTQuoteChr
cfg_StrGenTXTVersetDelimiter = config.GenTXTVersetDelimiterStr

# ================================================================ #
# configuration of generator: TEX
# ================================================================ #
cfg_StrGenTEXVersetDelimiter = config.GenTEXVersetDelimiterStr

# ================================================================ #
# implementation of generator interface
# ================================================================ #
class iGenerator(object):
  atr_Modules = {
    'Scripture' : Modules.Scripture(),
    'Sectioning' : Modules.Sectioning(),
    'Translations' : Modules.Translations()
  }

  def __init__(self):
    # assign file name
    self.atr_FileName = u''

    # set list of Scripture extracts to be studied
    self.atr_ScriptureExtracts = []

    # clear sectioning levels
    self.atr_SectioningLevels = [0 for tmp_Level in Modules.Sectioning.atr_Levels.items()]

    # create token container
    self.atr_Tokens = Helpers.Tokens()

    # set default verset delimiter
    self.atr_VersetDelimiter = u' (...) '

    # set default verset opening quote
    self.atr_VersetOpeningQuote = u'"'

    # set default verset closing quote
    self.atr_VersetClosingQuote = u'"'

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def GetOrigin(self, arg_Origin):
    return u'(' + arg_Origin + u')'

  def GetTagName(self, arg_Namespace, arg_TagName):
    self.GetXmlNamespaces['sectioning']

  def HandleTagUnknown(self, arg_XmlNode):
    raise Exception

  def HandleTagText(self, arg_XmlNode):
    return arg_XmlNode.text

  def HandleTagScriptureExtract(self, arg_XmlNode, arg_IncludeOrigin = True):
    tmp_Contents = []
    tmp_ScriptureExtract = []
    tmp_AtrTranslationName = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['TranslationName'], None)
    tmp_AtrNormalized = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Normalized'], None)
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    # sanity check
    if tmp_AtrNormalized is None or tmp_AtrOrigin is None:
      raise Exception

    tmp_Normalized = self.GetOrigin(tmp_AtrNormalized)
    tmp_Origin = self.GetOrigin(tmp_AtrOrigin)

    # sanity check
    if tmp_AtrTranslationName is None:
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

      tmp_ScriptureExtract.append(u' '.join(tmp_Translation.GetVersetByReference(tmp_VersetRef)))

    tmp_Contents.append(self.atr_VersetOpeningQuote + self.atr_VersetDelimiter.join(filter(None, tmp_ScriptureExtract)) + self.atr_VersetClosingQuote)

    if arg_IncludeOrigin:
      tmp_Contents.append(tmp_Origin)

    # add Scripture extract to the list of Scripture extracts to be studied
    if tmp_Normalized not in self.atr_ScriptureExtracts:
      self.atr_ScriptureExtracts.append(tmp_Normalized)

    return u' '.join(filter(None, tmp_Contents))

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

    tmp_Contents.append(u'.'.join(tmp_Prefixes))
    tmp_Contents.append(tmp_AtrTitle)

    return u' '.join(filter(None, tmp_Contents))

  def HandleTagObject(self, arg_XmlNode):
    tmp_Contents = []

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(
        {
          u'text' : self.HandleTagText,
          iGenerator.atr_Modules['Scripture'].GetXmlTagName('extract') : self.HandleTagScriptureExtract
        }.get(tmp_XmlNodeChild.tag, self.HandleTagUnknown)(tmp_XmlNodeChild)
      )

    return u''.join(filter(None, tmp_Contents))

  def HandleTag(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(
      {
        u'object' : self.HandleTagObject,
        iGenerator.atr_Modules['Sectioning'].GetXmlTagName(u'section') : self.HandleTagSectioningSection,
      }.get(arg_XmlNode.tag, self.HandleTagUnknown)(arg_XmlNode)
    )

    return u'\n'.join(filter(None, tmp_Contents))

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    tmp_XmlNodeDocument = arg_XmlNodeRoot.find(iGenerator.atr_Modules['Sectioning'].GetXmlTagName(u'section'), iGenerator.atr_Modules['Sectioning'].GetXmlNamespace())

    if tmp_XmlNodeDocument is None:
      raise Exception

    self.atr_FileName = arg_FileName

    tmp_Contents = self.HandleTag(tmp_XmlNodeDocument)

    for tmp_TokenName, tmp_Token in self.atr_Tokens.Items():
      tmp_Contents = tmp_Contents.replace(str(tmp_Token), tmp_Token.GetText())

    self.WriteContents(arg_FileName, tmp_Contents, arg_OutputFolderName)

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

  def GetName(self):
    return self.__class__.__name__.lower()
  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(super(TXT, self).HandleTagSectioningSection(arg_XmlNode))

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    return u'\n'.join(filter(None, tmp_Contents))

# ================================================================ #
# implementation of generator: HTM
# ================================================================ #
# generator
class HTM(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return self.__class__.__name__.lower()

  def HandleTagObject(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(u'<p>' + super(HTM, self).HandleTagObject(arg_XmlNode) + u'</p>')

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagScriptureExtract(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    # sanity check
    if tmp_AtrOrigin is None:
      raise Exception

    tmp_Origin = self.GetOrigin(tmp_AtrOrigin)

    tmp_ScriptureExtract = super(HTM, self).HandleTagScriptureExtract(arg_XmlNode, False)

    if tmp_AtrInline == u'false':
      tmp_Contents.append(u'<p class="css_bible_text">' + tmp_ScriptureExtract + u'</p>')
      tmp_Contents.append(u'<p class="css_bible_origin">' + tmp_Origin + u'</p>')
    else:
      tmp_Contents.append(tmp_ScriptureExtract + u' ' + tmp_Origin)

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)
    tmp_TokScriptureExtracts = None

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)
    
    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      # create token for Scripture extracts to be studied
      tmp_TokScriptureExtracts = self.atr_Tokens.Create(u'ScriptureExtracts')

      if tmp_AtrTitle is None:
        tmp_AtrTitle = self.atr_FileName

      tmp_Contents.append(u'<html>')
      tmp_Contents.append(u'<head>')
      tmp_Contents.append(u'<title>' + tmp_AtrTitle + u'</title>')
      tmp_Contents.append(u'<link rel="stylesheet" type="text/css" href="styles/default.css" />')
      tmp_Contents.append(u'</head>')
      tmp_Contents.append(u'<body>')
      tmp_Contents.append(u'<p class="css_title">' + tmp_AtrTitle + u'</p>')
      tmp_Contents.append(u'<p class="css_lines"><b>Wersety do studium:</b> ' + str(tmp_TokScriptureExtracts) + u'</p>')
    else:
      if tmp_AtrTitle is None:
        tmp_AtrTitle = u''

      tmp_Contents.append(u'<section>')
      tmp_Contents.append(u'<h1>' + super(HTM, self).HandleTagSectioningSection(arg_XmlNode) + u'</h1>')

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(u'</body>')
      tmp_Contents.append(u'</html>')

      if tmp_TokScriptureExtracts is not None:
        tmp_TokScriptureExtracts.SetText(u', '.join(self.atr_ScriptureExtracts))
    else:
      tmp_Contents.append(u'</section>')

    return u'\n'.join(filter(None, tmp_Contents))

# ================================================================ #
# implementation of generator: FODT
# ================================================================ #
# generator
class FODT(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def HandleTagScriptureExtract(self, arg_XmlNode):
    return u''

  def HandleTagSectioningSection(self, arg_XmlNode):
    return u''

  def GetName(self):
    return self.__class__.__name__.lower()

# ================================================================ #
# implementation of generator: PDF
# ================================================================ #
# generator
class PDF(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def HandleTagScriptureExtract(self, arg_XmlNode):
    return u''

  def HandleTagSectioningSection(self, arg_XmlNode):
    return u''

  def GetName(self):
    return self.__class__.__name__.lower()

# ================================================================ #
# implementation of generator: TEX
# ================================================================ #
# generator
class TEX(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

    # overwrite verset delimiter
    self.atr_VersetDelimiter = cfg_StrGenTEXVersetDelimiter

    # set default verset opening quote
    self.atr_VersetOpeningQuote = u',,'

    # set default verset closing quote
    self.atr_VersetClosingQuote = u'\'\''

  def GetName(self):
    return self.__class__.__name__.lower()

  def GetOrigin(self, arg_Origin):
    return u'\\mbox{(' + arg_Origin + u')}'

  def HandleTagObject(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(u'\\paragraph{}')
    tmp_Contents.append(super(TEX, self).HandleTagObject(arg_XmlNode))

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagScriptureExtract(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    # sanity check
    if tmp_AtrOrigin is None:
      raise Exception

    tmp_Origin = self.GetOrigin(tmp_AtrOrigin)

    tmp_ScriptureExtract = super(TEX, self).HandleTagScriptureExtract(arg_XmlNode, False)

    if tmp_AtrInline == u'false':
      tmp_Contents.append(u'\\begin{quote}')

    tmp_Contents.append(tmp_ScriptureExtract + u' ' + tmp_Origin)

    if tmp_AtrInline == u'false':
      tmp_Contents.append(u'\\end{quote}')

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)
    tmp_TokScriptureExtracts = None

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)
    
    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      # create token for Scripture extracts to be studied
      tmp_TokScriptureExtracts = self.atr_Tokens.Create(u'ScriptureExtracts')

      tmp_Contents.append(u'\\documentclass[10pt,a4paper,oneside]{article}')
      tmp_Contents.append(u'\\usepackage[utf8]{inputenc}')
      tmp_Contents.append(u'\\usepackage{polski}')
      tmp_Contents.append(u'\\usepackage[polish]{babel}')
      tmp_Contents.append(u'\\usepackage[margin=0.5in,bottom=0.75in]{geometry}')
      tmp_Contents.append(u'\\begin{document}')

      if tmp_AtrTitle is None:
        tmp_AtrTitle = self.atr_FileName

      tmp_Contents.append(u'\\centerline{\\textbf{\\MakeUppercase{' + tmp_AtrTitle + u'}}}')
      tmp_Contents.append(u'\\begin{center}')
      tmp_Contents.append(u'\\textbf{Wersety do studium:} ')
      tmp_Contents.append(str(tmp_TokScriptureExtracts))
      tmp_Contents.append(u'\\end{center}')
    else:
      tmp_Section = Modules.Sectioning.GetLevelName(tmp_Level)

      # sanity check
      if tmp_Section is None:
        raise Exception

      if tmp_AtrTitle is None:
        tmp_AtrTitle = u''

      tmp_Header = u'\\' + tmp_Section + u'{' + tmp_AtrTitle + u'}'
      tmp_Contents.append(tmp_Header)

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(u'\\end{document}')

      if tmp_TokScriptureExtracts is not None:
        tmp_TokScriptureExtracts.SetText(u', '.join(self.atr_ScriptureExtracts))

    return u'\n'.join(filter(None, tmp_Contents))

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

