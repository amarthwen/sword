# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import datetime, hashlib, os, re, xml.etree.ElementTree as ET
from modules import config

# ================================================================ #
# configuration
# ================================================================ #
# entry item related configuration variables
cfg_ChrEntryItemPathElementSeparator = u'::'
cfg_ChrEntryItemParamListSeparator = u','
cfg_ChrEntryItemQuote = config.EntryItemQuoteChr

# text origin related regular expression configuration variables
cfg_RegExpStrTextOriginDelimiterLineRange = config.ScriptureTextOriginDelimiterVersetRange
cfg_RegExpStrTextOriginDelimiterLineRangeInternal = config.ScriptureTextOriginDelimiterVersetRangeInternal
cfg_RegExpStrTextOriginDelimiterChapter = config.ScriptureTextOriginDelimiterChapter
cfg_RegExpStrTextOriginDelimiterChapterInternal = config.ScriptureTextOriginDelimiterChapterInternal
cfg_RegExpStrTextOriginDelimiterReferenceRange = config.ScriptureTextOriginDelimiterReferenceRange

# xml attributes: scripture:extract
cfg_XmlAttrScriptureExtractVerset = config.ScriptureExtractVersetXmlAttribs

# ================================================================ #
# implementation of helper class: Token
# ================================================================ #
class Token:
  def __init__(self):
    self.atr_Text = u''
    self.atr_DateTime = datetime.datetime.now()
    self.atr_Payload = os.urandom(1024)
    self.atr_PayloadHash = hashlib.sha1()

    # calculate payload hash
    self.atr_PayloadHash.update(self.atr_Payload)

  def __str__(self):
    # return u'(TOKEN:#tmsp=\'{}\'|#hash=\'{}\')'.format(self.atr_DateTime.strftime("%Y.%m.%d_%H:%M:%S.%f"), self.atr_PayloadHash.hexdigest().upper())
    return u'#TOKEN_TMSP:{}_HASH:{}#'.format(self.atr_DateTime.strftime("%Y%m%d%H%M%S%f"), self.atr_PayloadHash.hexdigest().upper())

  def SetText(self, arg_Text):
    self.atr_Text = arg_Text

  def GetText(self):
    return self.atr_Text

# ================================================================ #
# implementation of helper class: Token
# ================================================================ #
class Tokens:
  def __init__(self):
    self.atr_Tokens = {}

  def Create(self, arg_Name):
    if arg_Name not in self.atr_Tokens:
      self.atr_Tokens[arg_Name] = Token()

    return self.atr_Tokens[arg_Name]

  def Get(self, arg_Name, arg_Exceptional = None):
    return self.atr_Tokens.get(arg_Name, arg_Exceptional)

  def Items(self):
    return self.atr_Tokens.items()

