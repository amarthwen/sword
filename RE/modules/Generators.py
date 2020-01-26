# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import base64, codecs, mimetypes, os, xml.etree.ElementTree as ET
from PIL import Image
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

# xml attributes: 'image:image'
cfg_XmlAttrObjectImage = config.ObjectImageXmlAttribs

# xml attributes: 'document:config'
cfg_XmlAttrDocumentConfig = config.DocumentConfigXmlAttribs

# paragraph name
cfg_StrParagraphName = config.ParagraphName

# image temporary directory
cfg_DirImagesTmp = config.ImagesTmpDir

# ================================================================ #
# implementation of generator interface
# ================================================================ #
class iGenerator(object):
  atr_Modules = {
    'Document' : Modules.Document(),
    'Object' : Modules.Object(),
    'Scripture' : Modules.Scripture(),
    'Sectioning' : Modules.Sectioning(),
    'Translations' : Modules.Translations()
  }

  def __init__(self):
    # assign file name
    self.atr_FileName = u''

    # set document title
    self.atr_DocumentTitle = None

    # set document subtitle
    self.atr_DocumentSubTitle = None

    # set document emblem
    self.atr_DocumentEmblem = None

    # set document quote
    self.atr_DocumentQuote = None

    # set xml namespaces
    self.atr_XmlNamespaces = {}

    # set list of Scripture extracts to be studied
    self.atr_ScriptureExtracts = []

    # clear sectioning levels
    self.atr_SectioningLevels = [0 for tmp_Level in Modules.Sectioning.atr_Levels.values()]

    # set current sectioning level
    self.atr_SectioningLevel = -1

    # set text paragraphs
    self.atr_TextParagraphPrev = None
    self.atr_TextParagraphCurr = None

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

  def HandleTagObjectText(self, arg_XmlNode):
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

      tmp_ScriptureExtract.append(u' '.join(tmp_Translation.GetVersetByReferenceRangeStr(tmp_VersetRef)))

    tmp_Contents.append(self.atr_VersetOpeningQuote + self.atr_VersetDelimiter.join(filter(None, tmp_ScriptureExtract)) + self.atr_VersetClosingQuote)

    if arg_IncludeOrigin:
      tmp_Contents.append(tmp_Origin)

    # add Scripture extract to the list of Scripture extracts to be studied
    if tmp_Normalized not in self.atr_ScriptureExtracts:
      self.atr_ScriptureExtracts.append(tmp_Normalized)

    return u' '.join(filter(None, tmp_Contents))

  def HandleTagObjectImage(self, arg_XmlNode):
    tmp_Contents = []

    return u''.join(filter(None, tmp_Contents))

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

    # set text paragraphs
    self.atr_TextParagraphPrev = None
    self.atr_TextParagraphCurr = None

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

    if tmp_AtrTitle is not None:
      if arg_IncludePrefix:
        tmp_Contents.append(u'.'.join(tmp_Prefixes))

      tmp_Contents.append(tmp_AtrTitle)

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

    return u' '.join(filter(None, tmp_Contents))

  def HandleTagObjectParagraph(self, arg_XmlNode):
    tmp_Contents = []

    for tmp_XmlNodeChild in arg_XmlNode:
      self.atr_TextParagraphPrev = self.atr_TextParagraphCurr
      self.atr_TextParagraphCurr = None

      tmp_Contents.append(
        {
          iGenerator.atr_Modules['Object'].GetXmlTagName(u'text') : self.HandleTagObjectText,
          iGenerator.atr_Modules['Object'].GetXmlTagName(u'image') : self.HandleTagObjectImage,
          iGenerator.atr_Modules['Scripture'].GetXmlTagName(u'extract') : self.HandleTagScriptureExtract
        }.get(tmp_XmlNodeChild.tag, self.HandleTagUnknown)(tmp_XmlNodeChild)
      )

    # set text paragraphs
    self.atr_TextParagraphPrev = None
    self.atr_TextParagraphCurr = None

    return u''.join(filter(None, tmp_Contents))

  def HandleTag(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(
      {
        iGenerator.atr_Modules['Object'].GetXmlTagName(cfg_StrParagraphName) : self.HandleTagObjectParagraph,
        iGenerator.atr_Modules['Sectioning'].GetXmlTagName(u'section') : self.HandleTagSectioningSection
      }.get(arg_XmlNode.tag, self.HandleTagUnknown)(arg_XmlNode)
    )

    return u'\n'.join(filter(None, tmp_Contents))

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    tmp_XmlNodeDocument = arg_XmlNodeRoot.find(u'.//' + iGenerator.atr_Modules['Sectioning'].GetXmlTagName(u'section'), iGenerator.atr_Modules['Sectioning'].GetXmlNamespace())
    tmp_XmlNodeDocumentConfig = arg_XmlNodeRoot.find(u'.//' + iGenerator.atr_Modules['Document'].GetXmlTagName(u'config'), iGenerator.atr_Modules['Document'].GetXmlNamespace())

    if tmp_XmlNodeDocument is None or tmp_XmlNodeDocumentConfig is None:
      raise Exception

    tmp_XmlNodeDocumentConfigQuote = tmp_XmlNodeDocumentConfig.find(u'.//' + iGenerator.atr_Modules['Document'].GetXmlTagName(u'quote'), iGenerator.atr_Modules['Document'].GetXmlNamespace())

    self.atr_FileName = arg_FileName
    self.atr_DocumentTitle = tmp_XmlNodeDocumentConfig.get(cfg_XmlAttrDocumentConfig['Title'], arg_FileName)
    self.atr_DocumentSubTitle = tmp_XmlNodeDocumentConfig.get(cfg_XmlAttrDocumentConfig['SubTitle'], None)
    self.atr_DocumentEmblem = tmp_XmlNodeDocumentConfig.get(cfg_XmlAttrDocumentConfig['Emblem'], None)
    if tmp_XmlNodeDocumentConfigQuote is not None:
      for tmp_XmlNodeDocumentConfigQuoteChild in tmp_XmlNodeDocumentConfigQuote:
        self.atr_DocumentQuote = iGenerator.HandleTagScriptureExtract(self, tmp_XmlNodeDocumentConfigQuoteChild)

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

  def HandleTagObjectParagraph(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(u'<p>' + super(HTM, self).HandleTagObjectParagraph(arg_XmlNode) + u'</p>')

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
      tmp_Contents.append(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8">')
      tmp_Contents.append(u'<head>')
      tmp_Contents.append(u'<title>' + tmp_AtrTitle + u'</title>')
      tmp_Contents.append(u'<link rel="stylesheet" type="text/css" href="styles/default.css" />')
      tmp_Contents.append(u'</head>')
      tmp_Contents.append(u'<body>')
      tmp_Contents.append(u'<p class="css_title">' + tmp_AtrTitle + u'</p>')

      if self.atr_DocumentEmblem is not None and len(self.atr_DocumentEmblem) > 0:
        tmp_DocumentEmblem = os.path.join(u'..', u'..', cfg_DirImagesTmp, self.atr_DocumentEmblem)

        tmp_Contents.append(u'<center><img class="css_emblem" alt="' + self.atr_DocumentEmblem + u'" src="' + tmp_DocumentEmblem + u'"></center>')

      if self.atr_DocumentSubTitle is not None and len(self.atr_DocumentSubTitle) > 0:
        tmp_Contents.append(u'<p class="css_subtitle">' + self.atr_DocumentSubTitle + u'</p>')

      if self.atr_DocumentQuote is not None and len(self.atr_DocumentQuote) > 0:
        tmp_Contents.append(u'<p class="css_quote">' + self.atr_DocumentQuote + u'</p>')

      tmp_Contents.append(str(tmp_TokScriptureExtracts))
    else:
      if tmp_AtrTitle is not None:
        tmp_Contents.append(u'<section>')
        tmp_Contents.append(u'<h1>' + super(HTM, self).HandleTagSectioningSection(arg_XmlNode) + u'</h1>')

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(u'</body>')
      tmp_Contents.append(u'</html>')

      if tmp_TokScriptureExtracts is not None:
        if len(self.atr_ScriptureExtracts) > 0:
          tmp_TokScriptureExtracts.SetText(u'<p class="css_lines"><b>Wersety do studium:</b> ' + u', '.join(self.atr_ScriptureExtracts) + u'</p>')
        else:
          tmp_TokScriptureExtracts.SetText(u'')
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

    # register ODF namespaces
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

    # assign xml node office:text
    self.atr_XmlNodeOfficeText = tmp_XmlNodeOfficeText

    # remove contents of office:text xml node
    self.atr_XmlNodeOfficeText.clear()

    tmp_XmlNodeTextSequenceDecls = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:sequence-decls'))

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Illustration')

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Table')

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Text')

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Drawing')

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Figure')

    tmp_XmlNodeTextSequenceDecl = ET.SubElement(tmp_XmlNodeTextSequenceDecls, self.GetXmlTagName(u'text:sequence-decl'))
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:display-outline-level'), u'0')
    tmp_XmlNodeTextSequenceDecl.set(self.GetXmlTagName(u'text:name'), u'Obraz')

    # initialize number of images
    self.atr_ImageCounter = 0

    # initialize number of images
    self.atr_ImageCaptionCounter = 0

    # init MIME types
    mimetypes.init()

  def AddTextToCurrentParagraph(self, arg_Text):
    # print u'AddTextToCurrentParagraph'
    # print self.atr_TextParagraphPrev
    # print self.atr_TextParagraphCurr
    # print arg_Text
    if self.atr_TextParagraphPrev is not None:
      self.atr_TextParagraphPrev.text = filter(None, u''.join([self.atr_TextParagraphPrev.text, arg_Text]))
      self.atr_TextParagraphCurr = self.atr_TextParagraphPrev
    else:
      tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))

      if self.atr_SectioningLevel > 0:
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Text_20_body')
      else:
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Standard')

      tmp_XmlNodeTextP.text = arg_Text

      self.atr_TextParagraphCurr = tmp_XmlNodeTextP

  def AddImageCaption(self, arg_XmlNode, arg_Caption):
    tmp_XmlNodeTextSequence = ET.SubElement(arg_XmlNode, self.GetXmlTagName(u'text:sequence'))
    tmp_XmlNodeTextSequence.set(self.GetXmlTagName(u'text:ref-name'), u'refFigure' + str(self.atr_ImageCaptionCounter))
    tmp_XmlNodeTextSequence.set(self.GetXmlTagName(u'text:name'), u'Figure')
    tmp_XmlNodeTextSequence.set(self.GetXmlTagName(u'text:formula'), u'ooow:Figure+1')
    tmp_XmlNodeTextSequence.set(self.GetXmlTagName(u'style:num-format'), u'1')
    tmp_XmlNodeTextSequence.text = str(self.atr_ImageCounter + 1)
    tmp_XmlNodeTextSequence.tail = u': ' + arg_Caption

    self.atr_ImageCaptionCounter = self.atr_ImageCaptionCounter + 1

  def AddImage(self, arg_XmlNode, arg_Name, arg_Caption = None):
    tmp_FileNameFull = os.path.join(cfg_DirImagesTmp, arg_Name)
    # sanity check
    if not os.path.exists(tmp_FileNameFull):
      raise Exception

    tmp_FileName, tmp_FileExtension = os.path.splitext(arg_Name)

    # get MIME type
    tmp_FileMimeType = mimetypes.types_map.get(tmp_FileExtension, None)

    # sanity check
    if tmp_FileMimeType is None:
      raise Exception

    # get encoded file contents
    with open(tmp_FileNameFull, "rb") as tmp_File:
      tmp_FileContentsBase64 = base64.b64encode(tmp_File.read())

    tmp_PILImage = Image.open(tmp_FileNameFull)
    tmp_PILImageDPI = tmp_PILImage.info.get('dpi', None)

    # sanity check
    if tmp_PILImageDPI is None:
      raise Exception

    tmp_PILImageWidth = 2.54 * tmp_PILImage.width / tmp_PILImageDPI[0]
    tmp_PILImageHeight = 2.54 * tmp_PILImage.height / tmp_PILImageDPI[1]

    tmp_XmlNodeTextP_001 = ET.SubElement(arg_XmlNode, self.GetXmlTagName(u'text:p'))
    tmp_XmlNodeTextP_001.set(self.GetXmlTagName(u'text:style-name'), u'Figure')

    tmp_XmlNodeDrawFrame_001 = ET.SubElement(tmp_XmlNodeTextP_001, self.GetXmlTagName(u'draw:frame'))
    tmp_XmlNodeDrawFrame_001.set(self.GetXmlTagName(u'draw:style-name'), u'fr1')
    tmp_XmlNodeDrawFrame_001.set(self.GetXmlTagName(u'draw:name'), u'Frame' + str(self.GetImageCounter() + 1))
    tmp_XmlNodeDrawFrame_001.set(self.GetXmlTagName(u'text:anchor-type'), u'as-char')
    tmp_XmlNodeDrawFrame_001.set(self.GetXmlTagName(u'svg:width'), str(tmp_PILImageWidth) + u'cm')
    tmp_XmlNodeDrawFrame_001.set(self.GetXmlTagName(u'draw:z-index'), u'0')

    tmp_XmlNodeDrawTextBox = ET.SubElement(tmp_XmlNodeDrawFrame_001, self.GetXmlTagName(u'draw:text-box'))
    tmp_XmlNodeDrawTextBox.set(self.GetXmlTagName(u'fo:min-height'), str(tmp_PILImageHeight) + u'cm')

    tmp_XmlNodeTextP_002 = ET.SubElement(tmp_XmlNodeDrawTextBox, self.GetXmlTagName(u'text:p'))
    tmp_XmlNodeTextP_002.set(self.GetXmlTagName(u'text:style-name'), u'Figure')

    tmp_XmlNodeDrawFrame_002 = ET.SubElement(tmp_XmlNodeTextP_002, self.GetXmlTagName(u'draw:frame'))
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'draw:style-name'), u'fr2')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'draw:name'), u'Image' + str(self.GetImageCounter() + 1))
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'text:anchor-type'), u'as-char')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'svg:width'), str(tmp_PILImageWidth) + u'cm')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'style:rel-width'), u'100%')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'svg:height'), str(tmp_PILImageHeight) + u'cm')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'style:rel-height'), u'scale')
    tmp_XmlNodeDrawFrame_002.set(self.GetXmlTagName(u'draw:z-index'), u'1')

    tmp_XmlNodeDrawImage = ET.SubElement(tmp_XmlNodeDrawFrame_002, self.GetXmlTagName(u'draw:image'))
    tmp_XmlNodeDrawImage.set(self.GetXmlTagName(u'loext:mime-type'), tmp_FileMimeType)

    tmp_XmlNodeOfficeBinaryData = ET.SubElement(tmp_XmlNodeDrawImage, self.GetXmlTagName(u'office:binary-data'))
    tmp_XmlNodeOfficeBinaryData.text = tmp_FileContentsBase64

    if arg_Caption is not None:
      tmp_XmlNodeTextSpan = ET.SubElement(tmp_XmlNodeTextP_002, self.GetXmlTagName(u'text:span'))
      tmp_XmlNodeTextSpan.set(self.GetXmlTagName(u'text:style-name'), u'T1')
      tmp_XmlNodeTextSpan.tail = u'Obraz '
      self.AddImageCaption(tmp_XmlNodeTextP_002, arg_Caption)
      tmp_XmlNodeTextLineBreak = ET.SubElement(tmp_XmlNodeTextSpan, self.GetXmlTagName(u'text:line-break'))

    self.atr_ImageCounter = self.atr_ImageCounter + 1

  def GetImageCounter(self):
    return self.atr_ImageCounter

  def HandleTagObjectText(self, arg_XmlNode):
    self.AddTextToCurrentParagraph(arg_XmlNode.text)

    return u''

  def HandleTagObjectImage(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrName = arg_XmlNode.get(cfg_XmlAttrObjectImage['Name'], None)
    tmp_AtrCaption = arg_XmlNode.get(cfg_XmlAttrObjectImage['Caption'], None)

    # sanity check
    if tmp_AtrName is None:
      raise Exception

    # get xml node: image object
    self.AddImage(self.atr_XmlNodeOfficeText, tmp_AtrName, tmp_AtrCaption)

    return u''.join(filter(None, tmp_Contents))

  def HandleTagScriptureExtract(self, arg_XmlNode):
    tmp_AtrOrigin = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Origin'], None)
    tmp_AtrInline = arg_XmlNode.get(cfg_XmlAttrScriptureExtract['Inline'], u'true').lower()

    # sanity check
    if tmp_AtrOrigin is None:
      raise Exception

    tmp_Origin = self.GetOrigin(tmp_AtrOrigin)

    if tmp_AtrInline == u'false':
      tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))

      if True:
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Scripture_20_extract_20_raw')
        tmp_XmlNodeTextP.text = super(FODT, self).HandleTagScriptureExtract(arg_XmlNode)
      else:
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Scripture_20_extract_20_-_20_high')
        tmp_XmlNodeTextP.text = super(FODT, self).HandleTagScriptureExtract(arg_XmlNode, False)

        tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Scripture_20_extract_20_-_20_low')
        tmp_XmlNodeTextP.text = tmp_Origin
    else:
      self.AddTextToCurrentParagraph(super(FODT, self).HandleTagScriptureExtract(arg_XmlNode))

    return u''

  def HandleTagSectioningSection(self, arg_XmlNode):
    tmp_Contents = []
    tmp_AtrLevel = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Level'], None)
    tmp_AtrTitle = arg_XmlNode.get(cfg_XmlAttrSectioningSection['Title'], None)
    tmp_XmlNodeScriptureExtractsToBeStudied = None

    # sanity check
    if tmp_AtrLevel is None:
      raise Exception

    # get level
    tmp_Level = int(tmp_AtrLevel)
    
    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level

    # set text paragraphs
    self.atr_TextParagraphPrev = None
    self.atr_TextParagraphCurr = None

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_XmlNodeDcTitle = self.atr_XmlNodeRoot.find(u'.//' + self.GetXmlTagName(u'dc:title'))

      # sanity check
      if tmp_XmlNodeDcTitle is None:
        raise Exception

      tmp_XmlNodeDcTitle.text = u' - '.join(filter(None, [self.atr_DocumentTitle, self.atr_DocumentSubTitle]))

      tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
      tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Title')
      tmp_XmlNodeTextP.text = self.atr_DocumentTitle

      if self.atr_DocumentEmblem is not None and len(self.atr_DocumentEmblem) > 0:
        self.AddImage(self.atr_XmlNodeOfficeText, self.atr_DocumentEmblem)

      if self.atr_DocumentSubTitle is not None and len(self.atr_DocumentSubTitle) > 0:
        tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Subtitle')
        tmp_XmlNodeTextP.text = self.atr_DocumentSubTitle

      if self.atr_DocumentQuote is not None and len(self.atr_DocumentQuote) > 0:
        tmp_XmlNodeTextP = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
        tmp_XmlNodeTextP.set(self.GetXmlTagName(u'text:style-name'), u'Main_20_quote')
        tmp_XmlNodeTextP.text = self.atr_DocumentQuote

      tmp_XmlNodeScriptureExtractsToBeStudied = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:p'))
      tmp_XmlNodeScriptureExtractsToBeStudied.set(self.GetXmlTagName(u'text:style-name'), u'Scripture_20_extracts_20_to_20_be_20_studied')
      tmp_XmlNodeScriptureExtractsToBeStudiedInner = ET.SubElement(tmp_XmlNodeScriptureExtractsToBeStudied, self.GetXmlTagName(u'text:span'))
      tmp_XmlNodeScriptureExtractsToBeStudiedInner.set(self.GetXmlTagName(u'text:style-name'), u'T5')
    else:
      if tmp_AtrTitle is not None:
        # add header
        tmp_XmlNodeTextH = ET.SubElement(self.atr_XmlNodeOfficeText, self.GetXmlTagName(u'text:h'))
        tmp_XmlNodeTextH.set(self.GetXmlTagName(u'text:style-name'), u'Heading_20_' + str(tmp_Level))
        tmp_XmlNodeTextH.set(self.GetXmlTagName(u'text:outline-level'), str(tmp_Level))
        tmp_XmlNodeTextH.text = tmp_AtrTitle

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(ET.tostring(self.atr_XmlNodeRoot))

      if tmp_XmlNodeScriptureExtractsToBeStudiedInner is not None:
        if len(self.atr_ScriptureExtracts) > 0:
          tmp_XmlNodeScriptureExtractsToBeStudiedInner.text = u'Wersety do studium: '
          tmp_XmlNodeScriptureExtractsToBeStudiedInner.tail = u', '.join(self.atr_ScriptureExtracts)
        else:
          tmp_XmlNodeScriptureExtractsToBeStudiedInner.text = None
          tmp_XmlNodeScriptureExtractsToBeStudiedInner.tail = None
    else:
      pass

    # set current sectioning level
    self.atr_SectioningLevel = tmp_Level - 1

    return u'\n'.join(filter(None, tmp_Contents))

  def HandleTagObjectParagraph(self, arg_XmlNode):
    return super(FODT, self).HandleTagObjectParagraph(arg_XmlNode)

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
    self.atr_VersetDelimiter = u' (\\ldots) '

    # set default verset opening quote
    self.atr_VersetOpeningQuote = u',,'

    # set default verset closing quote
    self.atr_VersetClosingQuote = u'\'\''

  def GetName(self):
    return self.__class__.__name__.lower()

  def GetOrigin(self, arg_Origin):
    return u'\\mbox{(' + arg_Origin + u')}'

  def HandleTagObjectParagraph(self, arg_XmlNode):
    tmp_Contents = []

    tmp_Contents.append(u'\\paragraph{}')
    tmp_Contents.append(super(TEX, self).HandleTagObjectParagraph(arg_XmlNode))

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
      tmp_Contents.append(str(tmp_TokScriptureExtracts))
    else:
      tmp_Section = Modules.Sectioning.GetLevelName(tmp_Level)

      # sanity check
      if tmp_Section is None:
        raise Exception

      if tmp_AtrTitle is not None:
        tmp_Header = u'\\' + tmp_Section + u'{' + tmp_AtrTitle + u'}'
      else:
        tmp_Header = u'\\' + tmp_Section + u'*{}'

      tmp_Contents.append(tmp_Header)

    for tmp_XmlNodeChild in arg_XmlNode:
      tmp_Contents.append(self.HandleTag(tmp_XmlNodeChild))

    if tmp_Level == Modules.Sectioning.atr_Levels['document']:
      tmp_Contents.append(u'\\end{document}')

      if tmp_TokScriptureExtracts is not None:
        if len(self.atr_ScriptureExtracts) > 0:
          tmp_TokScriptureExtracts.SetText(u'\n'.join([u'\\begin{center}', u'\\textbf{Wersety do studium:} ' + u', '.join(self.atr_ScriptureExtracts), u'\\end{center}']))
        else:
          tmp_TokScriptureExtracts.SetText(u'')

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

