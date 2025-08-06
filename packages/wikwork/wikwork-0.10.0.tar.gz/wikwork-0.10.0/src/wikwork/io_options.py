#    Manage input/output options and creates the cache/output directory
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

"""Manage input/output options and creates the cache/output directory.

This class stores loosely related variables for internet requests and
manages the cache/output directories. It validates some input, protects
some options from direct update, and creates the seven first-level
subdirectories of the `lang_code` subdirectory.
"""

#------------------------------------------------------------------------------
# File:    io_options.py
# Date:    2024-02-23
# Author:  Ray Griner
# Changes:
# 20240301RG: Add __author__ and __all___
# 20240908RG: (1) Create new subdirectories of cache/output directory for
# storing HTML/wikitext info only for audio files where download is requested.
# (New subdirs: fnspwtxtr and fnsphtmlr). (2) Allow user to set
# IOOptions.AudioOutMode to NO_OVERWRITE and OVERWRITE to allow downloading
# of audio files. Code elsewhere already implemented the functionality to do
# the download, but here users were previously only allowed to set to
# NO_OVERWRITE.
# 20250625RG: Add `fetch_html` attribute to `IOOptions`.
#------------------------------------------------------------------------------
__author__ = 'Ray Griner'
__all__ = ['CacheMode','AudioOutMode','IOOptions']

import logging
import enum
import os
from collections.abc import Callable
from typing import Dict, Union

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
# Type aliases
#------------------------------------------------------------------------------
CacheMode = enum.Enum('CacheMode',
    ['NO_READ_OR_WRITE', 'READ_ONLY','WRITE_ONLY','READ_AND_WRITE'])
AudioOutMode = enum.Enum('AudioOutMode',
    ['NO_OUTPUT', 'NO_OVERWRITE','OVERWRITE'])
HttpHeaders = Dict[str, str]
AddSubdirFn = Callable[[str], str]
Timeout = Union[float, tuple[Union[int, float], Union[int, float]]]

