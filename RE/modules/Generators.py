# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, os, xml.etree.ElementTree as ET
from modules import config, Helpers, Modules

# ================================================================ #
# configuration
# ================================================================ #
# generators temporary directory
cfg_DirGenTmp = config.GenTmpDir

# xml attributes: 'scripture:extract'
cfg_XmlAttrScriptureExtract = config.ScriptureExtractXmlAttribs

# xml attributes: 'scripture:extract/verset'
cfg_XmlAttrScriptureExtractVerset = config.ScriptureExtractVersetXmlAttribs

# xml attributes: 'sectioning:section'
cfg_XmlAttrSectioningSection = config.SectioningSectionXmlAttribs

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

    # set xml namespaces
    self.atr_XmlNamespaces = {}

    # set list of Scripture extracts to be studied
    self.atr_ScriptureExtracts = []

    # clear sectioning levels
    self.atr_SectioningLevels = [0 for tmp_Level in Modules.Sectioning.atr_Levels.values()]

    # set current sectioning level
    self.atr_SectioningLevel = -1

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

  def GetXmlTagName(self, arg_TagName):
    tmp_Elements = arg_TagName.split(u':')
    tmp_XmlTagName = u''

    # sanity check
    if len(tmp_Elements) < 1 or len(tmp_Elements) > 2:
      raise Exception

    if len(tmp_Elements) == 2:
      tmp_URI = self.atr_XmlNamespaces.get(tmp_Elements[0], None)

      # sanity check
      if tmp_URI is None:
        raise Exception

      tmp_XmlTagName = u'{' + tmp_URI + u'}' + tmp_Elements[1]
    else:
      tmp_XmlTagName = tmp_Elements[0]

    return tmp_XmlTagName

  def RegisterXmlNamespaces(self, arg_XmlNamespaces):
    for tmp_XmlNamespace in arg_XmlNamespaces.items():
      self.atr_XmlNamespaces[tmp_XmlNamespace[0]] = tmp_XmlNamespace[1]
      ET.register_namespace(tmp_XmlNamespace[0], tmp_XmlNamespace[1])

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

  def HandleTagSectioningSection(self, arg_XmlNode, arg_IncludePrefix = True):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level

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

    if arg_IncludePrefix:
      tmp_Contents.append(u'.'.join(tmp_Prefixes))

    tmp_Contents.append(tmp_AtrTitle)

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

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

  def GetOrigin(self, arg_Origin):
    return u'(' + arg_Origin.replace(u' ', u'&nbsp;') + u')'

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
    
    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level

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

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

    return u'\n'.join(filter(None, tmp_Contents))

