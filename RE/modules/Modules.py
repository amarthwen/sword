# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, config, os, re
import xml.etree.ElementTree as ET

# ================================================================ #
# configuration
# ================================================================ #
cfg_ChrPathElementSeparator = u'::'
cfg_ChrParamListSeparator = u','
cfg_ChrQuote = u'"'

# line related regular expression configuration variables
cfg_RegExpStrLineDelimiterInternal = config.ScriptureLineDelimiterInternal

# translation related configuration variables
cfg_TranslationsPath = config.ScriptureTranslationPath
cfg_TranslationExtension = config.ScriptureTranslationExtension
cfg_TranslationFullNameQuoteChar = config.ScriptureFullNameQuoteChar

# text origin related regular expression configuration variables
cfg_RegExpStrTextOriginDelimiterLineRange = config.ScriptureTextOriginDelimiterVersetRange
cfg_RegExpStrTextOriginDelimiterLineRangeInternal = config.ScriptureTextOriginDelimiterVersetRangeInternal
cfg_RegExpStrTextOriginDelimiterChapter = config.ScriptureTextOriginDelimiterChapter
cfg_RegExpStrTextOriginDelimiterChapterInternal = config.ScriptureTextOriginDelimiterChapterInternal
cfg_RegExpStrTextOriginDelimiterReferenceRange = config.ScriptureTextOriginDelimiterReferenceRange

# ================================================================ #
# implementation of module entry
# ================================================================ #
class Entry:
  atr_RegExpStrTokenRaw = u'[a-zA-Z0-9_]*'
  atr_RegExpStrToken = u'[\s]*' + atr_RegExpStrTokenRaw + u'[\s]*'
  atr_RegExpStrPathElement = u'[\s]*' + atr_RegExpStrToken + u'[\s]*'
  atr_RegExpStrPath = u'(' + atr_RegExpStrPathElement + u'(?:' + cfg_ChrPathElementSeparator + atr_RegExpStrPathElement + u')*)'

  atr_RegExpStrString = cfg_ChrQuote + u'[^' + cfg_ChrQuote + u']*' + cfg_ChrQuote
  atr_RegExpStrParamListElement = u'[\s]*(?:' + atr_RegExpStrString + u'|' + atr_RegExpStrTokenRaw + u')[\s]*'
  atr_RegExpStrParamList = u'\((' + atr_RegExpStrParamListElement + u'(?:' + cfg_ChrParamListSeparator + atr_RegExpStrParamListElement + u')*)\)[\s]*'
  atr_RegExpStrOptionalParamListSeparatorWithParamListElement = u'(' + cfg_ChrParamListSeparator + u'{0,1}(' + atr_RegExpStrParamListElement + '))'

  atr_RegExpStrPathAndParamList = u'(' + atr_RegExpStrPath + atr_RegExpStrParamList + u')'

  atr_RegExpPathAndParamList = re.compile(atr_RegExpStrPathAndParamList, re.UNICODE)
  atr_RegExpParamListElement = re.compile(atr_RegExpStrOptionalParamListSeparatorWithParamListElement, re.UNICODE)

  def __init__(self, arg_Line):
    tmp_Items = []

    while len(arg_Line) > 0:
      tmp_Rslt = self.atr_RegExpPathAndParamList.search(arg_Line)
      if tmp_Rslt is not None:
        tmp_Groups = tmp_Rslt.groups()

        tmp_Start = tmp_Rslt.start(0)
        tmp_End = tmp_Rslt.end(0)

        # add text before entry
        if tmp_Start > 0:
          tmp_Items.append(arg_Line[ : tmp_Start])

        # add entry
        tmp_Items.append(self.GetEntry(arg_Line[tmp_Start : tmp_End], tmp_Groups[1].strip(), tmp_Groups[2].strip()))

        arg_Line = arg_Line[tmp_End : ]
      else:
        # add text after entry
        tmp_Items.append(arg_Line)
        break

    self.atr_Items = tmp_Items

  def GetEntry(self, arg_Text, arg_Path, arg_Params):
    tmp_Entry = {
      'text' : arg_Text,
      'elements' : [tmpPathElement.strip() for tmpPathElement in arg_Path.split(cfg_ChrPathElementSeparator)],
      'params' : []
    }

    while arg_Params != '':
      tmp_Rslt = self.atr_RegExpParamListElement.match(arg_Params)
      if tmp_Rslt is not None:
        tmp_Groups = tmp_Rslt.groups()
        tmp_Param = tmp_Groups[1].strip()
        tmp_Entry['params'].append(tmp_Param)
        arg_Params = arg_Params[:tmp_Rslt.start(1)] + arg_Params[tmp_Rslt.end(1):]
      else:
        break;

    return tmp_Entry

  def GetItems(self):
    return self.atr_Items

