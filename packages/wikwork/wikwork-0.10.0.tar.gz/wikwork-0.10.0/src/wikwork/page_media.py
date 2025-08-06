#    Classes for information about words and audio files
#    Copyright (C) 2024 Ray Griner (rgriner_fwd@outlook.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

""" Classes for information about words and audio files. """

#------------------------------------------------------------------------------
# File:    wrapper.py
# Author:  Ray Griner
# Date:    2024-02-29
# Changes:
# 20240301RG: Add __author__ and __all___
# 20240304RG: Fix so prob_author removes the 'author=' prefix
# 20240908RG: (1) Allow user to download audios. Uncomment code in
# `Headword._fetch_audio` and `AudioFile._fetch_audio`. (2) new functions to
# copy HTML/wikitext for audio files whose download is requested to a separate
# directory for easier review (`Headword.copy_req_html_and_wtxt` and
# `AudioFile.copy_req_html_and_wtxt`). (3) comment out entirely
# `Headword._copy_one_audio`. The body was already commented out, but this will
# omit it from docstring too.
#
# 20250125RG: Program stopped working sometime between the present and the last
# week of November 2024. The old API paths were still able to retrieve the page
# for the headword but no longer correctly retrieved the pages for the audio
# files.
#   Old path:  https://{lang_code}.wiktionary.org/api/rest_v1
#   New path:  https://api.wikimedia.org/core/v1/{project}, where project=
#     'wiktionary' or 'commons' depending on whether the page for the word
#     or the page for the audio file is requested.
# No documentation observed on when or why the old way was deprecated. The new
# way does have an advantage in that it is now simpler to get the wiki text
# for a page. It can be retrieved in a single GET request. With the old APIs
# it was necessary to get the HTML and then send a POST with the 'etag' and
# HTML data. Since we no longer need the etag, it will probably be deprecated
# in the future in this program, but for now we still save it when retrieving
# the HTML. We might in the future also make retrieval of the HTML optional.
# We have kept the old API for getting the list of media files fow now, but
# we might support the new API for this in the future.
# 20250625RG: (1) Add `timestamp` attribute to `Headword` class;
#   (2) Only call `_download_html` if `io_options.fetch_html` is True (in
#       `fetch_word_page` and `fetch_audio_info`);
#   (3) Rename `_html_to_wikitext` to `_download_wikitext` since as of previous
#       version it downloads the wikitext directly instead of converting the
#       HTML.
#------------------------------------------------------------------------------
__author__ = 'Ray Griner'
__all__ = ['AudioFile','Headword']

# Standard modules
import os
import shutil
import re
import json
import time
import collections
import logging
from collections.abc import Callable
from typing import Any, Union, Tuple, Optional, Dict
import urllib
from wikwork import io_options as io_opts
from wikwork import parse

# Third party package
import requests

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
# Type aliases
#------------------------------------------------------------------------------
#HttpHeaders = Dict[str, str]
MediaList = Any
AudioReqs = Dict[str, Tuple[int, str]]
SortKey = Callable[['AudioFile'], Any]
_LangInfo = collections.namedtuple('_LangInfo',
                                   'english_name filename_pattern')

#------------------------------------------------------------------------------
# Private module-level functions
#------------------------------------------------------------------------------
def _is_valid_lang_code(lang_code: str) -> bool:
    word_re = re.compile(r'[^abcdefghijklmnopqrstuvwxyz-]')
    if word_re.search(lang_code):
        return False
    else:
        return True

def _is_valid_headword(word: str) -> bool:
    # example with '’': halt’s Maul (de.wiktionary.org)
    # example with '…': nichts wie … (de.wiktionary.org)
    # hyphen is intentionally unquoted below, see `_is_valid_filename` for
    # details.
    word_re = re.compile(r"[^\w '-\.…’–]")
    if word_re.search(word) or word == '..' or word == '.' or '_' in word:
        return False
    else:
        return True

def _is_valid_filename(filename: str) -> bool:
    filename = str.strip(filename.replace(' ','_'))
    # hyphen is intentionally unquoted below to include the characters
    # betwen "'" and '.': "'", '(', ')', '+', '*', ',', '-', '.'.
    filename_re = re.compile(r"[^\w'-\.…’–]")
    if (filename_re.search(filename)
           or filename == '.' or filename == '..'):
        logger.warning('File: %s: name not valid', filename)
        return False
    else:
        return True

def _assign_pattern(lang_code: str,
        filename_pattern: Optional[str] = None) -> str:
    """Assign pattern used to guess if audio file is right language."""

    lang_info_dict = {
        'de' : _LangInfo('German',     r'^LL.*\(deu\)|^[Dd]e-'),
        'ar' : _LangInfo('Arabic',     r'^LL.*\(ara\)|^[Aa]r-'),
        'en' : _LangInfo('English',    r'^LL.*\(eng\)|^[Ee]n-'),
        'es' : _LangInfo('Spanish',    r'^LL.*\(spa\)|^[Ee]s-'),
        'fr' : _LangInfo('French',     r'^LL.*\(fra\)|^[Ff]r-'),
        'ru' : _LangInfo('Russian',    r'^LL.*\(rus\)|^[Rr]u-'),
        'pl' : _LangInfo('Polish',     r'^LL.*\(pol\)|^[Pp]l-'),
        'cs' : _LangInfo('Czech',      r'^LL.*\(cze\)|^[Cc]s-'),
        'sv' : _LangInfo('Swedish',    r'^LL.*\(sve\)|^[Ss]v-'),
        'zh' : _LangInfo('Chinese',    r'^LL.*\(zho\)|^[Zz]h-'),
        'hi' : _LangInfo('Hindi',      r'^LL.*\(hin\)|^[Hh]i-'),
        'mg' : _LangInfo('Malagasy',   r'^LL.*\(mal\)|^[Mm]g-'),
        'pt' : _LangInfo('Portuguese', r'^LL.*\(por\)|^[Pp]t-'),
        'ja' : _LangInfo('Japanese',   r'^LL.*\(jap\)|^[Jj]a-'),
        'uk' : _LangInfo('Ukrainian',  r'^LL.*\(ukr\)|^[Uu]k-'),
    }

    filename_pattern_str: str
    if (not filename_pattern) and lang_code in lang_info_dict:
        filename_pattern_str = lang_info_dict[lang_code].filename_pattern
    elif not filename_pattern:
        raise ValueError('No pre-specified filename_pattern available '
                         f'for lang_code={lang_code} so filename_pattern '
                         'parameter must be specified')
    else:
        filename_pattern_str = filename_pattern

    #return fnsp_prefix_str, filename_pattern_str
    return filename_pattern_str

def _quote_url(s: str) -> str:
    #return urllib.parse.quote(s.replace(' ','_'), safe='')
    return urllib.parse.quote(s, safe='')

def _should_audio_item_be_skipped(item: dict[str, Any],
                                  filename_pattern_str: str) -> bool:
    if item['title'].count(':') != 1:
        logger.warning('File %s: skipped, 0 or >1 colon', item['title'])
        return True
    else:
        filename_not_safe = item['title'].split(':')[1]

    if not item['audio_type'] in ['pronunciation','generic']:
        logger.warning('File %s: skipped because audio_type=%s',
                       filename_not_safe, item['audio_type'])
        return True

    if not re.search(filename_pattern_str, filename_not_safe):
        # Maybe should even be logger.debug instead
        logger.info('File %s: skipped because pattern does not match',
                    filename_not_safe)
        return True

    return False

