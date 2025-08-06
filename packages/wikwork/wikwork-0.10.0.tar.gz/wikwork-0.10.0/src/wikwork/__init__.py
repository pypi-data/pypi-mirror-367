#   Use REST APIs to get word and audio file info from Wiktionary
#   Copyright (C) 2024 Ray Griner (rgriner_fwd@outlook.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

"""Use Wikimedia™ REST APIs to get word and audio file info from Wiktionary™.

SUMMARY
-------
This package uses Wikimedia REST APIs to retrieve word and audio file
information from Wiktionary. Audio files selected by the user can also be
downloaded for most languages. There is also functionality to parse the
dictionary entries for German, Polish, and Czech words to extract much of
the page information as object attributes.

TRADEMARK NOTICE
----------------
Wiktionary, Wikimedia, Wikidata, Wikimedia Commons, and MediaWiki are
trademarks of the Wikimedia Foundation and are used with the permission of
the Wikimedia Foundation. We are not endorsed by or affiliated with the
Wikimedia Foundation.

WIKIMEDIA API TERMS AND CONDITIONS
----------------------------------
The REST APIs used are an interface provided by Wikimedia. The version
used is version 1. APIs from two sets of Wikimedia APIs are used. For want of
a better term, we refer to these as 'old' and 'new' API sets. See the
API documentation for global rules, content licensing, and terms of service.

The documentation for the 'old' `/page/media-list/{title}/{revision}` API
(which is used to get the list of audio files associated with a headword)
is at:
   https://[xx].wiktionary.org/api/rest_v1, where
[xx] is replaced by the language code of the Wiktionary (eg,
   https://en.wiktionary.org/api/rest_v1 for the English Wiktionary).

The documentation for the new set of APIs (all other APIs used by the package)
is at:
   https://api.wikimedia.org/wiki/Core_REST_API

# Release Notes (v0.10.0)
- Allow headwords to contain '…' (U+2026, horizontal ellipsis),
  '’' (U+2019, right single quote), and '–' (U+2013, en dash).
- Add `lemma_main_form` attribute to `GermanEntry` class and populate it
  from the `Lemmaverweis` template.

FUNCTIONALITY AND MOTIVATION
----------------------------
This package extracts word and audio file information from Wiktionary.
Audio files selected by the user can also be downloaded. For German,
Polish, and Czech words, the most common elements of the dictionary entry
or entries for a word can be extracted into separate fields. Similar
functionality may be added in the future for other languages, or users can
write their own parsers on the downloaded objects.

Downloading all audio files for a given headword (ie, page or page title)
technically only requires two REST API calls, one to get the list of audio
files for the headword and then to download the audio file. However, doing
this and nothing else would ignore the downloader's potential attribution
and other responsibilities imposed by the file licenses. Furthermore, the
audio files obtained from the media list API for a given headword should
consist of all audio files from the headword page, including those in
languages other than the one in which the Wiktionary is written.

OTHER CONSIDERATIONS
--------------------
1. The following page has other useful points to consider when deciding
whether or how to use downloaded media:
    https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia

See the README in the PyPI repository for more details and example code.

"""

#------------------------------------------------------------------------------
# File:    __init__.py
# Date:    2024-02-29
# Author:  Ray Griner
# Changes:
# 20240301RG: Add __author__, __version__, and __all__
# 20240908RG: Align doc with ../../README.md. Going forward, will aim to just
#  have the docstring be the README.md copied, with (1) section headers
#  formatted with all caps and hyphens to underline the header, and (2) the
#  triple backquotes in README.md removed.
#------------------------------------------------------------------------------
__author__ = 'Ray Griner'
__version__ = '0.10.0'
__all__ = ['io_options','page_media','wrapper']

import logging

from .page_media import Headword, AudioFile
from .io_options import IOOptions

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

