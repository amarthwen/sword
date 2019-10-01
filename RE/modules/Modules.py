# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, config, os, re
import Objects

# ================================================================ #
# configuration
# ================================================================ #
cfg_ChrPathElementSeparator = u':'
cfg_ChrParamListSeparator = u','
cfg_ChrQuote = u'"'

# line related regular expression configuration variables
cfg_RegExpStrLineDelimiterInternal = config.ScriptureLineDelimiterInternal

# translation related configuration variables
cfg_TranslationsPath = config.ScriptureTranslationPath
cfg_TranslationExtension = config.ScriptureTranslationExtension
cfg_TranslationFullNameQuoteChar = config.ScriptureFullNameQuoteChar

# text origin related regular expression configuration variables
cfg_RegExpStrTextOriginDelimiterLineRange = config.ScriptureTextOriginDelimiterLineRange
cfg_RegExpStrTextOriginDelimiterLineRangeInternal = config.ScriptureTextOriginDelimiterLineRangeInternal
cfg_RegExpStrTextOriginDelimiterChapter = config.ScriptureTextOriginDelimiterChapter
cfg_RegExpStrTextOriginDelimiterChapterInternal = config.ScriptureTextOriginDelimiterChapterInternal

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

  atr_RegExpStrPathAndParamList = atr_RegExpStrPath + atr_RegExpStrParamList

  atr_RegExpPathAndParamList = re.compile(atr_RegExpStrPathAndParamList, re.UNICODE)
  atr_RegExpParamListElement = re.compile(atr_RegExpStrOptionalParamListSeparatorWithParamListElement, re.UNICODE)

  def __init__(self, arg_Line):
    tmp_Entry = None

    tmp_Rslt = self.atr_RegExpPathAndParamList.match(arg_Line)
    if tmp_Rslt is not None:
      tmp_Entry = {
        'elements' : None,
        'params' : []
      }

      tmp_Groups = tmp_Rslt.groups()
      tmp_Path = tmp_Groups[0].strip()
      tmp_Params = tmp_Groups[1].strip()

      tmp_Entry['elements'] = [tmpPathElement.strip() for tmpPathElement in tmp_Path.split(cfg_ChrPathElementSeparator)]

      while tmp_Params != '':
        tmp_Rslt = self.atr_RegExpParamListElement.match(tmp_Params)
        if tmp_Rslt is not None:
          tmp_Groups = tmp_Rslt.groups()
          tmp_Param = tmp_Groups[1].strip()
          tmp_Entry['params'].append(tmp_Param)
          tmp_Params = tmp_Params[:tmp_Rslt.start(1)] + tmp_Params[tmp_Rslt.end(1):]
        else:
          break;

    self.atr_Entry = tmp_Entry

  def Get(self):
    return self.atr_Entry

# ================================================================ #
# implementation of module interface
# ================================================================ #
# interface
class IModule:
  def __init__(self):
    self.atr_Modules = {}

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def HandleCmdUnknown(self, arg_Params):
    raise NotImplementedError

  def HandleCmd(self, arg_Function, arg_Params):
    raise NotImplementedError

  def Process(self, arg_Elements, arg_Params):
    # print '> module running: "' + self.GetName() + '"'
    # print arg_Elements
    # print arg_Params

    if len(arg_Elements) == 1:
      tmp_Rslt = self.HandleCmd(arg_Elements[0], arg_Params)
    else:
      tmp_Module = self.atr_Modules.get(arg_Elements[0], None)
      if tmp_Module is not None:
        tmp_Rslt = tmp_Module.Process(arg_Elements[1:], arg_Params)
      else:
        raise Exception

    return tmp_Rslt

  def Register(self, arg_Module):
    tmp_ModuleName = str(arg_Module)

    if tmp_ModuleName not in self.atr_Modules:
      self.atr_Modules[tmp_ModuleName] = arg_Module

