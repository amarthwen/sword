# -*- coding: utf-8 -*-
import os
import sys
import codecs
import os
import sys
from SWORD import SWORD
from HTML import HTML
from LATEX import LATEX

output_folder_txt = u'txt'
output_folder_html = u'html'
output_folder_latex = u'latex'
output_folder_pdf = u'pdf'

def print_file_contents(bible_parsed_contents, dir_input, dir_output, filename):
    tmp_title = os.path.splitext(filename)[0]

    with open(os.path.join(dir_input, filename)) as f:
        tmp_contents = f.readlines()
    tmp_contents = [line.strip() for line in tmp_contents]

    tmp_text = [tmp_title.decode('utf-8')]

    HTML.Init()
    LATEX.Init()

    HTML.SetTitle(tmp_title.decode('utf-8'))
    LATEX.SetTitle(tmp_title.decode('utf-8'))

    for tmp_query in tmp_contents:
        tmp_bible_query_lines = SWORD.ParseQueryContents(tmp_query.decode('utf-8'))
        tmp_bible_text = SWORD.GetBibleText(bible_parsed_contents, tmp_bible_query_lines)

        if len(tmp_bible_text):
            tmp_bible_text_joined = u' '.join(tmp_bible_text)
            tmp_quoted_text = u'"' + tmp_bible_text_joined + u'"'
            tmp_query_stripped = tmp_query.decode('utf-8').replace(SWORD.g_delimiter_boundary, u'')

            tmp_text.append(u'* ' + tmp_quoted_text + u' ' + tmp_query_stripped)
            HTML.AddBibleText(tmp_quoted_text, tmp_query_stripped)
            LATEX.AddBibleText(tmp_bible_text_joined, tmp_query_stripped)
        else:
            tmp_text.append(tmp_query.decode('utf-8'))
            HTML.AddText(tmp_query.decode('utf-8'))
            LATEX.AddText(tmp_query.decode('utf-8'))

    with codecs.open(os.path.join(dir_output + u'/' + output_folder_txt, tmp_title.decode('utf-8') + '.txt'), 'w', 'utf-8') as f:
        f.write('\r\n'.join(tmp_text))

    with codecs.open(os.path.join(dir_output + u'/' + output_folder_html, tmp_title.decode('utf-8') + '.html'), 'w', 'utf-8') as f:
        f.write(HTML.GetPage(u'Wersety do studium:'))

    with codecs.open(os.path.join(dir_output + u'/' + output_folder_latex, tmp_title.decode('utf-8') + '.tex'), 'w', 'utf-8') as f:
        f.write(LATEX.GetPage(u'Wersety do studium:'))

if len(sys.argv) < 3:
    print 'error: please give at least three arguments: source, input directory and output directory'
    exit(1)

tmp_source = sys.argv[1]
tmp_dir_input = sys.argv[2]
tmp_dir_output = sys.argv[3]

tmp_bible_contents = SWORD.GetBibleContents(tmp_source)
tmp_bible_parsed_contents = SWORD.ParseBibleContents(tmp_bible_contents)

for filename in os.listdir(tmp_dir_input):
    if filename.endswith('.txt'):
        print_file_contents(tmp_bible_parsed_contents, tmp_dir_input, tmp_dir_output, filename)