#------------------------------------------------------------------------------
# Class definitions
#------------------------------------------------------------------------------
class AudioFile:
    r"""Audio file and relate page information (license, author, etc...).

    Attributes
    ----------
    revision : int
        Page revision. Used when requesting html and wikitext to ensure
        these correspond to the same revision. Set to 0 upon
        initialization and so will be 0 if processing halted before the
        revision was downloaded (eg, if valid_input == False).
    status_msg : str
        Status message indicating any problems processing the file
    html : str, optional
        HTML for the page with information about the audio file. Empty if
        problem loading or loading never requested.
    html_etag : str, optional
        eTag information in header when HTML was downloaded. This is stored
        as it needs to be passed when requesting the wikitext.
    wikitext : str, optional
        Wikitext for the page+revision. Empty if problem loading or loading
        never requested.
    prob_authors : list[str], optional
        Probable authors. Derived from parsing the wikitext as described
        in the `parse_audio_wikitext` documentation. Users should compare
        this with the `wikitext` output to confirm correct extraction
        before using.
    prob_licenses : list[str], optional
        Probable licenses. Derived from parsing the wikitext as described
        in the `parse_audio_wikitext` documentation. Users should compare
        this with the `wikitext` output to confirm correct extraction
        before using.
    prob_attribs: list[str], optional
        Probable attributions. Derived from parsing the wikitext as
        described in the `parse_audio_wikitext` documentation. Users
        should compare this with the `wikitext` output to confirm correct
        extraction before using.
    prob_templates: list[WikiTemp], optional
        Parsed templates used when populating `prob_licenses`,
        `prob_attribs`, and `prob_authors`.
    request_status : str
        Contains information whether the `filename` and `revision` are in
        the dict passed in the `input_audio_reqs` parameter for the
        `Headword` object to which this `AudioFile` belongs.

        Takes values based on whether this object had download requested
        (per the `input_audio_reqs` value passed for the `Headword` object
        this `AudioFile` belongs to). The value 'Unknown' is is set
        upon initialization. It will be reset to another value unless
        processing of the file stops before checking the dict or download
        (ie, if filename was set to an empty string)

        The next six values are set if `request_download` is 'Y', 'N', or
        '' and depending on whether or not self.revision matches the dict
        revision:
            'Requested', 'Requested, but revision out of date'
            'Not requested', 'Not requested, but revision out of date'
            'No decision', 'No decision, but revision out of date'
        Note that 'No decision' is also used if the filename is not empty
        and not in the passed dict. Any other case other than described
        above gives: 'Request decision not valid'.
    download_status : str
        'Not applicable'. For future use.

    """

    # Properties
    _html_lang_code: str
    _filename: str
    _title_uncoded: str
    _title_uncoded_osd: str
    _filename_not_safe: str
    _headword: str
    _headword_lang_code: str
    _media_list_position: Optional[int]

    _desc = 'Audio'

    def __init__(self, filename: str, headword: str, headword_lang_code: str,
                 media_list_position: Optional[int]):
        """Initialize instance, but no retrieval of data from internet/cache.

        Logs a warning and continues with '_' replacing ' ' if filename
        contains ' '. If filename is otherwise invalid, sets filename,
        title_uncoded, and title_uncoded_osd to ''.

        Parameters
        ----------
        filename : str
            Filename of the audio file. Typically this is obtained from
            calling the media list REST API for a headword. In the returned
            items, the 'title' field lists the filename as a two-part name
            separated by ':' (eg, "File:en-us-still.ogg") and the second
            part is passed to this parameter.

        headword : str
            If the audio filename was obtained by calling the media list
            API for a headword, the headword and headword_lang_code can be
            provided, and `set_headword_info` will be called to set
            `prob_headword`, a variable indicating whether the filename
            indicates the audio file is probably the pronunciation of the
            headword.

        headword_lang_code : str
            Language code specifying the language of the Wiktionary™ used to
            retrieve the headword. See headword for details.

        media_list_position : int, optional
            Position of the item (starting at 0) in the list of items
            returned by the REST API call of the headword.

        Trademark Notice
        ----------------
        Wiktionary is a trademark of the Wikimedia Foundation and is used
        with the permission of the Wikimedia Foundation. We are not
        endorsed by or affiliated with the Wikimedia Foundation.
        """
        if ' ' in filename:
            logger.warning(("Audiofile: %s: unexpected ' ' will be "
                            "converted to '_'"),
                    filename)
        if _is_valid_filename(filename):
            self._filename = filename.replace(' ','_')
            fnsp_prefix = 'File:'
            self._title_uncoded = fnsp_prefix + filename.replace(' ','_')
            if os.name == 'posix':
                self._title_uncoded_osd = self._title_uncoded
            else:
                self._title_uncoded_osd = (
                    # Code point U+A789 looks like a colon but isn't and
                    # will be used because Windows file systems cannot
                    # have colon in the file name.
                    fnsp_prefix.replace(':', '\ua789') +
                    filename.replace(' ','_'))
            self.status_msg = ''
        else:
            self._filename = ''
            self._title_uncoded = ''
            self._title_uncoded_osd = ''
            self.status_msg = 'Filename not valid'
        self._filename_not_safe = filename
        self.revision: int = 0
        self.html: str = ''
        self.html_etag: str = ''
        self.wikitext: str = ''
        self.prob_licenses: Optional[list[str]] = None
        self.prob_authors: Optional[list[str]] = None
        self.prob_attribs: Optional[list[str]] = None
        self.prob_templates: Optional[list[parse.WikiTemp]] = None
        self.download_status: str = 'Unknown'
        self.request_status: str = 'Unknown'
        self.set_headword_info(headword=headword,
                               headword_lang_code=headword_lang_code,
                               media_list_position=media_list_position)

    @property
    def lang_code(self) -> str:
        """Language code specifying the language of the Wiktionary."""
        return self._lang_code

    #@lang_code.setter
    #def lang_code(self, lang_code: str) -> None:
    #    if _is_valid_lang_code(lang_code):
    #        self._lang_code = lang_code
    #    else:
    #        raise ValueError(f'IOOptions: {lang_code=} can only contain [a-z]'
    #                         ' and "-"')
    @property
    def desc(self) -> str:
        """A class variable always equal to 'Audio' used in log messages."""
        return self._desc

    @property
    def filename(self) -> str:
        """Name of the audio file.

        This is not the html/wikitext page that contains information about
        the file, but rather the file itself (ie, usually an .ogg file).
        This is the name passed into the constructor, except ' ' is
        is replaced with '_' and it is replaced with the empty string if
        the input filename contains invalid characters. (Same check as for
        `Headword.valid_input`, except underscores are also permitted.)
        """
        return self._filename

    @property
    def title_uncoded(self) -> str:
        """Page title of the page that contains info about the audio file.

        This is not the name of the audio file itself. The page is in the
        'File:' namespace and therefore this variable starts with 'File:'.
        This title will be percent-encoded before being sent in the REST
        API call. The page is in the 'File:' namespace and therefore this
        variable starts with 'File:'. Like filename, it is set to the empty
        string if the input filename is not valid.
        """
        return self._title_uncoded

    @property
    def title_uncoded_osd(self) -> str:
        r"""Like title_uncoded, but may replace ':' with Unicode look-alike.

        If `os.name` != 'posix', the prefix 'File:' is replaced with
        'File' + '\ua789', where the second part is the Unicode Modifier
        Letter Colon. This is because Windows file systems cannot have
        colons in filenames. Like filename, it is set to the empty string
        if the input filename is not valid.
        """
        return self._title_uncoded_osd

    @property
    def headword(self) -> str:
        """The headword used to calculate `prob_headword`.

        See `set_headword_info` for details.
        """
        return self._headword

    @property
    def headword_lang_code(self) -> str:
        """The language code used to calculate `prob_headword`.

        See `set_headword_info` for details.
        """
        return self._headword_lang_code

    @property
    def filename_not_safe(self) -> str:
        """Filename from internet, but may be unsafe to use as local filename.

        In most cases, the audio filename will be obtained from an API call
        to Wiktionary and therefore it should be checked that it can be
        safely used as a local filename (ie, we would not want to save
        output files whose filenames start with '../' since that could lead
        to writing outside the designated cache/output directories. If the
        name from the internet has invalid characters, the `filename`
        property will be empty, but this will still be populated.
        """
        return self._filename_not_safe

    @property
    def html_lang_code(self) -> str:
        """The language code used when retrieving html.

        This is also the language_code used when transforming the html
        to the wikitext. It seems likely this generates the same wikitext
        regardless of starting `html_lang_code`.

        It is reasonable for this value to differ from
        `headword_lang_code`.  For example, an English speaker might want
        to download pronunciation of German words from the German
        Wiktionary but download HTML information about the audio files
        (eg, license information) in English.
        """
        return self._html_lang_code

    def set_headword_info(self, headword: str,
                          headword_lang_code: str,
                          media_list_position: Optional[int]) -> None:
        """Update the attributes to the parameters and set prob_headword.

        An audio file could exist on the page of more than one headword,
        but typically an audio file is constructed by getting the media
        list of a given headword and lang_code and then converting
        selected items from the list to AudioFile objects. In such a case,
        it is useful to know whether the audio file simply pronounces the
        headword (in contrast to, perhaps, an expression containing the
        headword). This can be inferred from the audio file name and the
        result is stored in `prob_headword`.

        Parameters
        -----------
        headword : str
            If the audio filename was obtained by calling the media list
            API for a headword, the headword and headword_lang_code can be
            provided.

        headword_lang_code : str
            Language code specifying the language of the Wiktionary used to
            retrieve the headword. See headword for details.

        media_list_position : int, optional
            Position of the item (starting at 0) in the list of items
            returned by the REST API call of the headword.
        """
        self._headword = headword
        self._headword_lang_code = headword_lang_code
        self._media_list_position = media_list_position

        if (not self.filename or not headword or not headword_lang_code
                or len(headword_lang_code)<2):
            self._prob_headword = False
            return

        pattern = '^[{}{}]{}-{}{}'.format(headword_lang_code[0].upper(),
                                      headword_lang_code.lower()[0],
                                      headword_lang_code.lower()[1:], headword,
                                      r'[1234567890]*\.(ogg|oga)')

        if re.search(pattern, self.filename) is None:
            self._prob_headword = False
        else:
            self._prob_headword = True

    @property
    def media_list_position(self) -> Optional[int]:
        """Position of this file in the 'items' of the media list API call."""
        return self._media_list_position

    @property
    def prob_headword(self) -> bool:
        """'Probably headword' pronunciation indicator.

        True if the headword and lang_code are valid and the filename is:
        The language code (first letter optionally capitalized)
        followed by: the headword
        followed by: an optional sequence of digits
        followed by: '.ogg' or '.oga'
        """
        return self._prob_headword

    def __repr__(self) -> str:
        return(f'AudioFile(filename="{self.filename}"'
            f'    headword="{self.headword}",'
            f'    headword_lang_code="{self.headword_lang_code}",'
            f'    media_list_position={self.media_list_position},'
            f'    title_uncoded="{self.title_uncoded}",'
            f'    title_uncoded_osd="{self.title_uncoded_osd}",'
            f'    revision={self.revision},'
            f'    status_msg="{self.status_msg}",'
            f'    html: len({len(self.html)}) str,'
            f'    html_etag="{self.html_etag}",'
            f'    wikitext: len({len(self.wikitext)}) str,'
            f'    prob_headword={self.prob_headword},'
            f'    prob_licenses="{self.prob_licenses}",'
            f'    prob_authors="{self.prob_authors}",'
            f'    prob_attribs="{self.prob_attribs}",'
            f'    request_status="{self.request_status}",'
            f'    download_status="{self.download_status}")')

    def update_request_status(self,
             audio_reqs: Optional[AudioReqs]) -> None:
        """Update `request_status` attribute.

        Parameters
        ----------
        audio_reqs : {str, Dict[str, (int, str)], None}
            Contains user-specified decisions on which audio files to
            download.  See `Headword.fetch_all_audio()` for details.

        Returns
        -------
        None
        """
        if audio_reqs is None:
            self.request_status = 'No request decision'
        else:
            reqval = audio_reqs.get(self.filename, None)
            if reqval is None:
                self.request_status = 'No decision'
            elif reqval[1] == 'Y':
                if reqval[0] != self.revision:
                    self.request_status = ('Requested, but revision '
                                           'out of date')
                else:
                    self.request_status = 'Requested'
            elif reqval[1] == 'N':
                if reqval[0] != self.revision:
                    self.request_status = ('Not requested, but revision '
                                           'out of date')
                else:
                    self.request_status = 'Not requested'
            elif not reqval[1]:
                if reqval[0] != self.revision:
                    self.request_status = ('No decision, but revision '
                                           'out of date')
                else:
                    self.request_status = 'No decision'
            else:
                self.request_status = 'Request decision not valid'

    def _copy_req_html_and_wtxt(self, lang_code: str,
                           io_options: io_opts.IOOptions) -> None:
        """Copy html and wikitext to new directory only for requested audios.
        If `self.request_status` == "Requested", copy the wikitext for
        the file from the "fnspwtxt" directory to "fnspwtxtr" and copy the
        HTML and eTag files from "fnsphtml" to "fnsphtmlr".

        Parameters
        ----------
        lang_code : str
            Language code specifying the language of the Wiktionary™ from
            which the HTML with info about the audio files was retrieved
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        if self.request_status != 'Requested': return

        #name_part1 = f'{self.title_uncoded_osd}.{lang_code}.{self.revision}'
        name_part1 = f'{self.title_uncoded_osd}.{self.revision}'
        wtxt_file_name = f'{name_part1}.txt'
        html_file_name = f'{name_part1}.html'
        etag_file_name = f'{name_part1}.etag.txt'

        dest_name = os.path.join(io_options.output_dir, 'fnspwtxtr',
            io_options.add_subdir_fn(self.title_uncoded), wtxt_file_name)
        src_name = os.path.join(io_options.output_dir, 'fnspwtxt',
            io_options.add_subdir_fn(self.title_uncoded), wtxt_file_name)
        shutil.copy(src_name, dest_name)

        dest_name = os.path.join(io_options.output_dir, 'fnsphtmlr',
            io_options.add_subdir_fn(self.title_uncoded), html_file_name)
        src_name = os.path.join(io_options.output_dir, 'fnsphtml',
            io_options.add_subdir_fn(self.title_uncoded), html_file_name)
        shutil.copy(src_name, dest_name)

        dest_name = os.path.join(io_options.output_dir, 'fnsphtmlr',
            io_options.add_subdir_fn(self.title_uncoded), etag_file_name)
        src_name = os.path.join(io_options.output_dir, 'fnsphtml',
            io_options.add_subdir_fn(self.title_uncoded), etag_file_name)
        shutil.copy(src_name, dest_name)

    def _fetch_audio(self, io_options: io_opts.IOOptions) -> None:
        """Download audio to 'allaudio' subdirectory if marked as requested.

        Parameters
        ----------
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        audio_file_name = os.path.join(io_options.output_dir, 'allaudio',
                io_options.add_subdir_fn(self.title_uncoded), self.filename)
        if os.path.isfile(audio_file_name):
            self.download_status = 'Previously Downloaded'
        if io_options.audio_out_mode is io_opts.AudioOutMode.NO_OUTPUT:
            return

        if ((io_options.audio_out_mode is io_opts.AudioOutMode.OVERWRITE or
                 (io_options.audio_out_mode is
                         io_opts.AudioOutMode.NO_OVERWRITE
                     and not os.path.isfile(audio_file_name)))
                 and self.request_status == 'Requested'):
            url = ('https://api.wikimedia.org/wiki/'
                  f'Special:Redirect/file/{_quote_url(self.filename)}')
            try:
                audio_file = requests.get(url, headers=io_options.headers,
                    timeout=io_options.timeout)
                time.sleep(io_options.sleep_time)
                with open(audio_file_name, 'wb') as f:
                    f.write(audio_file.content)
            except requests.exceptions.RequestException as err:
                logger.exception('Unexpected err=%s, type(err)=%s', err,
                    type(err))
                self.download_status = ('Download attempted, but '
                                       'error occurred')
            else:
                self.download_status = 'Downloaded'

    def str_wikitext_etal(self) -> str:
        """Create a string with prob_licenses, prob_authors, wikitext, etc.

        Purpose is to provide a user with a nicely formatted output of the
        wikitext and probable license and author information to aid in
        deciding whether the audio file should be requested for download.
        For example, the user should use this or a similar function to
        verify that the probable license or author information extracted
        by the (possibly imperfect) regular expression parser is accurate
        before making a decision whether to request the file for download.

        Parameters
        -----------
        None

        Returns
        -------
        String. First line is '-' repeated 79 times, then the object
        attributes with the attribute name and value, followed by newline.
        So the first line is 'filename: {filename}'. This is done for
        `filename`, `headword`, `headword_lang_code`, `prob_licenses`,
        `prob_authors`, `prob_attribs`, and `wikitext`.  For readability,
        additional newlines are added after the `headword_lang_code` value,
        the `prob_attribs` value, and the label for `wikitext` (so that
        the `wikitext` value starts on a new line).

        If filename is '', then a row for `filename_not_safe` is printed
        instead.
        """
        if self.filename:
            filename_str = f'filename: {self.filename}\n'
        else:
            filename_str = f'filename_not_safe: {self.filename_not_safe}\n'

        return ('----------------------------------------'
                '---------------------------------------\n'
                f'{filename_str}'
                f'headword: {self.headword}\n'
                f'headword_lang_code: {self.headword_lang_code}\n\n'
                f'prob_licenses: {self.prob_licenses}\n'
                f'prob_authors: {self.prob_authors}\n'
                f'prob_attribs: {self.prob_attribs}\n\n'
                f'wikitext:\n{self.wikitext}\n')


    def parse_audio_wikitext(self) -> None:
        """Parse wikitext for probable license, author, and attribution.

           `self.prob_licenses`, `self.prob_authors`, and
           `self.prob_attribs` are updated with the probable licenses,
           authors, and attributions found. `self.templates` is updated
           with the list of templates from which the info was extracted.

           Only a subset of all possible licensing templates are handled.
           At the time the function was written, the template documentation
           and code was inspected to check what parameters were permitted
           by the template.

           Templates are only processed if lines can be joined in the
           wikitext such that a template starts and ends on a single line,
           where joining is performed until the number of '{' and '}'
           match on the line. A successfully processed template is put
           into a `WikiTemp` namedtuple and consists of the template name
           as a string and a dictionary mapping the parameter names to
           values.

           When processing the templates, `attribution` parameters are put
           in the `prob_attribs` list, `author` parameters are put in the
           `prob_authors` list, the template name is put into the
           `prob_licenses` list (except for the 'Information' template,
            see note below), and the processed template is put into the
           `prob_templates` list. Parameter values that are empty strings
           are not put into the output lists. However, the above
           parameters are only extracted if the template documentation or
           code indicates support for such a paramter. The following
           summarizes the supported templates and parameters:

           cc-zero: No template parameters extracted
           GFDL: `attribution` parameter extracted
           PD-Self: `author` parameter extracted
           Self or self: value of `1`, `2`, ... `9` parameter put
               in `prob_licenses`. (This applies both for explicitly
               named paramaters or unnamed positional parameters.) An
               info message is logged if the parameter '10' exists so
               the user can decide whether to process the template
               some other way, as there is no actual limit on the
               number of licenses the template could hold.
               `author` or `Author` parameter and `attribution` or
               `Attribution` parameters are also extracted.
           Information: `permission` or `Permission` parameters put in
               `prob_licenses`. `author` or `Author` parameters also
               extracted.
           Cc-by-2.0-fr, Cc-by-sa-2.0-fr, Cc-by-sa-2.0-de, Cc-by-2.5,
           Cc-by-sa-2.5, Cc-by-sa-3.0, Cc-by-3.0, Cc-by-sa 3.0,
           Cc-by-3.0-us, Cc-by-3.0-fr, Cc-by-4.0, Cc-by-sa 4.0,
           Cc-by-sa-4.0: `attribution` parameter extracted if present.
               Otherwise, paramater `1` (named or unamed positional) is
               used as the attribution value.
           Pronunciation file, Lingua Libre record: `author` parameter
               extracted. These templates do not contain license
               information, so the name is not added to `prob_licenses`,
               although the template is added to `prob_templates`.

           An info message is logged for other templates (except the
           `Supported by Wikimedia Deutschland` template is ignored).

           Returns
           -------
           None

           Notes
           -----
           A few templates were found during testing but not included in
           the list of handled templates because the template pages are
           not protected. These include the relatively low frequenncy
           'Aussprache/countries' template used in some German files and
           the 'Forvo-1640max' template used for a number of Russian
           files.
        """
        prob_licenses = []
        prob_templates = []
        prob_authors = []
        prob_attribs = []
        lines = parse._oneline_templates(self.filename, self.wikitext)
        #----------------------------------------------------------------------
        # No parameters: cc-zero
        # Author and other irrelevant parms: PD-self
        # Multiple parameters for licenses, author, and attribution: self, Self
        # attribution only: below list, no numbered params
        # attribution only: below list, no numbered params
        #----------------------------------------------------------------------
        takes_attrib_list = ['GFDL']
        takes_attrib_and_1_list = [
            'Cc-by-2.0-fr', 'cc-by-2.0-fr','Cc-by-sa-2.0-fr','cc-by-sa-2.0-fr',
            'Cc-by-sa-2.0-de', 'cc-by-sa-2.0-de',
            'Cc-by-2.5', 'cc-by-2.5', 'Cc-by-sa-2.5', 'cc-by-sa-2.5',
            'Cc-by-sa-3.0', 'cc-by-sa-3.0', 'Cc-by-3.0', 'cc-by-3.0',
            'Cc-by-sa 3.0', 'cc-by-sa 3.0', 'Cc-by-3.0-us', 'cc-by-3.0-us',
            'Cc-by-3.0-fr', 'cc-by-3.0-fr',
            'Cc-by-4.0', 'cc-by-4.0',
            'Cc-by-sa 4.0', 'cc-by-sa 4.0', 'Cc-by-sa-4.0', 'cc-by-sa-4.0',
            ]
        author_but_not_license = ['Pronunciation file',
                                  'Lingua Libre record']
        # 'Aussprache/countries' is currently a GFDL v1.2+ license, but is
        # not protected.

        # also author information in these
        ignore_list = ['Supported by Wikimedia Deutschland']

        for line in lines:
            if line.find('<!--') != -1:
                logger.warning('File contains HTML commment and will not be '
                               'parsed for author, license, attrib info: %s',
                               self.title_uncoded)
                return

            if line.startswith('{{'):
                wtemp, err_msg = parse.parse_one_template(line)
                if wtemp:
                    if wtemp.name in ['cc-zero']:
                        prob_templates.append(wtemp)
                        prob_licenses.append(wtemp.name)
                    elif wtemp.name == 'PD-self':
                        prob_templates.append(wtemp)
                        prob_licenses.append(wtemp.name)
                        if wtemp.params.get('author',''):
                            prob_authors.append(wtemp.params['author'])
                    elif wtemp.name in author_but_not_license:
                        prob_templates.append(wtemp)
                        if wtemp.params.get('author',''):
                            prob_authors.append(wtemp.params['author'])
                    elif wtemp.name in takes_attrib_list:
                        prob_templates.append(wtemp)
                        prob_licenses.append(wtemp.name)
                        if wtemp.params.get('attribution',''):
                            prob_attribs.append(wtemp.params['attribution'])
                    elif wtemp.name in takes_attrib_and_1_list:
                        prob_templates.append(wtemp)
                        prob_licenses.append(wtemp.name)
                        if wtemp.params.get('attribution',''):
                            prob_attribs.append(wtemp.params['attribution'])
                        elif wtemp.params.get('1',''):
                            prob_attribs.append(wtemp.params['1'])
                    elif wtemp.name == 'Information':
                        if wtemp.params.get('permission',''):
                            prob_licenses.append(wtemp.params['permission'])
                        if wtemp.params.get('Permission',''):
                            prob_licenses.append(wtemp.params['Permission'])
                        if wtemp.params.get('author',''):
                            prob_authors.append(wtemp.params['author'])
                        if wtemp.params.get('Author',''):
                            prob_authors.append(wtemp.params['Author'])
                    elif wtemp.name == 'Self' or wtemp.name == 'self':
                        if '1' in wtemp.params:
                            prob_licenses.append(wtemp.params['1'])
                        if '2' in wtemp.params:
                            prob_licenses.append(wtemp.params['2'])
                        if '3' in wtemp.params:
                            prob_licenses.append(wtemp.params['3'])
                        if '4' in wtemp.params:
                            prob_licenses.append(wtemp.params['4'])
                        if '5' in wtemp.params:
                            prob_licenses.append(wtemp.params['5'])
                        if '6' in wtemp.params:
                            prob_licenses.append(wtemp.params['6'])
                        if '7' in wtemp.params:
                            prob_licenses.append(wtemp.params['7'])
                        if '8' in wtemp.params:
                            prob_licenses.append(wtemp.params['8'])
                        if '9' in wtemp.params:
                            prob_licenses.append(wtemp.params['9'])
                        if '10' in wtemp.params:
                            logger.warning(('File: %s: max 9 parameters used'
    ' from Self/self template'), self.title_uncoded)
                        if wtemp.params.get('author',''):
                            prob_authors.append(wtemp.params['author'])
                        if wtemp.params.get('Author',''):
                            prob_authors.append(wtemp.params['Author'])
                        if wtemp.params.get('attribution',''):
                            prob_attribs.append(wtemp.params['attribution'])
                        if wtemp.params.get('Attribution',''):
                            prob_attribs.append(wtemp.params['Attribution'])
                    elif wtemp.name not in ignore_list:
                        logger.warning('Template not handled: %s: %s: %s',
                            wtemp.name, line, self.title_uncoded)
                else:
                    logger.warning('Template not parsed: %s: %s: %s',
                        err_msg, line, self.title_uncoded)
        #print(f'{prob_licenses=}\n{prob_authors=}'
        #      '\n{prob_attribs=}\n{prob_templates=}')
        if prob_licenses:
            self.prob_licenses = sorted(list(set(prob_licenses)))
        if prob_authors:
            self.prob_authors = sorted(list(set(prob_authors)))
        if prob_attribs:
            self.prob_attribs = sorted(list(set(prob_attribs)))
        if prob_templates:
            self.prob_templates = prob_templates

    def _parse_wikitext_regex(self) -> None:
        license_list = [
            r'\{\{self\|cc-zero\}\}',
            r'\{\{cc-zero\}\}',
            r'\{\{PD-self\|.*\}\}',
            r'\{\{PD-self\}\}',
            r'\{\{[Cc]c-by-4.0\|.*\}\}',
            r'\{\{cc-by-sa 4.0\}\}',
            r'\{\{cc-by-sa-4.0\}\}',
            r'\{\{self\|author=.*?\|cc-by-sa-4.0\}\}',
            r'\{\{self\|cc-by-sa-4.0\}\}',
            r'\{\{cc-by-2.0-fr\}\}',
            r'\{\{cc-by-2.5\}\}',
            r'\{\{cc-by-3.0\}\}',
            r'\{\{cc-by-3.0-us\}\}',
            r'\{\{cc-by-sa-2.0-de\}\}',
            r'\{\{cc-by-sa-2.5\}\}',
            r'\{\{cc-by-sa 3.0\|.*\}\}',
            r'\{\{[Cc]c-by-sa-3.0\}\}',
            r'\{\{self\|cc-by-sa-2.5\}\}',
            r'\{\{self\|[Cc]c-by-sa-3.0\}\}',
            r'\{\{self\|cc-by-sa-3.0\|GFDL\}\}',
            (r'\{\{self\|cc-by-sa-3.0\|GFDL\|'
             r'author=I, \[\[.*?\]\]\}\}'),
            r'\{\{self\|GFDL\|cc-by-sa-3.0\}\}',
            r'\{\{self\|GFDL\|cc-by-sa-3.0,2.5,2.0,1.0\}\}',
            (r'\{\{Self\|GFDL\|Cc-by-sa-3.0-migrated\|'
        r'cc-by-sa-2.5,2.0,1.0\|author=I, \[\[.*?\]\]\}\}'),
            r'\{\{self\|GFDL\|cc-by-sa-all\}\}',
            r'\{\{self\|GFDL\|cc-by-sa-all\|migration=redundant\}\}',
            r'\{\{Cc-by-sa-2.5\}\}',
            r'\{\{Self\|GFDL\|Cc-by-sa-3.0-migrated\|Cc-by-2.5\}\}',
            (r'\{\{self\|GFDL\|Cc-by-sa-3.0-migrated\|'
             r'Cc-by-sa-2.5,2.0,1.0\}\}'),
            (r'\{\{Self\|GFDL\|Cc-by-sa-3.0-migrated\|'
             r'cc-by-sa-2.5,2.0,1.0\|.*\}\}'),
            (r'\{\{self\|GFDL\|Cc-by-sa-3.0-migrated\|'
             r'Cc-by-sa-2.5,2.0,1.0\}\}'),
            r'\{\{GFDL\|migration=relicense\}\}',
            r'\{\{Cc-by-2\.0-fr\}\}',
            r'\{\{cc-by-sa-3\.0-us\}\}',
        ]
        license_re = re.compile('(' + '|'.join(license_list) + ')')
        author_re = re.compile(r'[Aa]uthor=\[\[.*?\]\]|'
            r'[Aa]uthor=..*\||[Aa]uthor=..*\}\}')

        prob_licenses = re.findall(license_re, self.wikitext)

        if len(prob_licenses)>1:
            logger.warning('File: %s: multiple probable licenses %s',
                           self.title_uncoded_osd, prob_licenses)
            self.prob_license = str(prob_licenses)
        elif len(prob_licenses)==0:
            logger.warning('File: %s: no probable license',
                           self.title_uncoded_osd)
            self.prob_license = ''
        else:
            self.prob_license = prob_licenses[0]

        # Get the author
        authors = re.findall(author_re, self.wikitext)
        author_set = { re.sub('^[Aa]uthor=', '', x)
                       for x in authors if x.strip() != ''}
        if len(author_set)>1:
            logger.info('File: %s: multiple probable authors %s',
                        self.title_uncoded_osd, author_set)
            self.prob_author = ''
        elif len(author_set)==0:
            logger.warning('File: %s: no probable author',
                           self.title_uncoded_osd)
            self.prob_author = ''
        else:
            self.prob_author=author_set.pop()

