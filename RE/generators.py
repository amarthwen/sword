# -*- coding: utf-8 -*-

import argparse, codecs, os, sys

from modules import RAW, SWORD

# configuration variables
Cfg_CommentChar = u'%'

# check if given line is empty
def CheckIfLineIsEmpty(arg_Line):
  tmp_IsEmpty = False
  if arg_Line != None and len(arg_Line) == 0:
    tmp_IsEmpty = True

  return tmp_IsEmpty

# check if given line is a comment
def CheckIfLineIsComment(arg_Line):
  tmp_IsComment = False
  if arg_Line != None and len(arg_Line) > 0 and arg_Line[0] == Cfg_CommentChar:
    tmp_IsComment = True

  return tmp_IsComment

def main():
  tmp_Parser = argparse.ArgumentParser()
  tmp_Parser.add_argument('OptInput', metavar='FILE', help='input file to be processed')
  tmp_Args = tmp_Parser.parse_args()

  # sanity check
  if not os.path.exists(tmp_Args.OptInput):
    sys.exit(os.EX_OSFILE)

  tmp_ModSWORD = SWORD.SWORD()

  print 'Processing file ' + tmp_Args.OptInput

  with codecs.open(tmp_Args.OptInput, 'r', 'utf-8') as tmp_File:
    tmp_FileContents = [tmp_Line.strip() for tmp_Line in tmp_File.readlines()]

  # remove empty lines and comments
  tmp_FileContents[:] = [tmp_Line for tmp_Line in tmp_FileContents if not CheckIfLineIsEmpty(tmp_Line) and not CheckIfLineIsComment(tmp_Line)]

  # store results temporarily in tmp.txt file
  with codecs.open(os.path.join('.', 'tmp.txt'), 'w+', 'utf-8') as f:
    for tmp_Line in tmp_ModSWORD.Process(tmp_FileContents):
      f.write(tmp_Line + u'\n')

  # try:
    # tmp_ModSWORD.Process(tmp_FileContents)
    # print u'\n'.join(tmp_ModSWORD.Process(tmp_FileContents))
  # except <my_exception>:
    # sys.exit(os.EX_DATAERR)
  # except:
    # sys.exit(os.EX_SOFTWARE)

if __name__ == "__main__":
  main()