# ================================================================ #
# implementation of module interface
# ================================================================ #
# interface
class IModule:
  def __init__(self):
    self.atr_Modules = {}

    self.atr_XmlNamespace = {
      self.GetName().lower() : 'https://github.com/amarthwen/sword/xmlns/' + self.GetName().lower()
    }

    ET.register_namespace(self.atr_XmlNamespace.keys()[0], self.atr_XmlNamespace.values()[0])

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def GetXmlNamespaces(self):
    tmp_XmlNamespaces = {}

    for tmp_Module in self.atr_Modules.values():
      tmp_XmlNamespaces.update(tmp_Module.GetXmlNamespaces())

    tmp_XmlNamespaces.update(self.atr_XmlNamespace)

    return tmp_XmlNamespaces

  def GetXmlTagName(self, arg_TagName):
    return u'{' + self.atr_XmlNamespace.values()[0] + u'}' + arg_TagName

  def HandleCmdUnknown(self, arg_Params):
    raise NotImplementedError

  def HandleCmd(self, arg_Function, arg_Params):
    raise NotImplementedError

  def HandleObjectLocally(self, arg_XmlNodeObject):
    pass

  def HandleObject(self, arg_XmlNodeObject):
    for tmp_Module in self.atr_Modules.values():
      tmp_Module.HandleObject(arg_XmlNodeObject)

    self.HandleObjectLocally(arg_XmlNodeObject)
        
  def Process(self, arg_Elements, arg_Params):
    tmp_XmlNodeRoot = None

    if len(arg_Elements) == 1:
      tmp_XmlNodeChild = self.HandleCmd(arg_Elements[0], arg_Params)
    else:
      tmp_Module = self.atr_Modules.get(arg_Elements[0], None)

      if tmp_Module is None:
        raise Exception

      tmp_XmlNodeChild = tmp_Module.Process(arg_Elements[1:], arg_Params)

    return tmp_XmlNodeChild

  def Register(self, arg_Module):
    tmp_ModuleName = str(arg_Module)

    if tmp_ModuleName not in self.atr_Modules:
      self.atr_Modules[tmp_ModuleName] = arg_Module

