# -*- coding: utf-8 -*-

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

    g_contents.append('<p class="css_text">' + text + '</p>')

def AddBibleText(text, origin):
    global g_contents
    global g_lines

    g_contents.append('<p class="css_bible_text">' + text + '</p>')
    g_contents.append('<p class="css_bible_origin">' + origin[1:-1] + '</p>')
    g_lines.append(origin)

def GetTitle():
    return '<p class="css_title">' + g_title + '</p>'

def GetLines(text_lines):
    return '<p class="css_lines"><b>' + text_lines + '</b> ' + ', '.join(g_lines) + '</p>'

def GetContents():
    return ''.join(g_contents)

def GetPage(text_lines):
    return '<html><head><title>' + g_title + '</title><link rel="stylesheet" type="text/css" href="style/basic.css" /></head><body>' + GetTitle() + GetLines(text_lines) + GetContents() + '</body></html>'