#------------------------------------------------------------------------------
# Class definitions
#------------------------------------------------------------------------------
class IOOptions:
    """Control parameters for internet requests and local cache/output.

    This class stores loosely related variables for internet requests and
    managing the cache/output directories. It doesn't do much except
    validate input, protect some values from direct update, and create
    the seven first level subdirectories of the `output_dir` subdirectory.

    Attributes
    ----------
    headers : Dict[str, str]
        Dictionary of headers that will be sent with the HTTP requests. See
        `__init__` for details.
    add_subdir_fn : Callable[str, str], optional
        User-defined function that takes as input a string and outputs a
        string representing additional subdirectories to be used within the
        seven application-defined subdirectories (listed in `Notes`) for
        the cache and audio output.  The purpose is to prevent too many
        files from being in a single directory, which can degrades
        performance. See `__init__` for details.
    cache_mode : {CacheMode.READ_AND_WRITE, CacheMode.READ_ONLY,
                  CacheMode.WRITE_ONLY, CacheMode.NO_READ_OR_WRITE}
        Specifies how to use the cache/output directories when making REST
        API calls.
    audio_out_mode : {AudioOutMode.NO_OUTPUT (default),
                      AudioOutMode.OVERWRITE, AudioOutMode.NO_OVERWRITE}
        Controls whether audio files are to be output (ie, downloaded), and
        if so, whether existing files should be overwritten.
    sleep_time : float
        Length of time to sleep after each REST API call.
    """

    def __init__(self, output_dir: str,
                 headers: HttpHeaders,
                 project: str,
                 add_subdir_fn: AddSubdirFn = lambda x: '',
                 cache_mode: CacheMode = CacheMode.READ_AND_WRITE,
                 audio_out_mode: AudioOutMode = AudioOutMode.NO_OUTPUT,
                 sleep_time: float = 0.006, timeout: Timeout = 10,
                 fetch_html: bool = False,
                ) -> None:
        """Initialize instance and create first level subdirectories.

        Parameters
        ----------
        output_dir : str
            Root of output directory.  Seven subdirectories will be created
            under this directory. See `Notes` for details.
        headword_lang_code : str
            Language code specifying the language of the Wiktionary™ that
            the data should be retrieved from. This is the first part of
            the URL used on the internet. For example, if the URL is
            https://en.wiktionary.org, then 'en' should be passed. See:
            https://en.wikipedia.org/wiki/Wikipedia:List_of_Wiktionaries.
        headers : Dict[str, str]
            Dictionary of headers that will be sent with the HTTP requests.
            This must contain a key of 'User-Agent' or 'Api-User-Agent' and
            the value should be your contact information (although this is
            only enforced by the constructor). Per the Wikimedia REST API
            documentation (https://en.wiktionary.org/api/rest_v1/):
            "Set a unique User-Agent or Api-User-Agent header that allows
            [Wikimedia] to contact you quickly. Email addresses or URLs of
            contact pages work well."
        add_subdir_fn : Callable[str, str], optional
            User-defined function that takes as input a string and
            outputs a string representing additional subdirectories to be
            used within the seven application-defined subdirectories (see
            `Notes` for list). This will be called on the title_uncoded
            attribute of a Headword or AudioFile object when using the
            cache/output. The purpose is to prevent too many files from
            being in a single directory, which can degrade performance.
            Note that any subdirectories implied by this function need to
            be created by the user. They are not automatically created
            during object construction.
        cache_mode : {CacheMode.READ_AND_WRITE (default),
                      CacheMode.READ_ONLY, CacheMode.WRITE_ONLY,
                      CacheMode.NO_READ_OR_WRITE}
            Specifies how to use the local cache/output when making REST
            API calls.
        timeout : float, default = 10
            Timeout parameter that will be passed in HTTP request headers.
        fetch_html : bool, default = False
            Controls whether output is downloaded in HTML format in addition
            to wikitext format.

        Notes
        -----
        If the revision is part of the request made to Wikimedia REST APIs,
        then the revision is part of the cached filename before the file
        extension.

        The subdirectories of `output_dir` that will be created by the
        function are the following:

        'rev': page revision info for the word page
        'fnsprev': page revision info for the audio file page (ie, the
            page in the 'File:' namespace).
        'medlist': Media list for the word page
        'html': html output for the word page (where page revision is as
            stored in the 'rev' folder. Also contains a file with
            extension .etag.txt which is the eTag header from the HTTP
            response (and which is passed when requesting the wikitext).
        'fnsphtml' - html and etag output for the audio file page (where
            page revision is as stored in the 'fnsprev' folder).
        'fnsphtmlr' - like `fnsphtml`. Copy corrensponding file from
            `fnsphtml` if download is requested (ie, request_stats=="Y")
            for the file or dictionary passed as input to the
            `wrapper.input_audio_reqs` parameter or to
            `AudioFile.update_req_status()`
        'wtxt' - wikitext output from transforming the html and eTag in the
            html folder (for page revision as stored in the 'fnsprev'
            folder)
        'fnspwtxt' - wikitext output from transforming the html and eTag in
            the 'fnsphtml' folder (for page revision as stored in the
            'fnsprev' folder)
        'fnspwtxtr' - like `fnspwtxt`, copy corresponding file from
            `fnspwtxt` if download is requested. See note above on
            `fnsphtmlr` for details.

        Trademark Notice
        ----------------
        Wiktionary and Wikimedia are trademarks of the Wikimedia Foundation
        and are used with the permission of the Wikimedia Foundation. We
        are not endorsed by or affiliated with the Wikimedia Foundation.

        """
        self._output_dir: str = output_dir
        self._timeout: Timeout
        self._sleep_time: float
        self.headers: HttpHeaders = headers
        self.add_subdir_fn: AddSubdirFn = add_subdir_fn
        self.audio_out_mode: AudioOutMode = audio_out_mode # call the setter
        self.cache_mode: CacheMode = cache_mode
        self.timeout = timeout        # call the setter
        self.sleep_time = sleep_time
        self.fetch_html = fetch_html
        if project == 'Wiktionary':
            self._project = project
        else:
            raise ValueError('IOOptions: only valid value for project is'
                             "'Wiktionary'")

        if not 'User-Agent' in headers and not 'Api-User-Agent' in headers:
            logger.error("IOOptions: No 'User-Agent' or "
                         "'Api-User-Agent' header")
            raise ValueError("IOOptions: No 'User-Agent' or "
                             "'Api-User-Agent' key in header parameter")

        for leafdir in (['rev', 'medlist', 'html', 'allaudio', 'fnspwtxt',
              'wtxt','fnsprev', 'fnsphtml', 'fnspwtxt', 'fnspwtxtr',
              'fnsphtmlr']):
            os.makedirs(os.path.join(self.output_dir, leafdir), exist_ok=True)

    def __repr__(self) -> str:
        return(f'IOOptions(output_dir="{self.output_dir}", '
            f'headers="{self.headers}", '
            f'add_subdir_fn={self.add_subdir_fn}, '
            f'cache_mode={self.cache_mode}, '
            f'audio_out_mode={self.audio_out_mode}, '
            f'sleep_time={self.sleep_time}, '
            f'timeout={self.timeout})')

    @property
    def project(self) -> str:
        """Wikimedia project to fetch from. Must be 'Wiktionary'. """
        return self._project

    @property
    def output_dir(self) -> str:
        """Output directory. """
        return self._output_dir

    @property
    def sleep_time(self) -> float:
        """Length of time to sleep after each REST API call.

        Must be >= 0.005 (the REST APIs to which this parameter is passed
        indicate a limit of 200 calls per second).
        """
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, sleep_time: float) -> None:
        if sleep_time<0.005:
            raise ValueError(f'IOOptions: {sleep_time=} must be >= 0.005 ')
        else:
            self._sleep_time = sleep_time


    @property
    def audio_out_mode(self) -> AudioOutMode:
        """Controls download/overwriting of audio files.

        Must be AudioOutMode.NO_OUTPUT, AudioOutMode.OVERWRITE, or
        AudioOutMode.NO_OVERWRITE.
        """
        return self._audio_out_mode

    @audio_out_mode.setter
    def audio_out_mode(self, audio_out_mode: AudioOutMode) -> None:
        if not audio_out_mode in [AudioOutMode.NO_OUTPUT,
                AudioOutMode.OVERWRITE, AudioOutMode.NO_OVERWRITE]:
            raise ValueError('IOOptions: audio_out_mode must be '
                'AudioOutMode.NO_OUTPUT, AudioOutMode.OVERWRITE, '
                'or AudioOutMode.NO_OVERWRITE')
        else:
            self._audio_out_mode = audio_out_mode
        self._audio_out_mode = audio_out_mode

    @property
    def timeout(self) -> Timeout:
        """Timeout parameter passed to the requests package.

        Should be either a float or a 2-tuple of floats. Any value must
        be >0.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: Timeout) -> None:
        if isinstance(timeout, tuple):
            for i, tout in enumerate(timeout):
                if tout<=0:
                    raise ValueError('IOOptions: timeout tuple has value '
                                     f'({tout})<=0 at position {i}')
        elif timeout<=0:
            raise ValueError(f'IOOptions: {timeout=} must be > 0')

        self._timeout = timeout

