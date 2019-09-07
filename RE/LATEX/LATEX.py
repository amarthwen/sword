# -*- coding: utf-8 -*-

import os
import subprocess

g_contents = []
g_lines = []
g_title = u''

def Init():
    global g_contents
    global g_lines
    global g_title

    del g_contents[:]
    del g_lines[:]
    g_title = u''

def SetTitle(title):
    global g_title

    g_title = title

def AddText(text):
    global g_contents

    elements = [
        '\\begin{paragraph}',
        text,
        '\\end{paragraph}'
    ]

    # g_contents.append('\r\n'.join(elements))
    g_contents.append(text)

def AddBibleText(text, origin):
    global g_contents
    global g_lines

    origin_within_mbox = '\\mbox{' + origin + '}'

    elements = [
        '\\begin{quote}',
         ',,' + text.replace('(...)', '(\ldots)') + '\'\' ' + origin_within_mbox,
        '\\end{quote}'
    ]

    g_contents.append('\r\n'.join(elements))
    g_lines.append(origin_within_mbox)

def GetTitle():
    return '\\centerline{\\textbf{\\MakeUppercase{' + g_title + '}}}'

def GetLines(text_lines):
    elements = [
        '\\begin{center}',
        '\\textbf{' + text_lines + '} ' + ', '.join(g_lines),
        '\\end{center}'
    ]

    return '\r\n'.join(elements)

def GetContents():
    return '\r\n'.join(g_contents)

def GetPage(text_lines):
    elements = [
        '\\documentclass[10pt,a4paper,oneside]{article}',
        '\\usepackage[utf8]{inputenc}',
        '\\usepackage{polski}',
        '\\usepackage[polish]{babel}',
        '\\usepackage[margin=0.5in,bottom=0.75in]{geometry}',
        '\\begin{document}',
        GetTitle(),
        GetLines(text_lines),
        GetContents(),
        '\\end{document}'
    ]

    return '\r\n'.join(elements)

