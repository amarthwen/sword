# -*- coding: utf-8 -*-

import re

from modules import config

glb_RegExpStrModuleToken = '([' + config.StrModuleTokenCharSet + ']+)'
glb_RegExpStrModuleRoot = glb_RegExpStrModuleToken
glb_RegExpStrModuleElementParameterList = '(?:{"(.*)"}){0,1}'
glb_RegExpStrModuleElement = glb_RegExpStrModuleToken + glb_RegExpStrModuleElementParameterList
glb_RegExpStrModule = '^' + config.StrModuleLeadingChar + glb_RegExpStrModuleRoot + '(?:' + config.StrModuleElementSeparator + glb_RegExpStrModuleElement + ')*' + '$'
glb_RegExpBinModuleElement = re.compile(glb_RegExpStrModuleElement, re.UNICODE | re.IGNORECASE)
glb_RegExpBinModule = re.compile(glb_RegExpStrModule, re.UNICODE | re.IGNORECASE)

# process line and return module if present
def GetModule(arg_Line):
  tmp_Module = None

  tmp_Rslt = glb_RegExpBinModule.match(arg_Line)

  if tmp_Rslt:
    tmp_ModuleElements = []
    tmp_Module = {
      'id' : tmp_Rslt.groups()[0],
      'elements' : tmp_ModuleElements
    }

    for tmp_ModuleElement in arg_Line.split(config.StrModuleElementSeparator)[1:]:
      tmp_Rslt = glb_RegExpBinModuleElement.match(tmp_ModuleElement)

      if tmp_Rslt:
        tmp_ModuleElements.append(tmp_Rslt.groups())

  return tmp_Module