# ================================================================ #
# implementation of helper class: Entry
# ================================================================ #
class Entry:
  atr_RegExpStrToken = u'[a-zA-Z0-9_]*'
  atr_RegExpStrPath = u'(' + atr_RegExpStrToken + u'(?:' + u'[\s]*' + cfg_ChrEntryItemPathElementSeparator + u'[\s]*' + atr_RegExpStrToken + u')*)'

  atr_RegExpStrString = cfg_ChrEntryItemQuote + u'[^' + cfg_ChrEntryItemQuote + u']*' + cfg_ChrEntryItemQuote
  atr_RegExpStrParamListElement = u'[\s]*(?:' + atr_RegExpStrString + u'|' + atr_RegExpStrToken + u')[\s]*'
  atr_RegExpStrParamList = u'[\s]*\((' + atr_RegExpStrParamListElement + u'(?:' + cfg_ChrEntryItemParamListSeparator + atr_RegExpStrParamListElement + u')*)\)'
  atr_RegExpStrOptionalParamListSeparatorWithParamListElement = u'(' + cfg_ChrEntryItemParamListSeparator + u'{0,1}(' + atr_RegExpStrParamListElement + '))'

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
      'elements' : [tmpPathElement.strip() for tmpPathElement in arg_Path.split(cfg_ChrEntryItemPathElementSeparator)],
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
# implementation of helper class: Translation
# ================================================================ #
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
    self.atr_XmlNodeRoot = None
    self.atr_FileName = arg_TranslationFileName

  def __str__(self):
    return self.GetName()

  def GetContents(self):
    if self.atr_XmlNodeRoot is None:
      self.atr_XmlNodeRoot = ET.parse(self.atr_FileName)

    return self.atr_XmlNodeRoot

  def GetName(self):
    return self.GetContents().getroot().get('shortcut', None)

  def GetFullName(self):
    return self.GetContents().getroot().get('name', None)

  def GetVersetReference(self, arg_Book, arg_Chapter, arg_Verset):
    tmpXmlNode = self.GetContents().find(u"./book[@shortcut='{}']/chapter[@id='{}']/verset[@id='{}']".format(arg_Book, str(arg_Chapter), str(arg_Verset)))

    if tmpXmlNode is None:
      raise Exception

    return int(tmpXmlNode.get('ref', '0'))

  def GetVersetReferencesWithNormalizedOrigin(self, arg_TextOrigin):
    tmp_Versets = []
    tmp_VersetReferences = []

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

        tmp_VersetReferenceMin = self.GetVersetReference(tmp_Book, tmp_ChapterNr, tmp_LineRangeMin)
        tmp_VersetReferenceMax = self.GetVersetReference(tmp_Book, tmp_ChapterNr, tmp_LineRangeMax)

        # sanity check
        if tmp_VersetReferenceMin == 0 or tmp_VersetReferenceMax == 0:
          raise Exception

        tmp_Versets.append((tmp_ChapterNr, tmp_LineRangeMin, tmp_LineRangeMax, tmp_VersetReferenceMin, tmp_VersetReferenceMax))

    tmp_Versets.append((u'', 0, 0, 0, u''))

    tmp_VersetMin = None
    tmp_VersetMax = None

    tmp_Origin = tmp_Book
    tmp_LastChapter = 0

    for tmp_VersetCurr in tmp_Versets:
      if tmp_VersetMax is not None and tmp_VersetCurr[1] == tmp_VersetMax[2] + 1 and tmp_VersetCurr[0] == tmp_VersetMax[0]:
        tmp_VersetMax = tmp_VersetCurr
      else:
        if tmp_VersetMin is not None and tmp_VersetMax is not None:
          if tmp_VersetMin != tmp_VersetMax or tmp_VersetMin[1] != tmp_VersetMax[2]:
            tmp_VersetReferences.append({
              cfg_XmlAttrScriptureExtractVerset['Reference'] : str(tmp_VersetMin[3]) + cfg_RegExpStrTextOriginDelimiterReferenceRange + str(tmp_VersetMax[4]),
              cfg_XmlAttrScriptureExtractVerset['Origin'] : tmp_Book + u' ' + str(tmp_VersetMin[0]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[1]) + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + str(tmp_VersetMax[2])
            })

            # add versets to text origin
            if tmp_LastChapter != tmp_VersetMin[0]:
              if tmp_LastChapter != 0:
                tmp_Origin = tmp_Origin + cfg_RegExpStrTextOriginDelimiterChapter
              tmp_Origin = tmp_Origin + u' ' + str(tmp_VersetMin[0]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[1]) + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + str(tmp_VersetMax[2])
            else:
              if tmp_LastChapter != 0:
                tmp_Origin = tmp_Origin + cfg_RegExpStrTextOriginDelimiterLineRange
              tmp_Origin = tmp_Origin + str(tmp_VersetMin[1]) + cfg_RegExpStrTextOriginDelimiterLineRangeInternal + str(tmp_VersetMax[2])
          else:
            tmp_VersetReferences.append({
              cfg_XmlAttrScriptureExtractVerset['Reference'] : str(tmp_VersetMin[3]),
              cfg_XmlAttrScriptureExtractVerset['Origin'] : tmp_Book + u' ' + str(tmp_VersetMin[0]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[1])
            })

            # add versets to text origin
            if tmp_LastChapter != tmp_VersetMin[0]:
              if tmp_LastChapter != 0:
                tmp_Origin = tmp_Origin + cfg_RegExpStrTextOriginDelimiterChapter
              tmp_Origin = tmp_Origin + u' ' + str(tmp_VersetMin[0]) + cfg_RegExpStrTextOriginDelimiterChapterInternal + u' ' + str(tmp_VersetMin[1])
            else:
              if tmp_LastChapter != 0:
                tmp_Origin = tmp_Origin + cfg_RegExpStrTextOriginDelimiterLineRange
              tmp_Origin = tmp_Origin + str(tmp_VersetMin[1])

          tmp_LastChapter = tmp_VersetMin[0]

        tmp_VersetMin = tmp_VersetCurr
        tmp_VersetMax = tmp_VersetCurr

    return tmp_VersetReferences, tmp_Origin

  def GetVersetByReferenceRange(self, arg_RangeMin, arg_RangeMax):
    tmp_Verset = []

    for tmp_VersetRef in range(arg_RangeMin, arg_RangeMax + 1):
      tmpXmlNode = self.GetContents().find(u"./book/chapter/verset[@ref='{}']".format(str(tmp_VersetRef)))

      if tmpXmlNode is None:
        raise Exception

      tmp_Verset.append(tmpXmlNode.text)

    return tmp_Verset

  def GetVersetByReferenceRangeStr(self, arg_VersetReferenceRangeStr):
    tmp_Verset = []
    tmp_Range = arg_VersetReferenceRangeStr.split(cfg_RegExpStrTextOriginDelimiterReferenceRange)
    tmp_RangeMin = int(tmp_Range[0])
    tmp_RangeMax = int(tmp_Range[0])

    if len(tmp_Range) > 1:
      tmp_RangeMax = int(tmp_Range[1])

    return self.GetVersetByReferenceRange(tmp_RangeMin, tmp_RangeMax)

  @staticmethod
  def GetNameFromFileName(arg_FileName):
    return os.path.splitext(os.path.basename(arg_FileName))[0]

