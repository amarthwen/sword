# -*- coding: utf-8 -*-

import codecs, os, re

from modules import config, module

# translation related configuration variables
cfg_TranslationPath = config.ScriptureTranslationPath
cfg_TranslationExtension = config.ScriptureTranslationExtension
# default translation used until explicitly set with command SWORD:Scripture:UseTranslation{}
cfg_TranslationNameDefault = config.ScriptureTranslationDefault

cfg_TranslationFullNameQuoteChar = config.ScriptureFullNameQuoteChar

# default line delimiter
cfg_TextExcerptDelimiter = config.ScriptureTextExcerptDelimiter

# line related regular expression configuration variables
cfg_RegExpStrLineDelimiterInternal = config.ScriptureLineDelimiterInternal

# text origin related regular expression configuration variables
cfg_RegExpStrTextOriginDelimiterLineRange = config.ScriptureTextOriginDelimiterLineRange
cfg_RegExpStrTextOriginDelimiterLineRangeInternal = config.ScriptureTextOriginDelimiterLineRangeInternal
cfg_RegExpStrTextOriginDelimiterChapter = config.ScriptureTextOriginDelimiterChapter
cfg_RegExpStrTextOriginDelimiterChapterInternal = config.ScriptureTextOriginDelimiterChapterInternal

# interface: IModule
class IModule:
  def __init__(self):
    pass

  def Process(self, arg_FileContents):
    return None

# interface: IModuleElement
class IModuleElement:
  def __init__(self):
    pass

  def Log(self, arg_Text):
    print '> ' + arg_Text
    # pass

  def HandleCmdUnknown(self, arg_Value):
    self.Log('ERROR: unknown command received')

    return None

  def HandleCmd(self, arg_ModuleParams):
    return self.HandleCmdUnknown(arg_ModuleParams)

class Translation:
  # line related regular expression data
  atr_RegExpStrLine = cfg_RegExpStrLineDelimiterInternal + r'(\d*\D+)' + cfg_RegExpStrLineDelimiterInternal + r'(\d+)' + cfg_RegExpStrLineDelimiterInternal + r'(\d+)[ ]+\'(.*)\''

  # text origin related regular expression
  atr_RegExpLineQuery = re.compile(atr_RegExpStrLine, re.UNICODE | re.IGNORECASE)

  def __init__(self, arg_TranslationName):
    with codecs.open(os.path.join(cfg_TranslationPath, arg_TranslationName + cfg_TranslationExtension), 'r', 'utf-8') as tmp_TranslationHandle:
      tmp_Lines = [tmp_Line.strip() for tmp_Line in tmp_TranslationHandle.readlines()]

    i = 0
    tmp_Contents = {}
    for tmp_Line in tmp_Lines:
      tmp_Rslt = self.atr_RegExpLineQuery.match(tmp_Line)
      if tmp_Rslt is not None:
        tmp_Groups = tmp_Rslt.groups()
        tmp_Contents[(tmp_Groups[0], int(tmp_Groups[1]), int(tmp_Groups[2]))] = (i, tmp_Groups[3])
        i = i + 1

    self.atr_Name = arg_TranslationName
    self.atr_FullName = tmp_Lines[0].strip(cfg_TranslationFullNameQuoteChar)
    self.atr_Contents = tmp_Contents

  def GetName(self):
    return self.atr_Name

  def GetFullName(self):
    return self.atr_FullName

  def GetLine(self, arg_Line):
    tmp_Line = None

    if arg_Line in self.atr_Contents:
      tmp_Line = self.atr_Contents[arg_Line]

    return tmp_Line

  def GetText(self, arg_TextOriginLines):
    tmp_Text = []

    tmp_LineIDPrev = -1
    tmp_LineIDCurr = -1
    if arg_TextOriginLines is not None:
      for tmp_TextOriginLine in arg_TextOriginLines:
        tmp_Line = self.GetLine(tmp_TextOriginLine)
        if tmp_Line is not None:
          tmp_LineIDCurr = tmp_Line[0]
          if tmp_LineIDPrev >= 0 and tmp_LineIDCurr != tmp_LineIDPrev + 1:
            tmp_Text.append(cfg_TextExcerptDelimiter)
          tmp_Text.append(tmp_Line[1])
          tmp_LineIDPrev = tmp_LineIDCurr
        else:
          raise Exception
    else:
      raise Exception

    return u'"' + u' '.join(tmp_Text) + u'"'


