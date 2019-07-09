# -*- coding: utf-8 -*-
import re

g_delimiter_boundary = r'#'
g_delimiter_divider = r'/'
g_delimiter_chapter = r';'
g_delimiter_chapter_internal = r','
g_delimiter_line_range = r'.'
g_delimiter_line_range_min_max = r'-'

def GetBibleContents(filename):
    tmp_contents = []

    with open(filename) as f:
        tmp_contents = f.readlines()
    tmp_contents = [line.strip() for line in tmp_contents] 

    return tmp_contents

# Bible line:
#   [0] - ID
#   [1] - book
#   [2] - chapter
#   [3] - line
#   [4] - text
def ParseBibleContents(contents):
    # list of parsed lines
    tmp_lines = []

    # regular expressions
    tmp_re_line_text = g_delimiter_divider + r'(\d*\D+)' + g_delimiter_divider + r'(\d+)' + g_delimiter_divider + r'(\d+)[ ]+\'(.*)\''

    # compile regular expression
    tmp_re_line_comp = re.compile(tmp_re_line_text, re.UNICODE | re.IGNORECASE)

    # iterator
    i = 0

    for tmp_line in contents:
        tmp_result = tmp_re_line_comp.match(tmp_line)
        if tmp_result:
            tmp_groups = tmp_result.groups()
            tmp_lines.append((i, tmp_groups[0].decode('utf-8'), int(tmp_groups[1]), int(tmp_groups[2]), tmp_groups[3]))
            i = i + 1

    return tmp_lines

def PrepareQuery():
    # prepare regular expression - range
    tmp_re_range_text = r'\d+(?:' + g_delimiter_line_range_min_max + r'\d+){0,1}'
    tmp_re_multiple_range_text = tmp_re_range_text + r'(?:' + g_delimiter_line_range + tmp_re_range_text + r')*'

    # prepare regular expression - chapter
    tmp_re_chapter_text = r'(?:\d+' + g_delimiter_chapter_internal + tmp_re_multiple_range_text + r')'
    tmp_re_multiple_chapters_text = tmp_re_chapter_text + r'(?:' + g_delimiter_chapter + tmp_re_chapter_text + r')*'

    # prepare regular expression - query
    tmp_re_query_text = r'^' + g_delimiter_boundary + r'\((\d*\D+)('+ tmp_re_multiple_chapters_text + r')\)' + g_delimiter_boundary + r'$'

    # compile regular expression
    tmp_re_query_comp = re.compile(tmp_re_query_text, re.UNICODE | re.IGNORECASE)

    return tmp_re_query_comp

# Bible line:
#   [0] - book
#   [1] - chapter
#   [2] - line
def ParseQueryContents(query):
    tmp_lines = []

    tmp_re_query_comp = PrepareQuery()
    tmp_re_query_result = tmp_re_query_comp.match(query.replace(u' ', u''))
    if tmp_re_query_result:
        tmp_re_query_groups = tmp_re_query_result.groups()
        tmp_chapters = tmp_re_query_groups[1].split(g_delimiter_chapter)
        for tmp_chapter in tmp_chapters:
            tmp_chapter_info = tmp_chapter.split(g_delimiter_chapter_internal)
            tmp_chapter_nr = int(tmp_chapter_info[0])
            tmp_line_ranges = tmp_chapter_info[1].split(g_delimiter_line_range)
            for tmp_range in tmp_line_ranges:
                tmp_range_min_max = tmp_range.split(g_delimiter_line_range_min_max)
                if len(tmp_range_min_max) == 1:
                    tmp_lines.append((tmp_re_query_groups[0], tmp_chapter_nr, int(tmp_range_min_max[0])))
                else:
                    tmp_line_min = int(tmp_range_min_max[0])
                    tmp_line_max = int(tmp_range_min_max[1])
                    if tmp_line_min > tmp_line_max:
                        tmp_line_mid = tmp_line_min
                        tmp_line_min = tmp_line_max
                        tmp_line_max = tmp_line_mid
                    for i in range(tmp_line_min, tmp_line_max + 1):
                        tmp_lines.append((tmp_re_query_groups[0], tmp_chapter_nr, i))

    return tmp_lines

def GetBibleLineID(parsed_contents, tmp_query_line):
    tmp_id = -1
    for tmp_item in parsed_contents:
        if tmp_query_line == tmp_item[1:4]:
            tmp_id = tmp_item[0];
            break;
    return tmp_id

def GetBibleText(parsed_contents, query_lines):
    tmp_bible_text = []
    tmp_previous_id = -1

    for tmp_query_line in query_lines:
        tmp_id = GetBibleLineID(parsed_contents, tmp_query_line)
        if tmp_id >= 0:
            if tmp_previous_id >= 0 and tmp_id != tmp_previous_id + 1:
                tmp_bible_text.append(u'(...)')
            tmp_bible_text.append(parsed_contents[tmp_id][4].decode('utf-8'))
            tmp_previous_id = tmp_id
        else:
            del tmp_bible_text[:]
            break

    return tmp_bible_text

def GetBibleLines(bible_filename, query):
    tmp_bible_contents = GetBibleContents(bible_filename)
    tmp_bible_parsed_contents = ParseBibleContents(tmp_bible_contents)
    tmp_bible_query_lines = ParseQueryContents(query.decode('utf-8'))
    tmp_bible_text = GetBibleText(tmp_bible_parsed_contents, tmp_bible_query_lines)

    return tmp_bible_text