# ================================================================ #
# implementation of generator: FODT
# ================================================================ #
# generator
class FODT(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

    # set default verset opening quote
    self.atr_VersetOpeningQuote = u'„'

    # set default verset closing quote
    self.atr_VersetClosingQuote = u'”'

    self.RegisterXmlNamespaces({
      'office' : 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
      'style' : 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
      'text' : 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
      'table' : 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
      'draw' : 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
      'fo' : 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0',
      'xlink' : 'http://www.w3.org/1999/xlink',
      'dc' : 'http://purl.org/dc/elements/1.1/',
      'meta' : 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0',
      'number' : 'urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0',
      'svg' : 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0',
      'chart' : 'urn:oasis:names:tc:opendocument:xmlns:chart:1.0',
      'dr3d' : 'urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0',
      'math' : 'http://www.w3.org/1998/Math/MathML',
      'form' : 'urn:oasis:names:tc:opendocument:xmlns:form:1.0',
      'script' : 'urn:oasis:names:tc:opendocument:xmlns:script:1.0',
      'config' : 'urn:oasis:names:tc:opendocument:xmlns:config:1.0',
      'ooo' : 'http://openoffice.org/2004/office',
      'ooow' : 'http://openoffice.org/2004/writer',
      'oooc' : 'http://openoffice.org/2004/calc',
      'dom' : 'http://www.w3.org/2001/xml-events',
      'xforms' : 'http://www.w3.org/2002/xforms',
      'xsd' : 'http://www.w3.org/2001/XMLSchema',
      'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
      'rpt' : 'http://openoffice.org/2005/report',
      'of' : 'urn:oasis:names:tc:opendocument:xmlns:of:1.2',
      'xhtml' : 'http://www.w3.org/1999/xhtml',
      'grddl' : 'http://www.w3.org/2003/g/data-view#',
      'officeooo' : 'http://openoffice.org/2009/office',
      'tableooo' : 'http://openoffice.org/2009/table',
      'drawooo' : 'http://openoffice.org/2010/draw',
      'calcext' : 'urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0',
      'loext' : 'urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0',
      'field' : 'urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0',
      'formx' : 'urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0',
      'css3t' : 'http://www.w3.org/TR/css3-text/'
    })

    # create root node
    self.atr_XmlNodeRoot = ET.parse(os.path.join(cfg_DirGenTmp, self.GetName(), u'template.fodt')).getroot()

    # get office:text xml node
    tmp_XmlNodeOfficeText = self.atr_XmlNodeRoot.find(u'.//' + self.GetXmlTagName(u'office:text'))

    # sanity check
    if tmp_XmlNodeOfficeText is None:
      raise Exception

    # remove contents of office:text xml node
    tmp_XmlNodeOfficeText.clear()

    # remove contents of office:text xml node
    # for tmp_XmlNodeChild in tmp_XmlNodeOfficeText:
      # if tmp_XmlNodeChild.tag != self.GetXmlTagName(u'text:sequence-decls'):
        # tmp_XmlNodeOfficeText.remove(tmp_XmlNodeChild)

    # set pointer to currently used paragraph
    self.atr_XmlNodeParagraph = None

  def HandleTagText(self, arg_XmlNode):
    # sanity check
    if self.atr_XmlNodeParagraph is None:
      raise Exception

    if self.atr_XmlNodeParagraph.text is not None:
      self.atr_XmlNodeParagraph.text = self.atr_XmlNodeParagraph.text + arg_XmlNode.text
    else:
      self.atr_XmlNodeParagraph.text = arg_XmlNode.text

    return u''

  def HandleTagScriptureExtract(self, arg_XmlNode):
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    # sanity check
    if tmp_AtrOrigin is None:
      raise Exception

    tmp_Origin = self.GetOrigin(tmp_AtrOrigin)

    tmp_ScriptureExtract = super(FODT, self).HandleTagScriptureExtract(arg_XmlNode)

    # sanity check
    if self.atr_XmlNodeParagraph is None:
      raise Exception

    if tmp_AtrInline == u'false':
      # TODO: implement style for non-inlined Scripture extracts
      if self.atr_XmlNodeParagraph.text is not None:
        self.atr_XmlNodeParagraph.text = self.atr_XmlNodeParagraph.text + tmp_ScriptureExtract
      else:
        self.atr_XmlNodeParagraph.text = tmp_ScriptureExtract
    else:
      if self.atr_XmlNodeParagraph.text is not None:
        self.atr_XmlNodeParagraph.text = self.atr_XmlNodeParagraph.text + tmp_ScriptureExtract
      else:
        self.atr_XmlNodeParagraph.text = tmp_ScriptureExtract

    return u''

  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)
    tmp_TokScriptureExtracts = None
    tmp_XmlNodeRoot = None

    # clear pointer to currently used paragraph
    self.atr_XmlNodeParagraph = None

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)
    
    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level

    tmp_XmlNodeOfficeText = self.atr_XmlNodeRoot.find(u'.//' + self.GetXmlTagName(u'office:text'))

    # sanity check
    if tmp_XmlNodeOfficeText is None:
      raise Exception

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      # create token for Scripture extracts to be studied
      # tmp_TokScriptureExtracts = self.atr_Tokens.Create(u'ScriptureExtracts')

      if tmp_AtrTitle is None:
        tmp_AtrTitle = self.atr_FileName

      tmp_XmlNodeDcTitle = self.atr_XmlNodeRoot.find(u'.//' + self.GetXmlTagName(u'dc:title'))

      # sanity check
      if tmp_XmlNodeDcTitle is None:
        raise Exception

      tmp_XmlNodeDcTitle.text = tmp_AtrTitle

      tmp_XmlNodeTextP = ET.SubElement(tmp_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
      tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Title')
      tmp_XmlNodeTextP.text = tmp_AtrTitle
    else:
      if tmp_AtrTitle is None:
        tmp_AtrTitle = u''

      # add header
      tmp_XmlNodeTextH = ET.SubElement(tmp_XmlNodeOfficeText, self.GetXmlTagName(u'text:h'))
      tmp_XmlNodeTextH.set(self.GetXmlTagName(u'text:style-name'), u'Heading_20_' + str(tmp_Level))
      tmp_XmlNodeTextH.set(self.GetXmlTagName(u'text:outline-level'), str(tmp_Level))
      tmp_XmlNodeTextH.text = tmp_AtrTitle

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(ET.tostring(self.atr_XmlNodeRoot))

      # if tmp_TokScriptureExtracts is not None:
        # tmp_TokScriptureExtracts.SetText(u', '.join(self.atr_ScriptureExtracts))
    else:
      pass

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagObject(self, arg_XmlNode):
    tmp_XmlNodeOfficeText = self.atr_XmlNodeRoot.find(u'.//' + self.GetXmlTagName(u'office:text'))

    # sanity check
    if tmp_XmlNodeOfficeText is None:
      raise Exception

    # add paragraph
    tmp_XmlNodeTextP = ET.SubElement(tmp_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
    if self.atr_SectioningLevel > 0:
      tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Text_20_body')
    else:
      tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Standard')

    self.atr_XmlNodeParagraph = tmp_XmlNodeTextP

    return super(FODT, self).HandleTagObject(arg_XmlNode)

  def GetName(self):
    return self.__class__.__name__.lower()

  def WriteContents(self, arg_FileName, arg_Contents, arg_OutputFolderName):
    tmp_Name = self.GetName()

    tmp_OutputFolderName = os.path.join(arg_OutputFolderName, tmp_Name)
    tmp_OutputFileName = arg_FileName + u'.' + tmp_Name

    if os.path.exists(tmp_OutputFolderName):
      if not os.path.isdir(tmp_OutputFolderName):
        raise Exception
    else:
      os.mkdir(tmp_OutputFolderName)

    # store xml tree to output file
    ET.ElementTree(self.atr_XmlNodeRoot).write(
      os.path.join(tmp_OutputFolderName, tmp_OutputFileName),
      encoding = 'utf-8',
      xml_declaration = True,
      default_namespace = None,
      method = "xml"
    )

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
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    tmp_ScriptureExtract = super(TEX, self).HandleTagScriptureExtract(arg_XmlNode)

    if tmp_AtrInline == u'false':
      tmp_Contents.append(u'\\begin{quote}')

    tmp_Contents.append(tmp_ScriptureExtract)

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
    
    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      # create token for Scripture extracts to be studied
      tmp_TokScriptureExtracts = self.atr_Tokens.Create(u'ScriptureExtracts')

      if tmp_AtrTitle is None:
        tmp_AtrTitle = self.atr_FileName

      tmp_Contents.append(u'\\documentclass[10pt,a4paper,oneside]{article}')
      tmp_Contents.append(u'\\usepackage[utf8]{inputenc}')
      tmp_Contents.append(u'\\usepackage{polski}')
      tmp_Contents.append(u'\\usepackage[polish]{babel}')
      tmp_Contents.append(u'\\usepackage[margin=0.5in,bottom=0.75in]{geometry}')
      tmp_Contents.append(u'\\begin{document}')
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

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

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
      tmp_Generator.Process(arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName)