#------------------------------------------------------------------------------
# Class definition: Headword
#------------------------------------------------------------------------------
class Headword:
    """Headword information and associated audio files.

    That is, if self.headword='still' and lang_code='en', this contains
    information about https://en.wiktionary.org/wiki/still. Case matters,
    as headword='Still' refers to https://en.wiktionary.org/wiki/Still, a
    different page.

    Attributes
    ----------
    status_msg : str
        Status message indicating any problems processing the word
    audio_files : list[AudioFile]
        List of audio files associated with the word. Initialized to [].
    revision : int
        Page revision. Used when requesting html and wikitext to ensure
        these correspond to the same revision. Set to 0 upon
        initialization and remains 0 if revision is not retrieved
        (eg, if `valid_input` == False).
    timestamp : str
        Timestamp for the revision.
    html : str
        HTML for the page. Empty if problem loading or loading never
        requested.
    html_etag : str
        eTag information in header when HTML was downloaded. This is stored
        as it needs to be passed when requesting the wikitext.
    wikitext : str
        Wikitext for the page+revision. Empty if problem loading or loading
        never requested.

    Trademark Notice
    ----------------
    Wiktionary is a trademark of the Wikimedia Foundation and is used
    with the permission of the Wikimedia Foundation. We are not endorsed by
    or affiliated with the Wikimedia Foundation.

    """

    _lang_code: str
    _desc: str

    _desc = 'Word'

    def __init__(self, headword: str, lang_code: str):
        """Initialize instance based on headword and language code.

        Initialization does not cause information to be fetched from the
        internet or local application cache/output.

        Parameters
        ----------
        headword : str
            The word or phrase for which information will be retrieved.

        lang_code : str
            Language code specifying the language of the Wiktionary™ from
            which data will be retrieved.

        Trademark Notice
        ----------------
        Wiktionary is a trademark of the Wikimedia Foundation and is used
        with the permission of the Wikimedia Foundation. We are not
        endorsed by or affiliated with the Wikimedia Foundation.
        """

        self._headword: str = str.strip(headword)
        self._title_uncoded: str = headword.replace(' ','_')
        self._valid_input: bool = True
        self.status_msg: str = ''
        self.audio_files: list[AudioFile] = []
        self.revision: int = 0
        self.timestamp: str = ''
        self.html: str = ''
        self.html_etag: str = ''
        self.wikitext: str = ''

        if not headword:
            self.status_msg = 'Empty word.'
            self._valid_input = False
            logger.warning('Skipping empty word')
        elif not _is_valid_headword(headword):
            self.status_msg = 'Word not valid'
            self._valid_input = False
            logger.warning('Word=%s not valid', headword)

        if not _is_valid_lang_code(lang_code):
            self.status_msg = 'lang_code not valid'
            self._valid_input = False
            self._lang_code=''
        else:
            self._lang_code=lang_code

    @property
    def headword(self) -> str:
        """Headword of the dictionary entry.

        Corresponds to a web page in Wiktionary. This is the `headword`
        parameter passed to the constructor with str.strip() called. It can
        be a word or phrase, but can only contain certain characters (see
        `valid_input` attribute).  As an example, if information
        for https://en.wiktionary.org/wiki/still is requested, then
        lang_code='en' and headword='still'. Capitalization is important.
        headword='Still' would request a different page.
        """
        return self._headword

    @property
    def lang_code(self) -> str:
        """Language code specifying the language of the Wiktionary."""
        return self._lang_code

    @property
    def title_uncoded(self) -> str:
        """Title of the page that will be requested from Wiktionary.

        This is the headword after converting ' ' to '_' but without
        percent-encoding the title.
        """
        return self._title_uncoded

    @property
    def desc(self) -> str:
        """A class variable always equal to 'Word' used in log messages."""
        return self._desc

    @property
    def valid_input(self) -> bool:
        """Indicates whether the headword contains invalid characters.

        To be safe, only allow Unicode alphanumeric (except '_') and space,
        hyphen, single quote, and period { -'.}. The headwords '.' and '..'
        are also not valid. Wiktionary has more permissive validation criteria
        but these seem unnecessary to support at this time.
        """
        return self._valid_input

    def __repr__(self) -> str:
        return ('Headword('
            f'    lang_code="{self.lang_code}",'
            f'    headword="{self.headword}",'
            f'    title_uncoded="{self.title_uncoded}",'
            f'    valid_input={self.valid_input},'
            f'    status_msg="{self.status_msg}",'
            f'    revision={self.revision},'
            f'    html: len({len(self.html)}) str,'
            f'    html_etag="{self.html_etag}",'
            f'    wikitext: len({len(self.wikitext)}) str,'
            f'    desc="{self.desc}",'
            '     audio_files=[' +
            '\n'.join([f'    {af}' for af in self.audio_files]) +
            '])\n')

    #----------------
    # Public methods
    #----------------
    def fetch_revision_info(self, io_options: io_opts.IOOptions) -> None:
        """Fetch the revision number of the word page.

        Fetching only performed if self.valid_input == True. If
        self.headword='still' and lang_code='en', this will retrieve the
        current revision number of the page:
        https://en.wiktionary.org/wiki/still (from either the internet or
        local cache/output, depending on io_options.cache_mode).

        Parameters
        ----------
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        if self.valid_input:
            _fetch_current_revision(self, io_options=io_options,
                                    lang_code = self.lang_code)

    def fetch_word_page(self, io_options: io_opts.IOOptions) -> None:
        """Fetch the HTML and wikitext for the word page.

        That is, if self.headword='still' and the IOOptions.lang_code='en',
        this will retrieve the page: https://en.wiktionary.org/wiki/still

        Parameters
        ----------
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        if self.revision>0:
            if io_options.fetch_html:
                _download_html(self, self.lang_code, io_options=io_options)
            _download_wikitext(self, self.lang_code, io_options=io_options)

    # turning off the type_checker for the sort_key parameter because I do
    # not want to check the type in the default sort. Users are advised if
    # setting media_list_position = None to not use the default sort
    def fetch_audio_info(self, io_options: io_opts.IOOptions,
            audio_html_lang_code: str,
            sort_key:SortKey = lambda x: -x.media_list_position, # type: ignore
            parse_wikitext_fn: Optional[Callable[[AudioFile], Any]] = None,
            audio_reqs: Optional[AudioReqs] = None,
            filename_pattern: Optional[str] = None) -> None:
        """Fetch audio info for the word.

        Fetch the audio file information in HTML and wikitext form for all
        the audio files from the title page of the word, filtering out
        audio files in other languages. The page retrieved for each selected
        audio file is from the 'File' namespace (ie, the page title starts
        with 'File:' (or some translation for non-English languages).
        This does not control download of the audio files themselves, which
        is controlled by the 'input_audio_reqs' and 'audio_out_mode'
        parameters.

        Example: lang_code = 'en' and word = 'still', using the default
        filtering, this fetches the HTML and wikitext for pages (1) and (2)
        below but not (3), since these audio file names for (1) and (2)
        (ie, the portion of the name after 'File:') start with 'en-' or
        'En-').
        (1) https://en.wiktionary.org/wiki/File:en-uk-still.ogg
        (2) https://en.wiktionary.org/wiki/File:en-us-still.ogg
        (3) https://en.wiktionary.org/wiki/File:De-still.ogg

        See 'Notes' below for details on the filtering performed.

        Parameters
        ----------
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        audio_html_lang_code : str
            Language code specifying the language of the Wiktionary™ from
            which to retrieve the HTML with info about the audio files

        audio_reqs : {None (default), str, Dict[str, (int, str)]}
            Contains user-specified decisions on which audio files to
            download.  This is for potential future use (as no audio files
            are currently downloaded). Files in this list not selected by
            `fetch_audio_info` are ignored.  Files selected by
            `fetch_audio_info` that are not in this list will not be
            downloaded.

            The general idea is that the user will call this function
            once with input_audio_reqs=None and obtain the audio file
            information by processing the object or from the output file
            specified by the `output_audios_filename` parameter if the
            object was created using `wrapper.words_wrapper`. The user
            will update 'request_download' information and pass it back in.

            If a dict is passed, it should have key = filename [str] and
            value = (audio_revision [int], request_download [str]), where:

            'filename' - audio filename (ie, match `AudioFile.filename`)
            'audio_revision' - page revision of the file from the 'File:'
                 namespace (ie, the file containing license and author
                 information) upon which the decision to request download
                 was based.
            'request_download' - Takes one of three values: 'Y', 'N', ''

        sort_key : Callable[AudioFile, Any]
            Defines a partial key for sorting audio files using the
            sort_audio function.  It is useful useful for sorting the audio
            files before outputing the audio files for the user to create
            the 'request_download'. Audio files will be sorted by the full
            key in reverse order (because most keys will be booleans and
            this will make True sort before False).
            The full key used to sort is:
                (x.download_requested, sort_key(x))
            In other words, files where the download was requested (using
            the `input_audio_reqs` parameter) are always sorted first.
            Default is lambda x: -x.media_list_position so that the first
            requested item is taken from the ordering from the media list
            REST API call.

        parse_wikitext_fn : Callable([AudioFile], None), optional
            User-defined parsing function that if set will replace the
            default parser that sets the `prob_licenses`, `prob_authors`,
            `prob_attribs`, and `prob_templates` attributes of each
            `AudioFile` object. See `parse_audio_wikitext` for default
            behavior.

        filename_pattern : str, optional
            String containing regular expression used to try to determine
            the language of the audio file. Audio filenames that do not
            match this regular expression are not retrieved when
            constructing the Headword object for each word. Informational
            messages are written to the log for excluded audio files.
            Defaults exist for 17 languages, but these can be overridden.
            See `Notes` for details.

        Returns
        -------
        None

        Notes
        -----
        This parameter is needed because a Wiktionary page by design
        does not only contain sections for words in the language the
        Wiktionary is written in and therefore the page may contain
        audio files from languages other than the one matching
        `header_lang_code`. The default patterns are listed in the
        second element of the _LangInfo tuple below:

        {
            'de' : _LangInfo('German',     r'^LL.*\\(deu\\)|^[Dd]e-'),
            'ar' : _LangInfo('Arabic',     r'^LL.*\\(ara\\)|^[Aa]r-'),
            'en' : _LangInfo('English',    r'^LL.*\\(eng\\)|^[Ee]n-'),
            'es' : _LangInfo('Spanish',    r'^LL.*\\(spa\\)|^[Ee]s-'),
            'fr' : _LangInfo('French',     r'^LL.*\\(fra\\)|^[Ff]r-'),
            'ru' : _LangInfo('Russian',    r'^LL.*\\(rus\\)|^[Rr]u-'),
            'pl' : _LangInfo('Polish',     r'^LL.*\\(pol\\)|^[Pp]l-'),
            'cs' : _LangInfo('Czech',      r'^LL.*\\(cze\\)|^[Cc]s-'),
            'sv' : _LangInfo('Swedish',    r'^LL.*\\(sve\\)|^[Ss]v-'),
            'zh' : _LangInfo('Chinese',    r'^LL.*\\(zho\\)|^[Zz]h-'),
            'hi' : _LangInfo('Hindi',      r'^LL.*\\(hin\\)|^[Hh]i-'),
            'mg' : _LangInfo('Malagasy',   r'^LL.*\\(mal\\)|^[Mm]g-'),
            'pt' : _LangInfo('Portuguese', r'^LL.*\\(por\\)|^[Pp]t-'),
            'ja' : _LangInfo('Japanese',   r'^LL.*\\(jap\\)|^[Jj]a-'),
            'uk' : _LangInfo('Ukrainian',  r'^LL.*\\(ukr\\)|^[Uu]k-'),
         }
        Some of the languages for which default patterns are
        created appear to have minimal audio files in their Wiktionary.

        The portoin of the pattern starting with 'LL' presumably refers
        to audio files created using Lingua Libre, although it is
        unclear whether Wikimedia Commons™ prevents files created in
        another manner from having a similar naming convention.
        (https://meta.wikimedia.org/wiki/Lingua_Libre)

        Trademark Notice
        -----------------
        Wiktionary and Wikimedia Commons are trademarks of the Wikimedia
        Foundation and is used with the permission of the Wikimedia
        Foundation. We are not endorsed by or affiliated with the Wikimedia
        Foundation.
        """
        if self.revision <= 0: return

        ##fnsp_prefix_str = 'File:'
        pattern_str = _assign_pattern(self.lang_code,
                                      filename_pattern)

        self._fetch_media_list(io_options, pattern_str)

        valid_audio_html_lang_code : bool = _is_valid_lang_code(
            audio_html_lang_code)

        for aud_file in self.audio_files:
            if aud_file.filename == '': continue
            if not valid_audio_html_lang_code:
                logger.error('fetch_audio_info: Lang %s: Word %s: '
                    'audio_html_lang_code=%s not valid', self.lang_code,
                     self.headword, audio_html_lang_code)
                self.status_msg = ('HTML not downloaded as '
                               f'{audio_html_lang_code=} not valid')
                continue
            _fetch_current_revision(aud_file, io_options=io_options,
                                    lang_code=audio_html_lang_code)
            aud_file.update_request_status(audio_reqs=audio_reqs)
            if io_options.fetch_html:
                _download_html(aud_file, lang_code=audio_html_lang_code,
                               io_options=io_options)
            _download_wikitext(aud_file, lang_code=audio_html_lang_code,
                           io_options=io_options)
            if parse_wikitext_fn is None:
                aud_file.parse_audio_wikitext()  # don't want to make public, so pylint: disable=protected-access
            else :
                parse_wikitext_fn(aud_file)

        self.sort_audio(sort_key=sort_key)

    def sort_audio(self, sort_key: SortKey) -> None:
        """Sort audio files according to user-provided key.

        Parameters
        ----------
        sort_key : Callable[AudioFile, Any]
            Defines a partial key for sorting audio files. The full key
            used to sort (in reverse) is:
                (x.download_requested, sort_key(x))
            See `Headword.fetch_all_audio()` for details.

        Returns
        -------
        None
        """
        self.audio_files.sort(
            key = lambda x: (x.request_status == 'Requested', sort_key(x)),
            reverse=True)

    def update_audio_req_and_sort(self,
             audio_reqs: Optional[AudioReqs],
             sort_key: SortKey) -> None:
        """Update `request_status` attribute on all audio files and re-sort.

        Parameters
        ----------
        audio_reqs : {str, Dict[str, (int, str)], None}
            Contains user-specified decisions on which audio files to
            download. See `Headword.fetch_all_audio` for details.

        sort_key : Callable[AudioFile, Any], default: lambda x: True
            Defines a partial key for sorting audio files. The full key
            used to sort (in reverse) is:
                (x.download_requested, sort_key(x))
            See `Headword.fetch_all_audio` for details.

        Returns
        -------
        None
        """
        for aud_file in self.audio_files:
            aud_file.update_request_status(audio_reqs)
        self.sort_audio(sort_key=sort_key)

    def _fetch_audio(self, io_options: io_opts.IOOptions) -> None:
        """Download audio for requested audio files.

        Calls AudioFile.fetch_audio for each file in audio_files.

        Parameters
        ----------
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        for aud_file in self.audio_files:
            aud_file._fetch_audio(io_options=io_options)

    def copy_req_html_and_wtxt(self, audio_html_lang_code: str,
                           io_options: io_opts.IOOptions) -> None:
        """Copy html and wikitext to new directory only for requested audios.

        Calls `AudioFile._copy_req_html_and_wtxt()` for each audio file.

        Parameters
        ----------
        audio_html_lang_code : str
            Language code specifying the language of the Wiktionary™ from
            which the HTML with info about the audio files was retrieved
        io_options : io_options.IOOptions
            Control parameters for internet requests and local cache/output

        Returns
        -------
        None
        """
        for aud_file in self.audio_files:
            aud_file._copy_req_html_and_wtxt(lang_code=audio_html_lang_code,
                io_options=io_options)

#    def _copy_one_audio(self, io_options: io_opts.IOOptions) -> None:
#        """Copy one (or zero) audio file from 'allaudio' to 'oneaudio' subdir.
#
#        Copies the first audio file (assume already sorted by the user)
#        from the 'allaudio' cache/output subdirectory to the 'oneaudio'
#        subdirectory. Files are always first sorted by whether
#        `request_status`=='Requested' and those files that aren't requested
#        aren't downloaded (although might be in the cache from a previous
#        download). Therefore, if `request_status` is not 'Requested' for
#        the first file, no files are copied. Also, nothing is done if
#        `io_options.audio_out_mode` is AudioOutMode.NO_OUTPUT.
#
#        Parameters
#        ----------
#        io_options : io_options.IOOptions
#           Control parameters for internet requests and local cache/output
#
#        Returns
#        -------
#        None
#        """
#        if (io_options.audio_out_mode is io_opts.AudioOutMode.NO_OUTPUT or
#               (not (self.audio_files
#                and self.audio_files[0].request_status == 'Requested'))):
#            return
#        dest_name = os.path.join(io_options.output_dir, 'oneaudio',
#            io_options.add_subdir_fn(self.audio_files[0].filename))
#        if ( io_options.audio_out_mode is io_opts.AudioOutMode.OVERWRITE
#            or ( os.path.isfile(dest_name)
#                and io_options.audio_out_mode is
#                    io_opts.AudioOutMode.NO_OVERWRITE)):
#            src_name = os.path.join(io_options.output_dir, 'allaudio',
#                io_options.add_subdir_fn(self.audio_files[0].filename))
#            shutil.copy(src_name, dest_name)

    #-------------------
    # Private methods
    #-------------------
    def _fetch_media_list(self, io_options: io_opts.IOOptions,
            pattern_str: str) -> None:

        #if self.lang_code != 'es':
        media_list = self._fetch_media_list_rest_api(io_options=io_options)

        try:
            media_list_items = media_list['items']
        except KeyError:
            logger.error(("Lang %s: Word %s: 'items' not found "
                           'in media list response'),
                           self.lang_code, self.headword)
            self.status_msg = ("'items' not found in media list "
                               'response. refecting')
            return

        for media_list_position, item in enumerate(media_list_items):
            if item['type'] == 'audio':
                if _should_audio_item_be_skipped(item, pattern_str):
                    continue
                audio_file = AudioFile(
                    filename = item['title'].split(':')[1],
                    headword = self.headword,
                    headword_lang_code = self.lang_code,
                    media_list_position = media_list_position)
                self.audio_files.append(audio_file)
        #else:
        #    if not self.wikitext: return

    def _fetch_media_list_rest_api(self,
                io_options: io_opts.IOOptions) -> MediaList:

        media_list: MediaList
        base_url = f'https://{self.lang_code}.wiktionary.org/api/rest_v1'

        cache_file_name = os.path.join(io_options.output_dir, 'medlist',
                io_options.add_subdir_fn(self.title_uncoded),
                (f'{self.title_uncoded}.{self.lang_code}.'
                 f'{self.revision}.json'))
        cache_usable = False
        if ( (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE or
              io_options.cache_mode is io_opts.CacheMode.READ_ONLY)
                and os.path.isfile(cache_file_name)):
            with open(cache_file_name, encoding='utf-8') as f:
                media_list = json.load(f)
            if 'items' in media_list:
                cache_usable = True

        if not cache_usable:
            url = (f'{base_url}/page/media-list/'
                   f'{_quote_url(self.title_uncoded)}/{self.revision}')
            response = requests.get(url, headers=io_options.headers,
                                    timeout=io_options.timeout)
            time.sleep(io_options.sleep_time)
            media_list = response.json()
            if (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE or
                    io_options.cache_mode is io_opts.CacheMode.WRITE_ONLY):
                with open(cache_file_name, 'w', encoding='utf-8') as f:
                    json.dump(media_list, f)
        return media_list

