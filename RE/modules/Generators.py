# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import codecs, os
import xml.etree.ElementTree as ET

# ================================================================ #
# implementation of generator interface
# ================================================================ #
class iGenerator:
  def __init__(self):
    pass

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    self.WriteContents(arg_FileName, u'Generated with generator: "' + self.GetName() + '"', arg_OutputFolderName)

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
    # print '> registering generator: "' + tmp_GeneratorName + '"'

    if tmp_GeneratorName not in self.atr_Generators:
      self.atr_Generators[tmp_GeneratorName] = arg_Generator

  def Process(self, arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName):
    for tmp_Generator in self.atr_Generators.values():
      tmp_Contents = tmp_Generator.Process(arg_FileName, arg_XmlNodeRoot, arg_OutputFolderName)