# ================================================================ #
# implementation of module: Scripture
# ================================================================ #
# helper class
class Translation:
  # text origin related regular expression data
  atr_RegExpStrTextOriginRange = r'\d+(?:' + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + r'\d+){0,1}'
  atr_RegExpStrTextOriginMultipleRange = atr_RegExpStrTextOriginRange + r'(?:' + cfg_RegExpStrTextOriginDelimiterLineRange + atr_RegExpStrTextOriginRange + r')*'
  atr_RegExpStrTextOriginChapter = r'(?:\d+' + cfg_RegExpStrTextOriginDelimiterChapterInternal + atr_RegExpStrTextOriginMultipleRange + r')'
  atr_RegExpStrTextOriginMultipleChapters = atr_RegExpStrTextOriginChapter + r'(?:' + cfg_RegExpStrTextOriginDelimiterChapter + atr_RegExpStrTextOriginChapter + r')*'
  atr_RegExpStrTextOriginQuery = r'(\d*\D+)('+ atr_RegExpStrTextOriginMultipleChapters + r')'

  # text origin related regular expression
  atr_RegExpTextOriginQuery = re.compile(atr_RegExpStrTextOriginQuery, re.UNICODE | re.IGNORECASE)

  def __init__(self, arg_TranslationFileName):
    self.atr_XmlNodeRoot = ET.parse(arg_TranslationFileName)

  def __str__(self):
    return self.GetName()

  def GetName(self):
    return self.atr_XmlNodeRoot.getroot().get('shortcut', None)

  def GetFullName(self):
    return self.atr_XmlNodeRoot.getroot().get('name', None)

  def GetVerset(self, arg_Book, arg_Chapter, arg_Verset):
    tmpXmlNode = self.atr_XmlNodeRoot.find(u"./book[@shortcut='{}']/chapter[@id='{}']/verset[@id='{}']".format(arg_Book, str(arg_Chapter), str(arg_Verset)))

    if tmpXmlNode is None:
      raise Exception

    return (arg_Book, arg_Chapter, arg_Verset, int(tmpXmlNode.get('ref', '0')), tmpXmlNode.text)

  def GetText(self, arg_TextOrigin, tmp_XmlNodeRoot):
    tmp_Versets = []

    tmp_Rslt = self.atr_RegExpTextOriginQuery.match(arg_TextOrigin.replace(u' ', u''))
    if tmp_Rslt is None:
      raise Exception

    # get book and chapters with lines
    tmp_Groups = tmp_Rslt.groups()
    tmp_Book = tmp_Groups[0]
    tmp_Chapters = tmp_Groups[1].split(cfg_RegExpStrTextOriginDelimiterChapter)
    for tmp_Chapter in tmp_Chapters:
      tmp_ChapterInfo = tmp_Chapter.split(cfg_RegExpStrTextOriginDelimiterChapterInternal)
      tmp_ChapterNr = int(tmp_ChapterInfo[0])
      tmp_LineRanges = tmp_ChapterInfo[1].split(cfg_RegExpStrTextOriginDelimiterLineRange)
      for tmp_LineRange in tmp_LineRanges:
        tmp_LineRangeMinMax = tmp_LineRange.split(cfg_RegExpStrTextOriginDelimiterLineRangeInternal)

        # check if single line or range of lines
        if len(tmp_LineRangeMinMax) == 1:
          tmp_LineRangeMin = int(tmp_LineRangeMinMax[0])
          tmp_LineRangeMax = int(tmp_LineRangeMinMax[0])
        else:
          tmp_LineRangeMin = int(tmp_LineRangeMinMax[0])
          tmp_LineRangeMax = int(tmp_LineRangeMinMax[1])

        # validate min and max elements
        if tmp_LineRangeMin > tmp_LineRangeMax:
          tmp_LineRangeMid = tmp_LineRangeMin
          tmp_LineRangeMin = tmp_LineRangeMax
          tmp_LineRangeMax = tmp_LineRangeMid

        # add xml nodes for each line
        for i in range(tmp_LineRangeMin, tmp_LineRangeMax + 1):
          tmp_Versets.append(self.GetVerset(tmp_Book, tmp_ChapterNr, i))

    tmp_Versets.append((u'', 0, 0, 0, u''))

    tmp_VersetMin = None
    tmp_VersetMax = None
    for tmp_VersetCurr in tmp_Versets:
      if tmp_VersetMax is not None and tmp_VersetCurr[3] == tmp_VersetMax[3] + 1 and tmp_VersetCurr[1] == tmp_VersetMax[1]:
        tmp_VersetMax = tmp_VersetCurr
        # tmp_Text = tmp_Text + u' ' + tmp_VersetCurr[4]
      else:
        if tmp_VersetMin is not None and tmp_VersetMax is not None:
          tmp_XmlNodeVerset = ET.SubElement(tmp_XmlNodeRoot, 'verset')
          if tmp_VersetMin != tmp_VersetMax:
            tmp_XmlNodeVerset.set('ref', str(tmp_VersetMin[3]) + cfg_RegExpStrTextOriginDelimiterReferenceRange + str(tmp_VersetMax[3]))
            tmp_XmlNodeVerset.set('origin', tmp_VersetMin[0] + u' ' + str(tmp_VersetMin[1]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[2]) + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + str(tmp_VersetMax[2]))
          else:
            tmp_XmlNodeVerset.set('ref', str(tmp_VersetMin[3]))
            tmp_XmlNodeVerset.set('origin', tmp_VersetMin[0] + u' ' + str(tmp_VersetMin[1]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[2]))
          # tmp_XmlNodeVerset.text = tmp_Text

        tmp_VersetMin = tmp_VersetCurr
        tmp_VersetMax = tmp_VersetCurr
        # tmp_Text = tmp_VersetCurr[4]

  @staticmethod
  def GetNameFromFileName(arg_FileName):
    return os.path.splitext(os.path.basename(arg_FileName))[0]

# helper class
class Translations:
  def __init__(self):
    self.atr_Translations = {}
    self.atr_CurrentTranslation = None

  def Get(self, arg_TranslationName):
    return self.atr_Translations.get(arg_TranslationName, None)

  def GetCurrent(self):
    return self.atr_CurrentTranslation

  def SetCurrent(self, arg_TranslationName):
    self.atr_CurrentTranslation = self.Get(arg_TranslationName)

  def Register(self, arg_TranslationFileName):
    tmp_TranslationName = Translation.GetNameFromFileName(arg_TranslationFileName)

    if tmp_TranslationName not in self.atr_Translations:
      self.atr_Translations[tmp_TranslationName] = Translation(arg_TranslationFileName)

