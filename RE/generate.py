# -*- coding: utf-8 -*-

import argparse, codecs, os, sys

from modules import Generators

# configuration variables
Cfg_ChrComment = '#'

def main():
  tmp_Parser = argparse.ArgumentParser()
  tmp_Parser.add_argument('OptInput', metavar='FILE', help='input file to be processed')
  tmp_Args = tmp_Parser.parse_args()

  # sanity check
  if not os.path.exists(tmp_Args.OptInput):
    sys.exit(os.EX_OSFILE)

  print 'Processing file: "' + tmp_Args.OptInput + '"'

  with codecs.open(tmp_Args.OptInput, 'r', 'utf-8') as tmp_File:
    tmp_FileContents = [tmp_Line.strip() for tmp_Line in tmp_File.readlines()]

  # remove empty lines and comments
  tmp_FileContents[:] = [tmp_Line for tmp_Line in tmp_FileContents if len(tmp_Line) > 0 and tmp_Line[0] != Cfg_ChrComment]

  # create instance of modules
  tmp_Mods = Modules.Modules()

  # register modules
  tmp_Mods.Register(Modules.Sword())

  tmp_

  # create instance of generators
  tmp_Gens = Generators.Generators()

  # register generators
  tmp_Gens.Register(Generators.Text())
  # tmp_Gens.Register(Generators.HTML())
  # tmp_Gens.Register(Generators.ODT())
  # tmp_Gens.Register(Generators.PDF())

  tmp_Gens.Process(tmp_FileContents)

if __name__ == "__main__":
  main()