#------------------------------------------------------------------------------
# Private functions that act on Headword and AudioFile classes. In the future,
#   I might consider making an abstract class that both Headword and AudioFile
#   are derived from, and this could be a method of the abstract class.
# But I think the current set-up is good enough for now, since the function
#   is private.
#------------------------------------------------------------------------------
def _download_html(self: Union[Headword, AudioFile], lang_code: str,
                   io_options: io_opts.IOOptions) -> None:
    #base_url = f'https://{lang_code}.wiktionary.org/api/rest_v1'
    if not isinstance(self, Headword):
        outsubdir = 'fnsphtml'
        title_uncoded_osd = self.title_uncoded_osd
        base_url = 'https://api.wikimedia.org/core/v1/commons/page'
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{self.revision}.html')
        etag_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{self.revision}.etag.txt')
    else:
        outsubdir = 'html'
        base_url = ('https://api.wikimedia.org/core/v1/wiktionary/'
                   f'{lang_code}/page')
        title_uncoded_osd = self.title_uncoded
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{lang_code}.{self.revision}.html')
        etag_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{lang_code}.{self.revision}.etag.txt')

    cache_usable = False
    if ( (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
            or io_options.cache_mode is io_opts.CacheMode.READ_ONLY)
            and os.path.isfile(cache_file_name)
            and os.path.isfile(etag_file_name)):
        with open(cache_file_name, encoding='utf-8') as f:
            resp_text = f.read()
        with open(etag_file_name, encoding='utf-8') as f:
            etag_text = f.read()
        if resp_text and etag_text:
            cache_usable = True
        else:
            logging.info('Cached html or etag empty so will'
                         ' not be used: %s %s',
                         self.desc, self.title_uncoded)

    if not cache_usable:
        url = f'{base_url}/{_quote_url(self.title_uncoded)}/with_html'
        response = requests.get(url, headers=io_options.headers,
                                timeout=io_options.timeout)
        time.sleep(io_options.sleep_time)
        resp_json = response.json()

        # Check revision in response matches self.revision
        try:
            new_revision = resp_json['latest']['id']
        except KeyError:
            self.status_msg = 'revision not in html response (bad key)'
            logger.error(('Lang %s, %s %s: revision not in html response'
                ' (bad key): status %d'), lang_code, self.desc,
                self.title_uncoded, response.status_code)
            return

        if new_revision != self.revision:
            self.status_msg = 'revision mismatch'
            logger.error(('Lang %s, %s %s: revision mismatch:'
                ' status %d'), lang_code, self.desc, self.title_uncoded,
                response.status_code)
            return

        # Check etag
        try:
            etag_text = response.headers['etag']
        except KeyError:
            self.status_msg = 'etag not in response (bad key)'
            logger.error(('Lang %s, %s %s: etag not in response (bad key):'
                ' status %d'), lang_code, self.desc, self.title_uncoded,
                response.status_code)
            return
        #print(f'html {response.json()}')
        resp_text = response.text
        if (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
                or io_options.cache_mode is io_opts.CacheMode.WRITE_ONLY):
            with open(cache_file_name, 'w', encoding='utf-8') as f:
                f.write(resp_text)
            with open(etag_file_name, 'w', encoding='utf-8') as f:
                f.write(etag_text)
    self.html = resp_text
    self.html_etag = etag_text[3:-1]
    if not self.html:
        logger.error('%s %s: empty self.html', self.desc, self.title_uncoded)
    if not self.html_etag:
        logger.error('%s %s: empty html_etag', self.desc, self.title_uncoded)