class Scripture(IModuleElement):
  # list of all Scriptures already used
  atr_Translations = {}

  # currently used Scripture
  atr_CurrentTranslation = None

  # text origin related regular expression data
  atr_RegExpStrTextOriginRange = r'\d+(?:' + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + r'\d+){0,1}'
  atr_RegExpStrTextOriginMultipleRange = atr_RegExpStrTextOriginRange + r'(?:' + cfg_RegExpStrTextOriginDelimiterLineRange + atr_RegExpStrTextOriginRange + r')*'
  atr_RegExpStrTextOriginChapter = r'(?:\d+' + cfg_RegExpStrTextOriginDelimiterChapterInternal + atr_RegExpStrTextOriginMultipleRange + r')'
  atr_RegExpStrTextOriginMultipleChapters = atr_RegExpStrTextOriginChapter + r'(?:' + cfg_RegExpStrTextOriginDelimiterChapter + atr_RegExpStrTextOriginChapter + r')*'
  atr_RegExpStrTextOriginQuery = r'\((\d*\D+)('+ atr_RegExpStrTextOriginMultipleChapters + r')\)'

  # text origin related regular expression
  atr_RegExpTextOriginQuery = re.compile(atr_RegExpStrTextOriginQuery, re.UNICODE | re.IGNORECASE)

  def __init__(self):
    self._UseTranslation(cfg_TranslationNameDefault)
  
  def _GetLinesFromTextOrigin(self, arg_TextOrigin):
    self.Log('get lines from text origin: ' + arg_TextOrigin)

    tmp_Lines = None

    tmp_Rslt = self.atr_RegExpTextOriginQuery.match(arg_TextOrigin.replace(u' ', u''))
    if tmp_Rslt is not None:
      tmp_Lines = []
      tmp_Groups = tmp_Rslt.groups()
      tmp_Chapters = tmp_Groups[1].split(cfg_RegExpStrTextOriginDelimiterChapter)
      for tmp_Chapter in tmp_Chapters:
        tmp_ChapterInfo = tmp_Chapter.split(cfg_RegExpStrTextOriginDelimiterChapterInternal)
        tmp_ChapterNr = int(tmp_ChapterInfo[0])
        tmp_LineRanges = tmp_ChapterInfo[1].split(cfg_RegExpStrTextOriginDelimiterLineRange)
        for tmp_LineRange in tmp_LineRanges:
          tmp_LineRangeMinMax = tmp_LineRange.split(cfg_RegExpStrTextOriginDelimiterLineRangeInternal)
          if len(tmp_LineRangeMinMax) == 1:
            tmp_Lines.append((tmp_Groups[0], tmp_ChapterNr, int(tmp_LineRangeMinMax[0])))
          else:
            tmp_LineRangeMin = int(tmp_LineRangeMinMax[0])
            tmp_LineRangeMax = int(tmp_LineRangeMinMax[1])
            if tmp_LineRangeMin > tmp_LineRangeMax:
              tmp_LineRangeMid = tmp_LineRangeMin
              tmp_LineRangeMin = tmp_LineRangeMax
              tmp_LineRangeMax = tmp_LineRangeMid
            for i in range(tmp_LineRangeMin, tmp_LineRangeMax + 1):
              tmp_Lines.append((tmp_Groups[0], tmp_ChapterNr, i))
    else:
      raise Exception

    return tmp_Lines

  def _GetTranslation(self, arg_TranslationName):
    if arg_TranslationName not in self.atr_Translations:
      self.atr_Translations[arg_TranslationName] = Translation(arg_TranslationName)

    return self.atr_Translations[arg_TranslationName]

  def _UseTranslation(self, arg_TranslationName):
    self.atr_CurrentTranslation = self._GetTranslation(arg_TranslationName)

  def _GetText(self, arg_TextOrigin, arg_Translation):
    tmp_TextOriginLines = self._GetLinesFromTextOrigin(arg_TextOrigin)

    return arg_Translation.GetText(tmp_TextOriginLines) + u' ' + arg_TextOrigin

  def HandleCmdUseTranslation(self, arg_TranslationName):
    self._UseTranslation(arg_TranslationName)

  def HandleCmdGetText(self, arg_TextOrigin):
    return self._GetText(arg_TextOrigin, self.atr_CurrentTranslation)

  def HandleCmd(self, arg_ModuleParams):
    return {
        'UseTranslation' : self.HandleCmdUseTranslation,
        'GetText' : self.HandleCmdGetText,
    }.get(arg_ModuleParams[0][0], self.HandleCmdUnknown)(arg_ModuleParams[0][1])

# module: SWORD
class SWORD(IModule, IModuleElement):
  atr_Scripture = Scripture()

  # constructor
  def __init__(self):
    pass

  # run module
  def Run(self, arg_ModuleParams):
    return {
        'Scripture' : self.atr_Scripture.HandleCmd,
    }.get(arg_ModuleParams[0][0], self.HandleCmdUnknown)(arg_ModuleParams[1:])

  # process file contents
  def Process(self, arg_FileContents):
    tmp_FileContents = []

    for tmp_Line in arg_FileContents:
      tmp_Module = module.GetModule(tmp_Line)
      if tmp_Module and tmp_Module['id'] == self.__class__.__name__:
        tmp_Rslt = self.Run(tmp_Module['elements'])
        if tmp_Rslt is not None:
          if len(tmp_Rslt) > 0:
            tmp_FileContents.append(tmp_Rslt)
      else:
        tmp_FileContents.append(tmp_Line)

    return tmp_FileContents

