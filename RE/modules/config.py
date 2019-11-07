# -*- coding: utf-8 -*-

# ================================================================ #
# XML namespaces
# ================================================================ #
XmlNamespaceBase = u'https://github.com/amarthwen/sword/xmlns/'

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
  'Normalized' : u'normalized', # origin normalized
  'Origin' : u'origin',
  'TranslationName' : u'translation',
  'Inline' : u'inline' # Optional, default value: true
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
# module: Image
# ================================================================ #
# xml attributes: 'object:image'
ObjectImageXmlAttribs = {
  'Name' : u'name',
  'Caption' : u'caption'
}

# ================================================================ #
# module: Document
# ================================================================ #
# xml attributes: 'document:config'
DocumentConfigXmlAttribs = {
  'Title' : u'title',
  'SubTitle' : u'subtitle',
  'Emblem' : u'emblem'
}

# ================================================================ #
# generators
# ================================================================ #
GenTmpDir = u'./tmp/generators'

# ================================================================ #
# miscellaneous
# ================================================================ #
ParagraphName = u'paragraph'
TextName = u'text'
ImagesTmpDir = u'./tmp/images'
DefaultEmblem = u'default.jpg'

