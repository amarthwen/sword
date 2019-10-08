# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import Modules
import xml.etree.ElementTree as ET

# ================================================================ #
# implementation of generator interface
# ================================================================ #
class iGenerator:
  def __init__(self):
    self.atr_Modules = Modules.Modules()

  def __str__(self):
    return self.GetName()

  def GetName(self):
    raise NotImplementedError

  def Process(self, arg_FileContents):
    # print '> generator running: "' + self.GetName() + '"'
    return self.atr_Modules.Process(arg_FileContents)

  def Register(self, arg_Module):
    self.atr_Modules.Register(arg_Module)

# ================================================================ #
# implementation of generator: Text
# ================================================================ #
# generator
class Text(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

    self.Register(Modules.SWORD())

  def GetName(self):
    return 'text'

# ================================================================ #
# implementation of generator: HTML
# ================================================================ #
# generator
class HTML(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

    self.Register(Modules.Document())

  def GetName(self):
    return 'html'

# ================================================================ #
# implementation of generator: ODT
# ================================================================ #
# generator
class ODT(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return 'odt'

# ================================================================ #
# implementation of generator: PDF
# ================================================================ #
# generator
class PDF(iGenerator):
  def __init__(self):
    iGenerator.__init__(self)

  def GetName(self):
    return 'pdf'

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

  def Process(self, arg_FileContents):
    for tmp_GeneratorName, tmp_Generator in self.atr_Generators.items():
      tmp_XmlNodeRoot = tmp_Generator.Process(arg_FileContents)
      print ET.tostring(tmp_XmlNodeRoot, encoding='utf-8')
      # print 'generator: "' + tmp_Generator.GetName() + '", text: "' + tmp_Text + '"'