# module
class Scripture(IModule):
  def __init__(self):
    IModule.__init__(self)

    self.atr_Translations = Translations()

    # register all available translations
    for tmp_File in os.listdir(cfg_TranslationsPath):
      if tmp_File.endswith(cfg_TranslationExtension):
        self.atr_Translations.Register(os.path.join(cfg_TranslationsPath, tmp_File))

  def GetName(self):
    return self.__class__.__name__

  def HandleCmdGetText(self, arg_Params):
    tmp_TextOrigin = arg_Params[0].strip(cfg_ChrQuote)

    tmp_XmlNodeRoot = ET.Element(self.GetXmlTagName('extract'))

    tmp_CurrentTranslation = self.atr_Translations.GetCurrent()

    if tmp_CurrentTranslation is None:
      raise Exception

    tmp_CurrentTranslation.GetText(tmp_TextOrigin, tmp_XmlNodeRoot)

    tmp_XmlNodeRoot.set('translation', tmp_CurrentTranslation.GetName())
    tmp_XmlNodeRoot.set('origin', tmp_TextOrigin)

    return tmp_XmlNodeRoot

  def HandleCmdUseTranslation(self, arg_Params):
    tmp_XmlNodeRoot = None
    tmp_TranslationName = arg_Params[0].strip(cfg_ChrQuote)

    if self.atr_Translations.Get(tmp_TranslationName) is None:
      raise Exception

    self.atr_Translations.SetCurrent(tmp_TranslationName)

    return tmp_XmlNodeRoot

  def HandleCmd(self, arg_Function, arg_Params):
    return {
        'GetText' : self.HandleCmdGetText,
        'UseTranslation' : self.HandleCmdUseTranslation
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

# ================================================================ #
# implementation of module: Document
# ================================================================ #
# module
class Sectioning(IModule):
  atr_Levels = {
    'Document' : 0,
    'Section' : 1,
    'SubSection' : 2,
    'SubSubSection' : 3,
    'Paragraph' : 4,
    'SubParagraph' : 5
  }

  def __init__(self):
    IModule.__init__(self)

    # set xml path
    self.atr_XmlPath = [None for tmp_Key in self.atr_Levels]

  def GetName(self):
    return self.__class__.__name__

  def GetCurrentLevel(self):
    tmp_CurrentLevel = -1

    # calculate current level
    for tmp_XmlNode in self.atr_XmlPath:
      if tmp_XmlNode is not None:
        tmp_CurrentLevel = tmp_CurrentLevel + 1
      else:
        break

    return tmp_CurrentLevel

  def HandleObjectLocally(self, arg_XmlNodeObject):
    # do not add document itself
    if arg_XmlNodeObject is not None and arg_XmlNodeObject.find(u'.//' + Sectioning.GetLevelName(0)) is None:
      tmp_CurrentLevel = self.GetCurrentLevel()

      if tmp_CurrentLevel >= 0 and self.atr_XmlPath[tmp_CurrentLevel] is not None:
        self.atr_XmlPath[tmp_CurrentLevel].append(arg_XmlNodeObject)

  def HandleCmdBegin(self, arg_Params):
    tmp_XmlNode = None
    tmp_Level = None
    tmp_Title = None

    # sanity check
    if len(arg_Params) == 0:
      raise Exception

    # get requested level
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrQuote), None)

    # sanity check
    if tmp_Level is None:
      raise Exception

    # sanity check
    if tmp_Level > self.GetCurrentLevel() + 1:
      raise Exception

    # sanity check
    if tmp_Level == 0 and self.atr_XmlPath[tmp_Level] is not None:
      raise Exception

    # get title, if set
    if len(arg_Params) > 1:
      tmp_Title = arg_Params[1].strip(cfg_ChrQuote)

    # set tag name
    tmp_TagName = self.GetXmlTagName(Sectioning.GetLevelName(tmp_Level).lower())

    if tmp_Level == 0:
      tmp_XmlNode = ET.Element(tmp_TagName)
    else:
      tmp_XmlNode = ET.SubElement(self.atr_XmlPath[tmp_Level - 1], tmp_TagName)

    if tmp_Title is not None:
      tmp_XmlNode.set('title', tmp_Title)

    # assign xml node in xml path
    self.atr_XmlPath[tmp_Level] = tmp_XmlNode

    # clear all children from xml path
    for tmp_Value in self.atr_Levels.values():
      if tmp_Value > tmp_Level:
        self.atr_XmlPath[tmp_Value] = None

    # return only xml node with level set to 0
    if tmp_Level > 0:
      tmp_XmlNode = None

    return tmp_XmlNode

  def HandleCmdEnd(self, arg_Params):
    tmp_Level = None

    # sanity check
    if len(arg_Params) == 0:
      raise Exception

    # get requested level
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrQuote), None)

    # sanity check
    if tmp_Level is None:
      raise Exception

    # sanity check
    if tmp_Level > self.GetCurrentLevel():
      raise Exception

    # clear all children from xml path
    for tmp_Value in self.atr_Levels.values():
      if tmp_Value >= tmp_Level:
        self.atr_XmlPath[tmp_Value] = None

    return None

  def HandleCmd(self, arg_Function, arg_Params):
    return {
      'Begin' : self.HandleCmdBegin,
      'End' : self.HandleCmdEnd,
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

  @staticmethod
  def GetLevelName(arg_Level):
    tmp_LevelName = None

    for tmp_Key, tmp_Value in Sectioning.atr_Levels.items():
      if tmp_Value == arg_Level:
        tmp_LevelName = tmp_Key
        break;

    return tmp_LevelName

# module
class Document(IModule):
  def __init__(self):
    IModule.__init__(self)

    self.Register(Sectioning())

  def GetName(self):
    return self.__class__.__name__

# ================================================================ #
# implementation of module: SWORD
# ================================================================ #
# module
class SWORD(IModule):
  def __init__(self):
    IModule.__init__(self)

    self.Register(Scripture())
    # self.Register(Document())
    pass

  def GetName(self):
    return self.__class__.__name__

  def HandleCmdInt1(self, arg_Params):
    return None

  def HandleCmdInt2(self, arg_Params):
    return None

  def HandleCmd(self, arg_Function, arg_Params):
    return {
        'Int1' : self.HandleCmdInt1,
        'Int2' : self.HandleCmdInt2
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

# ================================================================ #
# implementation of modules container
# ================================================================ #
# container
class Modules:
  def __init__(self):
    self.atr_Modules = {}

  def Register(self, arg_Module):
    tmp_ModuleName = str(arg_Module)

    if tmp_ModuleName not in self.atr_Modules:
      self.atr_Modules[tmp_ModuleName] = arg_Module

  def Process(self, arg_FileContents):
    tmp_XmlNodeContents = ET.Element('contents')
    tmp_XmlNamespaces = {} # TODO: add default namespace?
    for tmp_Module in self.atr_Modules.values():
      tmp_XmlNamespaces.update(tmp_Module.GetXmlNamespaces())

    for tmp_Line in arg_FileContents:
      tmp_XmlNodeObject = ET.Element('object')
      tmp_Items = Entry(tmp_Line).GetItems()

      for tmp_Item in tmp_Items:
        tmp_Module = None

        if self.atr_Modules:
          try:
            tmp_Module = self.atr_Modules.get(tmp_Item['elements'][0], None)
          except:
            tmp_Module = None

        if tmp_Module is not None:
          tmp_XmlNodeChild = tmp_Module.Process(tmp_Item['elements'][1:], tmp_Item['params'])
          if tmp_XmlNodeChild is not None:
            tmp_XmlNodeObject.append(tmp_XmlNodeChild)
        else:
          # regular text
          tmp_XmlNodeText = ET.SubElement(tmp_XmlNodeObject, 'text')

          try:
            tmp_XmlNodeText.text = tmp_Item['text']
          except:
            tmp_XmlNodeText.text = tmp_Item

      tmp_TagName = u'sectioning' + u':' + Sectioning.GetLevelName(0).lower()
      tmp_XmlNodeDocument = tmp_XmlNodeObject.find(tmp_TagName, tmp_XmlNamespaces)
      if tmp_XmlNodeDocument is not None:
        tmp_XmlNodeContents.append(tmp_XmlNodeDocument)
      else:
        if tmp_XmlNodeObject.find('*') is not None and self.atr_Modules:
          for tmp_Module in self.atr_Modules.values():
            tmp_Module.HandleObject(tmp_XmlNodeObject)

    return tmp_XmlNodeContents

