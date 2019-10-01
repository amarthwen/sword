# -*- coding: utf-8 -*-

# ================================================================ #
# imports
# ================================================================ #
import xml.etree.ElementTree as ET

# ================================================================ #
# implementation of object interface
# ================================================================ #
class IObject:
  def __init__(self):
    pass

  def __str__(self):
    raise NotImplementedError

# ================================================================ #
# implementation of object interface
# ================================================================ #
class ObjectSwordScriptureExtract(IObject):
  def __init__(self, arg_Translation, arg_Origin, arg_Lines):
    IObject.__init__(self)

    self.atr_Translation = arg_Translation
    self.atr_Origin = arg_Origin
    self.atr_Lines = arg_Lines
    self.atr_Root = ET.Element('sword')
    tmp_Scripture = ET.SubElement(self.atr_Root, 'scripture')
    tmp_Scripture.set('translation', self.atr_Translation)
    tmp_Extract = ET.SubElement(tmp_Scripture, 'extract')
    tmp_Extract.set('origin', self.atr_Origin)
    for tmp_Line in self.atr_Lines:
      tmp_LineEntry = ET.SubElement(tmp_Extract, 'line')
      tmp_LineEntry.set('id', str(tmp_Line[1][0]))
      tmp_LineEntry.set('origin', u'/' + tmp_Line[0][0] + u'/' + str(tmp_Line[0][1]) + u'/' + str(tmp_Line[0][2]))
      tmp_LineEntry.text = tmp_Line[1][1]

  def __str__(self):
    # tmp_Output = ET.tostring(self.atr_Root, encoding='utf-8')
    # print tmp_Output
    # return tmp_Output
    return ET.tostring(self.atr_Root)