def _fetch_current_revision(self: Union[Headword, AudioFile],
         io_options: io_opts.IOOptions, lang_code: str) -> None:
    if not isinstance(self, Headword):
        outsubdir = 'fnsprev'
        title_uncoded_osd = self.title_uncoded_osd
        base_url = 'https://api.wikimedia.org/core/v1/commons/page'
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.json')
    else:
        outsubdir = 'rev'
        title_uncoded_osd = self.title_uncoded
        base_url = ('https://api.wikimedia.org/core/v1/wiktionary/'
                   f'{lang_code}/page')
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{lang_code}.json')

    # See if the cache is usable
    cache_usable = False
    revision = 0
    if ( (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
            or io_options.cache_mode is io_opts.CacheMode.READ_ONLY)
            and os.path.isfile(cache_file_name)):
        with open(cache_file_name, encoding='utf-8') as f:
            resp_json = json.load(f)

        if (('httpCode' in resp_json
            and resp_json['httpCode'] in [200, 404])):
            cache_usable = True
        else:
            try:
                revision = resp_json['latest']['id']
            except KeyError:
                logger.info('Cache file without revision. Refetching: %s %s',
                            self.desc, self.title_uncoded)
            if revision > 0: cache_usable = True

    if not cache_usable:
        url = f'{base_url}/{_quote_url(self.title_uncoded)}/bare'
        response = requests.get(url, headers=io_options.headers,
                                timeout=io_options.timeout)
        time.sleep(io_options.sleep_time)
        resp_json = response.json()
        #print(f'page {resp_json}')
        if (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
                or io_options.cache_mode is io_opts.CacheMode.WRITE_ONLY):
            with open(cache_file_name, 'w', encoding='utf-8') as f:
                json.dump(resp_json, f)

    if 'httpCode' in resp_json and resp_json['httpCode'] == 404:
        self.status_msg = 'Page not found'
        self.revision = 0
        logger.warning('File %s: page not found', self.title_uncoded)
    else:
        try:
            self.revision = resp_json['latest']['id']
        except KeyError:
            self.status_msg = 'revision not in bare response (bad key)'
            logger.error(('Lang %s, %s %s: revision not in bare response'
                ' (bad key): status %d'), lang_code, self.desc,
                self.title_uncoded, response.status_code)
            self.revision = 0

        try:
            self.timestamp = resp_json['latest']['timestamp']
        except KeyError:
            self.timestamp = ''

