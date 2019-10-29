# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import os, xml.etree.ElementTree as ET
from modules import config, Helpers

# ================================================================ #
# configuration
# ================================================================ #
# The base of all xml namespaces
cfg_XmlNamespaceBase = config.XmlNamespaceBase

# entry item related configuration variables
cfg_ChrEntryItemQuote = config.EntryItemQuoteChr

# translation related configuration variables
cfg_StrTranslationsPath = config.ScriptureTranslationsPath
cfg_StrTranslationExtension = config.ScriptureTranslationExtension

# xml attributes: 'scripture:extract'
cfg_XmlAttrScriptureExtract = config.ScriptureExtractXmlAttribs

# xml attributes: 'sectioning:section'
cfg_XmlAttrSectioningSection = config.SectioningSectionXmlAttribs

# xml attributes: 'image:image'
cfg_XmlAttrObjectImage = config.ObjectImageXmlAttribs

# paragraph name
cfg_StrParagraphName = config.ParagraphName

# ================================================================ #
# implementation of module interface
# ================================================================ #
class IModule(object):
  atr_XmlNamespaceBase = cfg_XmlNamespaceBase

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
  def Get(arg_TranslationName, arg_Exceptional = None):
    return Translations.atr_Translations.get(arg_TranslationName, arg_Exceptional)

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
    tmp_Inline = 'true'

    # sanity check
    if len(arg_Params) == 0:
      raise Exception

    tmp_Origin = arg_Params[0].strip(cfg_ChrEntryItemQuote)

    if len(arg_Params) > 1:
      if arg_Params[1].lower() in [u'false', u'true']:
        tmp_Inline = arg_Params[1].lower()

    tmp_XmlNodeRoot = ET.Element(self.GetXmlTagName(u'extract'))

    tmp_CurrentTranslation = Translations.GetCurrent()

    if tmp_CurrentTranslation is None:
      raise Exception

    tmp_VersetReferences, tmp_NormalizedOrigin = tmp_CurrentTranslation.GetVersetReferencesWithNormalizedOrigin(tmp_Origin)

    for tmp_VersetReference in tmp_VersetReferences:
      tmp_XmlNodeVersetReference = ET.SubElement(tmp_XmlNodeRoot, u'verset')
      for tmp_Key, tmp_Value in tmp_VersetReference.items():
        tmp_XmlNodeVersetReference.set(tmp_Key, tmp_Value)

    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['TranslationName'], tmp_CurrentTranslation.GetName())
    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['Normalized'], tmp_NormalizedOrigin)
    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['Origin'], tmp_Origin)
    tmp_XmlNodeRoot.set(cfg_XmlAttrScriptureExtract['Inline'], tmp_Inline)

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
    'document' : 0,
    'section' : 1,
    'subsection' : 2,
    'subsubsection' : 3,
    'paragraph' : 4,
    'subparagraph' : 5
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
    tmp_Title = None

    # sanity check
    if len(arg_Params) == 0:
      raise Exception

    # get requested level
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrEntryItemQuote).lower(), None)

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
    tmp_TagName = self.GetXmlTagName(u'section')

    if tmp_Level == 0:
      tmp_XmlNode = ET.Element(tmp_TagName)
    else:
      tmp_XmlNode = ET.SubElement(self.atr_XmlPath[tmp_Level - 1], tmp_TagName)

    tmp_XmlNode.set(cfg_XmlAttrSectioningSection['Level'], str(tmp_Level))

    if tmp_Title is not None:
      tmp_XmlNode.set(cfg_XmlAttrSectioningSection['Title'], tmp_Title)

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
    tmp_Level = self.atr_Levels.get(arg_Params[0].strip(cfg_ChrEntryItemQuote).lower(), None)

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
  def GetLevelName(arg_Level, arg_Exceptional = None):
    tmp_LevelName = arg_Exceptional

    for tmp_Key, tmp_Value in Sectioning.atr_Levels.items():
      if tmp_Value == arg_Level:
        tmp_LevelName = tmp_Key
        break;

    return tmp_LevelName

# ================================================================ #
# implementation of module: Object
# ================================================================ #
class Object(IModule):
  def __init__(self):
    IModule.__init__(self)

  def GetName(self):
    return self.__class__.__name__

  def HandleCmdImage(self, arg_Params):
    tmp_XmlNode = None
    tmp_FileName = None
    tmp_Caption = None

    # sanity check
    if len(arg_Params) == 0:
      raise Exception

    # get requested level
    tmp_FileName = arg_Params[0].strip(cfg_ChrEntryItemQuote)

    if len(arg_Params) > 1:
      tmp_Caption = arg_Params[1].strip(cfg_ChrEntryItemQuote)

    tmp_XmlNode = ET.Element(self.GetXmlTagName(u'image'))
    tmp_XmlNode.set(cfg_XmlAttrObjectImage['Name'], tmp_FileName)
    if tmp_Caption is not None:
      tmp_XmlNode.set(cfg_XmlAttrObjectImage['Caption'], tmp_Caption)

    return tmp_XmlNode

  def HandleCmd(self, arg_Function, arg_Params):
    return {
      'Image' : self.HandleCmdImage
    }.get(arg_Function, self.HandleCmdUnknown)(arg_Params)

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

  def GetModules(self):
      return self.atr_Modules
