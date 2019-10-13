# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import os, xml.etree.ElementTree as ET
from modules import config, Helpers

# ================================================================ #
# configuration
# ================================================================ #
# entry item related configuration variables
cfg_ChrEntryItemQuote = config.EntryItemQuoteChr

# translation related configuration variables
cfg_StrTranslationsPath = config.ScriptureTranslationsPath
cfg_StrTranslationExtension = config.ScriptureTranslationExtension

# xml attributes: 'scripture:extract'
cfg_XmlAttrScriptureExtract = config.ScriptureExtractXmlAttribs

# ================================================================ #
# implementation of module interface
# ================================================================ #
class IModule:
  atr_XmlNamespaceBase = u'https://github.com/amarthwen/sword/xmlns/'

  def __init__(self):
    self.atr_Modules = {}

    self.atr_XmlNamespace = {
      self.GetName().lower() : IModule.atr_XmlNamespaceBase + self.GetName().lower()
    }

    ET.register_namespace(self.atr_XmlNamespace.keys()[0], self.atr_XmlNamespace.values()[0])

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError
  
  def GetXmlNamespace(self):
    return self.atr_XmlNamespace

  def GetXmlNamespaces(self):
    tmp_XmlNamespaces = {}

    for tmp_Module in self.atr_Modules.values():
      tmp_XmlNamespaces.update(tmp_Module.GetXmlNamespaces())

    tmp_XmlNamespaces.update(self.GetXmlNamespace())

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
# implementation of module: Translations
# ================================================================ #
class Translations(IModule):
  atr_Translations = {}
  atr_CurrentTranslation = None

  def __init__(self):
    IModule.__init__(self)

    # register all available translations
    for tmp_File in os.listdir(cfg_StrTranslationsPath):
      if tmp_File.endswith(cfg_StrTranslationExtension):
        Translations.Register(os.path.join(cfg_StrTranslationsPath, tmp_File))

  def GetName(self):
    return self.__class__.__name__

  @staticmethod
  def Get(arg_TranslationName):
    return Translations.atr_Translations.get(arg_TranslationName, None)

  @staticmethod
  def GetCurrent():
    return Translations.atr_CurrentTranslation

  @staticmethod
  def SetCurrent(arg_TranslationName):
    Translations.atr_CurrentTranslation = Translations.Get(arg_TranslationName)

  @staticmethod
  def Register(arg_TranslationFileName):
    tmp_TranslationName = Helpers.Translation.GetNameFromFileName(arg_TranslationFileName)

    if tmp_TranslationName not in Translations.atr_Translations:
      Translations.atr_Translations[tmp_TranslationName] = Helpers.Translation(arg_TranslationFileName)

  def HandleCmdUse(self, arg_Params):
    tmp_XmlNodeRoot = None
    tmp_TranslationName = arg_Params[0].strip(cfg_ChrEntryItemQuote)

    Translations.SetCurrent(tmp_TranslationName)

    return tmp_XmlNodeRoot

  def HandleCmd(self, arg_Function, arg_Params):
    return {
      'Use' : self.HandleCmdUse
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

# ================================================================ #
# implementation of module: Scripture
# ================================================================ #
class Scripture(IModule):
  def __init__(self):
    IModule.__init__(self)

  def GetName(self):
    return self.__class__.__name__

  def HandleCmdGetText(self, arg_Params):
    tmp_TextOrigin = arg_Params[0].strip(cfg_ChrEntryItemQuote)
    tmp_Inline = False

    if len(arg_Params) > 1:
      tmp_Inline = {
        'true' : True
      }.get(arg_Params[1].lower(), False)

    tmp_XmlNodeRoot = ET.Element(self.GetXmlTagName(u'extract'))

    tmp_CurrentTranslation = Translations.GetCurrent()

    if tmp_CurrentTranslation is None:
      raise Exception

    GetVersetReferences = tmp_CurrentTranslation.GetVersetReferences(tmp_TextOrigin)

    for GetVersetReference in GetVersetReferences:
      tmp_XmlNodeVersetReference = ET.SubElement(tmp_XmlNodeRoot, u'verset')
      for tmp_Key, tmp_Value in GetVersetReference.items():
        tmp_XmlNodeVersetReference.set(tmp_Key, tmp_Value)

    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['TranslationName'], tmp_CurrentTranslation.GetName())
    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['Origin'], tmp_TextOrigin)

    if tmp_Inline:
      tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['Inline'], u'true')

    return tmp_XmlNodeRoot

  def HandleCmd(self, arg_Function, arg_Params):
    return {
        'GetText' : self.HandleCmdGetText,
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

# ================================================================ #
# implementation of module: Sectioning
# ================================================================ #
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
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrEntryItemQuote), None)

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
      tmp_Title = arg_Params[1].strip(cfg_ChrEntryItemQuote)

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
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrEntryItemQuote), None)

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

# ================================================================ #
# implementation of module: Document
# ================================================================ #
class Document(IModule):
  def __init__(self):
    IModule.__init__(self)

  def GetName(self):
    return self.__class__.__name__

# ================================================================ #
# implementation of module: SWORD
# ================================================================ #
# module
class SWORD(IModule):
  def __init__(self):
    IModule.__init__(self)

  def GetName(self):
    return self.__class__.__name__

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
      tmp_Items = Helpers.Entry(tmp_Line).GetItems()

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

