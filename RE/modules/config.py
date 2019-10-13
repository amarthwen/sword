# -*- coding: utf-8 -*-

# ================================================================ #
# helper: Entry
# ================================================================ #
EntryItemQuoteChr = u'"'

# ================================================================ #
# module: Scripture
# ================================================================ #
# Scripture: path to stored translations
ScriptureTranslationsPath = 'Scripture/translations'

# Scripture: default translation extension
ScriptureTranslationExtension = '.xml'

# Scripture: text origin related configuration
ScriptureTextOriginDelimiterChapter = r';'
ScriptureTextOriginDelimiterChapterInternal = r','
ScriptureTextOriginDelimiterVersetRange = r'.'
ScriptureTextOriginDelimiterVersetRangeInternal = r'-'
ScriptureTextOriginDelimiterReferenceRange = r'..'

# xml attributes: 'scripture:extract'
ScriptureExtractXmlAttribs = {
  'Origin' : u'origin',
  'TranslationName' : u'translation',
  'Inline' : u'inline' # Optional, default value: false
}

# xml attributes: 'scripture:extract/verset'
ScriptureExtractVersetXmlAttribs = {
  'Origin' : u'origin',
  'Reference' : u'ref'
}

# ================================================================ #
# module: Sectioning
# ================================================================ #
# xml attributes: 'sectioning:section'
SectioningSectionXmlAttribs = {
  'Level' : u'level',
  'Title' : u'title'
}

# ================================================================ #
# generator: TXT
# ================================================================ #
GenTXTQuoteChr = u'"'
GenTXTVersetDelimiterStr = u' (...) '