def _download_wikitext(self: Union[Headword, AudioFile],
                      lang_code: str,
                      io_options: io_opts.IOOptions) -> None:
    if not _is_valid_lang_code(lang_code): return
    #base_url = f'https://{lang_code}.wiktionary.org/api/rest_v1'
    if not isinstance(self, Headword):
        outsubdir = 'fnspwtxt'
        title_uncoded_osd = self.title_uncoded_osd
        base_url = 'https://api.wikimedia.org/core/v1/commons/page'
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{self.revision}.txt')
    else:
        outsubdir = 'wtxt'
        title_uncoded_osd = self.title_uncoded
        base_url = ('https://api.wikimedia.org/core/v1/wiktionary/'
                   f'{lang_code}/page')
        cache_file_name = os.path.join(io_options.output_dir, outsubdir,
            io_options.add_subdir_fn(self.title_uncoded),
            f'{title_uncoded_osd}.{lang_code}.{self.revision}.txt')

    if ( (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
            or io_options.cache_mode is io_opts.CacheMode.READ_ONLY)
            and os.path.isfile(cache_file_name)):
        with open(cache_file_name, encoding='utf-8') as f:
            resp_text = f.read()
    else:
        url = f'{base_url}/{_quote_url(self.title_uncoded)}'
        #params: Dict[str, Union[str, int]] = {
        #    'title' : _quote_url(self.title_uncoded),
        #    'revision' : self.revision,
        #    'if-match' : self.html_etag
        #}
        #body = {
        #    'html' : self.html
        #}
        #response = requests.post(url, headers=io_options.headers,
        #    params = params, data=body, timeout=io_options.timeout)
        response = requests.get(url, headers=io_options.headers,
            timeout=io_options.timeout)
        time.sleep(io_options.sleep_time)
        resp_json = response.json()

        # Check revision in response matches self.revision
        try:
            new_revision = resp_json['latest']['id']
        except KeyError:
            self.status_msg = 'revision not in page response (bad key)'
            logger.error(('Lang %s, %s %s: revision not in page response'
                ' (bad key): status %d'), lang_code, self.desc,
                self.title_uncoded, response.status_code)
            return

        if new_revision != self.revision:
            self.status_msg = 'revision mismatch'
            logger.error(('Lang %s, %s %s: page revision mismatch:'
                ' status %d'), lang_code, self.desc, self.title_uncoded,
                response.status_code)
            return

        try:
            resp_text = resp_json['source']
        except KeyError:
            self.status_msg = 'source not in response (bad key)'
            logger.error('Lang %s, %s %s: source not in response (bad key)',
                lang_code, self.desc, self.title_uncoded)
            resp_text = ''
        if (io_options.cache_mode is io_opts.CacheMode.READ_AND_WRITE
                or io_options.cache_mode is io_opts.CacheMode.WRITE_ONLY):
            with open(cache_file_name, 'w', encoding='utf-8') as f:
                f.write(resp_text)
    self.wikitext = resp_text
    if not self.wikitext:
        logger.error('%s %s: empty self.wikitext',
                     self.desc, self.title_uncoded)