# ================================================================ #
# implementation of module: sword
# ================================================================ #
# helper class
class Translation:
  # line related regular expression data
  atr_RegExpStrLine = cfg_RegExpStrLineDelimiterInternal + r'(\d*\D+)' + cfg_RegExpStrLineDelimiterInternal + r'(\d+)' + cfg_RegExpStrLineDelimiterInternal + r'(\d+)[ ]+\'(.*)\''

  # text origin related regular expression
  atr_RegExpLineQuery = re.compile(atr_RegExpStrLine, re.UNICODE | re.IGNORECASE)

  # text origin related regular expression data
  atr_RegExpStrTextOriginRange = r'\d+(?:' + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + r'\d+){0,1}'
  atr_RegExpStrTextOriginMultipleRange = atr_RegExpStrTextOriginRange + r'(?:' + cfg_RegExpStrTextOriginDelimiterLineRange + atr_RegExpStrTextOriginRange + r')*'
  atr_RegExpStrTextOriginChapter = r'(?:\d+' + cfg_RegExpStrTextOriginDelimiterChapterInternal + atr_RegExpStrTextOriginMultipleRange + r')'
  atr_RegExpStrTextOriginMultipleChapters = atr_RegExpStrTextOriginChapter + r'(?:' + cfg_RegExpStrTextOriginDelimiterChapter + atr_RegExpStrTextOriginChapter + r')*'
  atr_RegExpStrTextOriginQuery = r'(\d*\D+)('+ atr_RegExpStrTextOriginMultipleChapters + r')'

  # text origin related regular expression
  atr_RegExpTextOriginQuery = re.compile(atr_RegExpStrTextOriginQuery, re.UNICODE | re.IGNORECASE)

  def __init__(self, arg_TranslationFileName):
    with codecs.open(arg_TranslationFileName, 'r', 'utf-8') as tmp_TranslationHandle:
      tmp_Lines = [tmp_Line.strip() for tmp_Line in tmp_TranslationHandle.readlines()]

    i = 0
    tmp_Contents = {}
    for tmp_Line in tmp_Lines:
      tmp_Rslt = self.atr_RegExpLineQuery.match(tmp_Line)
      if tmp_Rslt is not None:
        tmp_Groups = tmp_Rslt.groups()
        tmp_Contents[(tmp_Groups[0], int(tmp_Groups[1]), int(tmp_Groups[2]))] = (i, tmp_Groups[3])
        i = i + 1

    self.atr_Name = Translation.GetName(arg_TranslationFileName)
    self.atr_FullName = tmp_Lines[0].strip(cfg_TranslationFullNameQuoteChar)
    self.atr_Contents = tmp_Contents

    # print 'Translation: "' + self.atr_Name + '" ("' + self.atr_FullName + '") registered'

  def __str__(self):
    return self.GetName()

  def GetName(self):
    return self.atr_Name

  def GetFullName(self):
    return self.atr_FullName

  def GetLine(self, arg_LineID):
    tmpLine = self.atr_Contents.get(arg_LineID, None)

    if tmpLine is None:
      raise Exception

    return tmpLine

  def GetText(self, arg_TextOrigin):
    tmp_Lines = []

    tmp_Rslt = self.atr_RegExpTextOriginQuery.match(arg_TextOrigin.replace(u' ', u''))
    if tmp_Rslt is not None:
      tmp_Groups = tmp_Rslt.groups()
      tmp_Chapters = tmp_Groups[1].split(cfg_RegExpStrTextOriginDelimiterChapter)
      for tmp_Chapter in tmp_Chapters:
        tmp_ChapterInfo = tmp_Chapter.split(cfg_RegExpStrTextOriginDelimiterChapterInternal)
        tmp_ChapterNr = int(tmp_ChapterInfo[0])
        tmp_LineRanges = tmp_ChapterInfo[1].split(cfg_RegExpStrTextOriginDelimiterLineRange)
        for tmp_LineRange in tmp_LineRanges:
          tmp_LineRangeMinMax = tmp_LineRange.split(cfg_RegExpStrTextOriginDelimiterLineRangeInternal)
          if len(tmp_LineRangeMinMax) == 1:
            tmp_LineID = (tmp_Groups[0], tmp_ChapterNr, int(tmp_LineRangeMinMax[0]))
            tmp_Line = self.GetLine(tmp_LineID)
            tmp_Lines.append((tmp_LineID, tmp_Line)) 
          else:
            tmp_LineRangeMin = int(tmp_LineRangeMinMax[0])
            tmp_LineRangeMax = int(tmp_LineRangeMinMax[1])
            if tmp_LineRangeMin > tmp_LineRangeMax:
              tmp_LineRangeMid = tmp_LineRangeMin
              tmp_LineRangeMin = tmp_LineRangeMax
              tmp_LineRangeMax = tmp_LineRangeMid
            for i in range(tmp_LineRangeMin, tmp_LineRangeMax + 1):
              tmp_LineID = (tmp_Groups[0], tmp_ChapterNr, i)
              tmp_Line = self.GetLine(tmp_LineID)
              tmp_Lines.append((tmp_LineID, tmp_Line)) 
    else:
      raise Exception

    return str(Objects.ObjectSwordScriptureExtract(self.atr_Name, arg_TextOrigin, tmp_Lines))

  @staticmethod
  def GetName(arg_FileName):
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
    tmp_TranslationName = Translation.GetName(arg_TranslationFileName)

    if tmp_TranslationName not in self.atr_Translations:
      # print '> add translation: "' + tmp_TranslationName + '"'
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
    return u'Scripture'

  def HandleCmdGetText(self, arg_Params):
    tmp_TextOrigin = arg_Params[0].strip(cfg_ChrQuote)

    if self.atr_Translations.GetCurrent() is None:
      raise Exception

    # return ' '.join([tmp_Line for tmp_LineNr, tmp_Line in self.atr_Translations.GetCurrent().GetText(tmp_TextOrigin)])
    return self.atr_Translations.GetCurrent().GetText(tmp_TextOrigin)

  def HandleCmdUseTranslation(self, arg_Params):
    tmp_Rslt = None
    tmp_TranslationName = arg_Params[0].strip(cfg_ChrQuote)
    # print '> use translation: "' + tmp_TranslationName + '"'

    if self.atr_Translations.Get(tmp_TranslationName) is not None:
      self.atr_Translations.SetCurrent(tmp_TranslationName)
      tmp_Rslt = u'<use_translation(' + ','.join(arg_Params) + u')>'
    else:
      raise Exception

    return tmp_Rslt

  def HandleCmd(self, arg_Function, arg_Params):
    return {
        'GetText' : self.HandleCmdGetText,
        'UseTranslation' : self.HandleCmdUseTranslation
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

# ================================================================ #
# implementation of module: document
# ================================================================ #
# module
class Document(IModule):
  def __init__(self):
    IModule.__init__(self)

  def GetName(self):
    return u'Document'

# module
class Sword(IModule):
  def __init__(self):
    IModule.__init__(self)

    self.Register(Scripture())
    self.Register(Document())
    pass

  def GetName(self):
    return u'SWORD'

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
    # print '> registering module: "' + tmp_ModuleName + '"'

    if tmp_ModuleName not in self.atr_Modules:
      self.atr_Modules[tmp_ModuleName] = arg_Module

  def Process(self, arg_FileContents):
    tmp_Lines = []

    for tmp_Line in arg_FileContents:
      tmp_Rslt = None

      tmp_Entry = Entry(tmp_Line).Get()
      if tmp_Entry is not None:
        tmp_Module = self.atr_Modules.get(tmp_Entry['elements'][0], None)
        if tmp_Module is not None:
          tmp_Rslt = tmp_Module.Process(tmp_Entry['elements'][1:], tmp_Entry['params'])

      if tmp_Rslt is not None:
        tmp_Lines.append(tmp_Rslt)
      else:
        tmp_Lines.append(tmp_Line)

    return '#'.join(tmp_Lines)

