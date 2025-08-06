#    CzechWord subclass and related functions.
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

""" CzechWord subclass and related functions. """

#------------------------------------------------------------------------------
# File:    czech.py
# Author:  Ray Griner
# Date:    2024-03-11
# Changes:
#------------------------------------------------------------------------------
__author__ = 'Ray Griner'
#__all__ = ['AudioFile','Headword']

# Standard modules
import re
import logging
#import collections
from typing import Optional
from wikwork import page_media
from wikwork import parse
from wikwork import io_options as io_opts

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
# Type aliases
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Class definition: GermanWord
#------------------------------------------------------------------------------
class CzechEntry():
    """Czech Wiktionary™ entry with selected attributes parsed from wikitext.

    Selected elements of the dictionary entries (for the same language as
    the Wiktionary) parsed from the wikitext.

    The attributes attracted from the noun, verb, and adjective templates
    start with 'adj_', 'verb_', and 'noun_', respectively, and are a single
    string and do contain some wikitext. Other attributes are lists of
    strings found after an identifying header in the wikitext. These
    attributes still do contain wikitext, although it may be replaced in
    the future.

    Attributes
    ----------
    definitions : list[str]
        Lines after '==== význam ====' header. Sometimes includes examples.
    etymology_entry : list[str]
        Lines after '==== etymologie ====' header. Note that lines after
        '=== etymologie ===' are in `CzechWord.etymology`.
    synonyms : list[str]
        Lines after '==== synonyma ====' header.
    antonyms : list[str]
        Lines after '==== antonyma ====' header.
    examples : list[str]
        Lines after '==== překlady ====' header.
    expressions : list[str]
        Lines after '==== fráze a idiomy ====' or '==== fráze ====' header.
    sayings : list[str]
        Lines after '==== přísloví ====' or
        '==== přísloví, rčení a pořekadla ====' or
        '==== přísloví, úsloví a pořekadla ====' headers.
    related_words : list[str]
        Lines after '==== související ====' header.
    variants : list[str]
        Lines after '==== varianty ====' header.
    word_combos : list[str]
        Lines after '==== slovní spojení ====' header.
    abbreviations : list[str]
        Lines after '==== zkratky ====' header.
    declesions : list[str]
        Lines after '==== skloňování ====' or '==== skloňování (1) ====' or
        '==== skloňování (2) ====' or '==== skloňování (3) ====' headers.
    collocations : list[str]
        Lines after '==== kolokace ====' header.
    part_of_speech : str
        Will be set to a the indicated value if a header indicating a
        part of speech is found. Note that this also causes a new entry
        to be created.
            -----------------------------------------------
            Header                        Value
            -----------------------------------------------
            '=== podstatné jméno ==='     'noun'
            '=== přídavné jméno ==='      'adjective'
            '=== zájmeno ==='             'pronoun'
            '=== číslovka ==='            'numeral'
            '=== sloveso ==='             'verb'
            '=== příslovce ==='           'adverb'
            '=== předložka ==='           'preposition'
            '=== spojka ==='              'conjunction'
            '=== částice ==='             'particle'
            '=== citoslovce ==='          'interjection'
            '=== slovní spojení ==='      'word combination'
            '=== fráze ==='               'phrase'
            '=== idiom ==='               'idiom'
            '=== přísloví ==='            'proverb'
            '=== zkratka ==='             'abbreviation'
            '=== předpona ==='            'prefix'
            '=== přípona ==='             'suffix'
            '=== číslo ==='               'number'
            '=== značka ==='              'mark'
            '=== symbol ==='              'symbol'
            -----------------------------------------------
    part_of_speech_info : str
        Any lines after the header that set the `part_of_speech` attribute.
    adj_comp : str
        Comparative form of adjective. 'komp' parameter of '{{Stupňování}}'
        template.
    adj_comp2 : str
        Alternate comparative form of adjective. 'komp2' parameter of
        '{{Stupňování}}' template.
    adj_super :
        Superlative form of adjective. 'sup' parameter of '{{Stupňování}}'
        template.
    adj_super2 : str
        Alternate superlative form of adjective. 'sup2' parameter of
        '{{Stupňování}}' template.

    verb_aspect : str
        Verb aspect. Set to 'imperfective' if the line "* ''nedokonavé''"
        is found in the verb section (ie, after the heading that set
        `part_of_speech`='verb'. Set to 'perfective' if the line
        "* ''dokonavé''" is found in the verb section or if the
        'Sloveso (cs)' template (ie, the verb template) has parameter
        'dok' with value 'ano'.  If these two sources conflict, the verb
        template is used.

    verb_conj_1s : str
        Indicative first person singular. From 'spre1' parameter of the
        verb template. If the verb aspect is imperfective, the tense
        is present. Otherwise, the tense is future.
    verb_conj_2s : str
        Indicative second person singular. From 'spre2' parameter of the
        verb template. See notes on `verb_conj_1s` for tense.
    verb_conj_3s : str
        Indicative third person singular. From 'spre3' parameter of the
        verb template. See notes on `verb_conj_1s` for tense.
    verb_conj_1p : str
        Indicative first person plural. From 'ppre1' parameter of the
        verb template. See notes on `verb_conj_1s` for tense.
    verb_conj_2p : str
        Indicative second person plural. From 'ppre2' parameter of the
        verb template. See notes on `verb_conj_1s` for tense.
    verb_conj_3p : str
        Indicative third person plural. From 'ppre3' parameter of the
        verb template. See notes on `verb_conj_1s` for tense.

    verb_fut_1s : str
        Future first person singular. From 'sfut1' parameter of the
        verb template if the 'fut' parameter is populated. (This parameter
        will not always be populated.)
    verb_fut_2s : str
        Future second person singular. From 'sfut2' parameter of the
        verb template if the 'fut' parameter is populated.
    verb_fut_3s : str
        Future third person singular. From 'sfut3' parameter of the
        verb template if the 'fut' parameter is populated.
    verb_fut_1p : str
        Future first person plural. From 'pfut1' parameter of the
        verb template if the 'fut' parameter is populated.
    verb_fut_2p : str
        Future second person plural. From 'pfut2' parameter of the
        verb template if the 'fut' parameter is populated.
    verb_fut_3s : str
        Future third person plural. From 'pfut3' parameter of the
        verb template if the 'fut' parameter is populated.

    verb_past_part_ms : str
        Past participle masculine singular. From 'sactm' parameter of
        the verb template.
    verb_past_part_fs : str
        Past participle feminine singular. From 'sactf' parameter of
        the verb template.
    verb_past_part_ns : str
        Past participle neuter singular. From 'sactn' parameter of
        the verb template.
    verb_past_part_mp : str
        Past participle masculine plural. From 'pactm' parameter of
        the verb template.
    verb_past_part_fp : str
        Past participle feminine plural. From 'pactf' parameter of
        the verb template.
    verb_past_part_np : str
        Past participle neuter plural. From 'sactf' parameter of
        the verb template (ie, by definition equals `verb_past_part_fs`).
    verb_pass_part_ms : str
        Passive participle masculine singular. From 'spasm' parameter of
        the verb template.
    verb_pass_part_fs : str
        Passive participle feminine singular. From 'spasf' parameter of
        the verb template.
    verb_pass_part_ns : str
        Passive participle neuter singular. From 'spasn' parameter of
        the verb template.
    verb_pass_part_mp : str
        Passive participle masculine plural. From 'ppasm' parameter of
        the verb template.
    verb_pass_part_fp : str
        Passive participle feminine plural. From 'ppasf' parameter of
        the verb template.
    verb_pass_part_np : str
        Passive participle neuter plural. From 'spasf' parameter of
        the verb template (ie, by definition equals `verb_pass_part_fs`).

    verb_imper_2s : str
        Imperative (second person) singular. From 'simp2' parameter of the
        verb template.
    verb_imper_1p : str
        Imperative first person plural . From 'pimp1' parameter of the
        verb template.
    verb_imper_2p : str
        Imperative second person plural . From 'pimp2' parameter of the
        verb template.

    verb_pres_trans_ms : str
        Present transgressive masculine singular. From 'ptram' parameter of
        the verb template.
    verb_pres_trans_fns : str
        Present transgressive feminine/neuter singular. From 'ptraf'
        parameter of the verb template.
    verb_pres_trans_p : str
        Present transgressive plural. From 'ptrap' parameter of the verb
        template.
    verb_past_trans_ms : str
        Past transgressive masculine singular. From 'mtram' parameter of
        the verb template.
    verb_past_trans_fns : str
        Past transgressive feminine/neuter singular. From 'mtraf' parameter
        of the verb template.
    verb_past_trans_p : str
        Past transgressive plural. From 'mtrap' parameter of the verb
        template.

    noun_gender_subcat : str
        Detailed noun gender. Extracted from lines matching the patterns
        below in the 'noun' section (ie, lines after a heading that
        set `part_of_speech` = 'noun').
            Line                            Value
            ----------------------------------------------
            "* ''rod mužský neživotný''"    'm : inanimate'
            "* ''rod mužský životný''"      'm : animate'
            "* ''rod mužský''"              'm'
            "* ''rod střední''"             'n'
            "* ''rod ženský''"              'f'
            ----------------------------------------------
        A message is printed to the log for other strings that start with
            "* ''rod " that don't match the above.
    noun_gender : str
        The first character of noun_gender_subcat (so 'm', 'f', or 'n').
    noun_nom_s : str
        Noun nominative singular. 'snom' parameter of 'Substantivum (cs)'
        template (ie, the 'noun template').
    noun_nom_p : str
        Noun nominative plural. 'pnom' parameter of the noun template.
    noun_acc_s : str
        Noun accusative singular. 'sacc' parameter of the noun template.
    noun_acc_p : str
        Noun accusative plural. 'pacc' parameter of the noun template.
    noun_voc_s : str
        Noun vocative singular. 'svoc' parameter of the noun template.
    noun_voc_p : str
        Noun vocative plural. 'pvoc' parameter of the noun template.
    noun_loc_s : str
        Noun locative singular. 'sloc' parameter of the noun template.
    noun_loc_p : str
        Noun locative plural. 'ploc' parameter of the noun template.
    noun_dat_s : str
        Noun dative singular. 'sdat' parameter of the noun template.
    noun_dat_p : str
        Noun dative plural. 'pdat' parameter of the noun template.
    noun_gen_s : str
        Noun genitive singular. 'sgen' parameter of the noun template.
    noun_gen_p : str
        Noun genitive plural. 'pgen' parameter of the noun template.
    noun_inst_s : str
        Noun instrumental singular. 'sins' parameter of the noun template.
    noun_inst_p : str
        Noun instrumental plural. 'pins' parameter of the noun template.
    """
    def __init__(self) -> None :
        """ Initialize entry. Set contents to empty lists or strings. """
        self.definitions: list[str] = []
        self.etymology_entry: list[str] = []
        self.synonyms: list[str] = []
        self.antonyms: list[str] = []
        self.examples: list[str] = []
        self.expressions: list[str] = []
        self.sayings: list[str] = []
        self.related_words: list[str] = []
        self.variants: list[str] = []
        self.word_combos: list[str] = []
        self.abbreviations: list[str] = []
        self.declensions: list[str] = []
        self.collocations: list[str] = []

        # From headings indicating the part of speech
        self.part_of_speech: str = ''
        self.part_of_speech_info: str = ''

        # From parsing templates with grammar info
        self._adj_written: bool = False
        self.adj_comp : str = ''
        self.adj_comp2 : str = ''
        self.adj_super : str = ''
        self.adj_super2 : str = ''

        self._verb_written: bool = False
        self.verb_aspect = ''
        self.verb_conj_1s: str = ''
        self.verb_conj_2s: str = ''
        self.verb_conj_3s: str = ''
        self.verb_conj_1p: str = ''
        self.verb_conj_2p: str = ''
        self.verb_conj_3p: str = ''
        self.verb_past_part_ms: str = ''
        self.verb_past_part_fs: str = ''
        self.verb_past_part_ns: str = ''
        self.verb_past_part_mp: str = ''
        self.verb_past_part_fp: str = ''
        self.verb_past_part_np: str = ''
        self.verb_pass_part_ms: str = ''
        self.verb_pass_part_fs: str = ''
        self.verb_pass_part_ns: str = ''
        self.verb_pass_part_mp: str = ''
        self.verb_pass_part_fp: str = ''
        self.verb_pass_part_np: str = ''
        self.verb_imper_2s: str = ''
        self.verb_imper_1p: str = ''
        self.verb_imper_2p: str = ''
        self.verb_pres_trans_ms: str = ''
        self.verb_pres_trans_fns: str = ''
        self.verb_pres_trans_p: str = ''
        self.verb_past_trans_ms: str = ''
        self.verb_past_trans_fns: str = ''
        self.verb_past_trans_p: str = ''

        self._noun_written: bool = False
        self.noun_gender_subcat: str = ''
        self.noun_gender: str = ''
        self.noun_nom_s: str = ''
        self.noun_nom_p: str = ''
        self.noun_acc_s: str = ''
        self.noun_acc_p: str = ''
        self.noun_voc_s: str = ''
        self.noun_voc_p: str = ''
        self.noun_loc_s: str = ''
        self.noun_loc_p: str = ''
        self.noun_gen_s: str = ''
        self.noun_gen_p: str = ''
        self.noun_dat_s: str = ''
        self.noun_dat_p: str = ''
        self.noun_inst_s: str = ''
        self.noun_inst_p: str = ''

    def __repr__(self) -> str:
        selfvars = vars(self)
        output_list = []
        for k, v in selfvars.items():
            output_list.append(f'{k}="{v}"')
        return 'CzechEntry(' + ', '.join(output_list) + ')'

class CzechWord(page_media.Headword):
    """Headword information and associated audio files for German headword.

    Attributes (see `page_media.Headword for inherited attributes)
    --------------------------------------------------------------
    entries: list[CzechEntry]
        A list of entries. An entry is created every time a heading
        in the wikitext is indicates a part of speech.  (See
        `CzechEntry.part_of_speech` for details.)
    pronunciations : list[str]
        Lines after '=== výslovnost ===' header.
    word_separations : list[str]
        Lines after '=== dělení ===' header.
    etymology : list[str]
        Lines after '=== výslovnost ===' header.
    external_links : list[str]
        Lines after '=== externí odkazy ===' header.
    variants : list[str]
        Lines after '=== varianty ===' header.
    references : list[str]
        Lines after '== poznámky ==' header.
    """

    def __init__(self, headword: str, lang_code: str):
        """Initialize instance.

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
        super().__init__(headword=headword, lang_code=lang_code)
        self.entries: list[CzechEntry] = []
        self.pronunciations = ''
        self.word_separations = ''
        self.etymology = ''
        self.variants = ''
        self.external_links = ''
        self.references = ''

    def __repr__(self) -> str:
        return ('CzechWord('
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
            '], ' +
            f'   pronunciations="{self.pronunciations}",'
            f'   word_separations="{self.word_separations}",'
            f'   etymology="{self.etymology}",'
            f'   variants="{self.variants}",'
            f'   external_links="{self.external_links}",'
            f'   references="{self.references}",'
            '    entries=[' +
            '\n'.join([f'    {entry}' for entry in self.entries]) +
            '])\n')

    #----------------
    # Public methods
    #----------------
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
        super().fetch_word_page(io_options=io_options)
        _parse_wikitext(self)

    def add_new_entry(self) -> int:
        """Add a new empty entry to the `entries` attribute."""
        self.entries.append(CzechEntry())
        return len(self.entries)-1

#------------------
# Private functions
#------------------
def _parse_verb_template(self: CzechWord, line: str) -> bool:
    """Parse line containing verb template and update entry.
    """
    current_entry = self.entries[-1]
    if current_entry._verb_written:
        logger.info('Word %s: Template not handled: already found: %s',
            self.headword, line)
        return True
    wiki_temp, err_msg = parse.parse_one_template(line)
    if wiki_temp is None:
        logger.warning('Word: %s: Template parser: %s',
                        self.headword, err_msg)
        return False

    temp_dict = wiki_temp.params

    verb_aspect = temp_dict.get('dok', '')
    if verb_aspect == 'ano':
        if current_entry.verb_aspect == 'imperfective':
            logger.warning('Overwriting verb aspect: Word %s',
                           self.headword)
        current_entry.verb_aspect = 'perfective'

    current_entry.verb_conj_1s = temp_dict.get('spre1', '')
    current_entry.verb_conj_2s = temp_dict.get('spre2', '')
    current_entry.verb_conj_3s = temp_dict.get('spre3', '')
    current_entry.verb_conj_1p = temp_dict.get('ppre1', '')
    current_entry.verb_conj_2p = temp_dict.get('ppre2', '')
    current_entry.verb_conj_3p = temp_dict.get('ppre3', '')

    current_entry.verb_past_part_ms = temp_dict.get('sactm', '')
    current_entry.verb_past_part_fs = temp_dict.get('sactf', '')
    current_entry.verb_past_part_ns = temp_dict.get('sactn', '')
    current_entry.verb_past_part_mp = temp_dict.get('pactm', '')
    current_entry.verb_past_part_fp = temp_dict.get('pactf', '')
    current_entry.verb_past_part_np = temp_dict.get('sactf', '')

    current_entry.verb_pass_part_ms = temp_dict.get('spasm', '')
    current_entry.verb_pass_part_fs = temp_dict.get('spasf', '')
    current_entry.verb_pass_part_ns = temp_dict.get('spasn', '')
    current_entry.verb_pass_part_mp = temp_dict.get('ppasm', '')
    current_entry.verb_pass_part_fp = temp_dict.get('ppasf', '')
    current_entry.verb_pass_part_np = temp_dict.get('spasf', '')

    current_entry.verb_pres_trans_ms = temp_dict.get('ptram', '')
    current_entry.verb_pres_trans_fns = temp_dict.get('ptraf', '')
    current_entry.verb_pres_trans_p = temp_dict.get('ptrap', '')
    current_entry.verb_past_trans_ms = temp_dict.get('mtram', '')
    current_entry.verb_past_trans_fns = temp_dict.get('mtraf', '')
    current_entry.verb_past_trans_p = temp_dict.get('mtrap', '')

    current_entry.verb_imper_2s = temp_dict.get('simp2', '')
    current_entry.verb_imper_1p = temp_dict.get('pimp1', '')
    current_entry.verb_imper_2p = temp_dict.get('pimp2', '')
    return True

def _parse_noun_template(self: CzechWord, line: str) -> bool:
    """Parse line containing noun template and update entry.
    """
    current_entry = self.entries[-1]
    if current_entry._noun_written:
        logger.info('Word %s: Template not handled: already found: %s',
            self.headword, line)
        return True
    wiki_temp, err_msg = parse.parse_one_template(line)
    if wiki_temp is None:
        logger.warning('Word: %s: Template parser: %s',
                        self.headword, err_msg)
        return False

    temp_dict = wiki_temp.params

    current_entry._noun_written = True
    current_entry.noun_nom_s = temp_dict.get('snom', '')
    current_entry.noun_nom_p = temp_dict.get('pnom', '')
    current_entry.noun_acc_s = temp_dict.get('sacc', '')
    current_entry.noun_acc_p = temp_dict.get('pacc', '')
    current_entry.noun_voc_s = temp_dict.get('svoc', '')
    current_entry.noun_voc_p = temp_dict.get('pvoc', '')
    current_entry.noun_loc_s = temp_dict.get('sloc', '')
    current_entry.noun_loc_p = temp_dict.get('ploc', '')
    current_entry.noun_dat_s = temp_dict.get('sdat', '')
    current_entry.noun_dat_p = temp_dict.get('pdat', '')
    current_entry.noun_gen_s = temp_dict.get('sgen', '')
    current_entry.noun_gen_p = temp_dict.get('pgen', '')
    current_entry.noun_inst_s = temp_dict.get('sins', '')
    current_entry.noun_inst_p = temp_dict.get('pins', '')
    return True

def _parse_adjective_template(self: CzechWord, line: str) -> bool:
    """Parse line containing adjective template and update entry.
    """
    wiki_temp, err_msg = parse.parse_one_template(line)
    if wiki_temp is None:
        logger.warning('Word: %s: Template parser: %s',
                        self.headword, err_msg)
        return False
    temp_dict = wiki_temp.params
    entry = self.entries[-1]

    if entry._adj_written:
        logger.info('Word %s: Template not handled: already found: %s',
            self.headword, line)
        return False

    entry._adj_written = True
    entry.adj_comp = temp_dict.get('komp','')
    entry.adj_comp2 = temp_dict.get('komp2','')
    entry.adj_super = temp_dict.get('sup','')
    entry.adj_super2 = temp_dict.get('sup2','')
    return True

def _parse_wikitext(self: CzechWord) -> None:
    """Parse the wikitext and put results in the entries attribute.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    # List of templates and the field the result will be put in
    line_to_attrib_dict: dict[str, parse.Attr] = {
        '== poznámky ==' : parse.Attr(2, 'references'),

        '=== dělení ===' : parse.Attr(3, 'word_separations'),
        '=== výslovnost ===' : parse.Attr(3, 'pronunciations'),
        '=== výslovnost (1) ===' : parse.Attr(3,'pronunciations'),
        #'=== výslovnost (2) ===' : parse.Attr(3,'pronunciations'),
        '=== etymologie ===' : parse.Attr(3,'etymology'),
        '== externí odkazy ==' : parse.Attr(3, 'external_links'),
        '=== varianty ===' : parse.Attr(3, 'variants'),

        '==== význam ====' : parse.Attr(4,'definitions'),
        '==== etymologie ====' : parse.Attr(4,'etymology_entry'),
        '==== synonyma ====' : parse.Attr(4,'synonyms'),
        '==== antonyma ====' : parse.Attr(4,'antonyms'),
        '==== překlady ====' : parse.Attr(4,'examples'),
        '==== fráze a idiomy ====' : parse.Attr(4,'expressions'),
        '==== fráze ====' : parse.Attr(4,'expressions'),

        # next two section headers refer to sections that should contain
        # templates that are parsed, so can ignore
        '==== stupňování ====' : parse.Attr(0, 'IGNORE'), # adj compare
        '==== časování ====' : parse.Attr(0,'IGNORE'), # verb conjugation
        '==== přísloví ====' : parse.Attr(4,'sayings'),
        '==== přísloví, rčení a pořekadla ====' : parse.Attr(4, 'sayings'),
        '==== přísloví, úsloví a pořekadla ====' : parse.Attr(4, 'sayings'),
        '==== související ====' : parse.Attr(4, 'related_words'),
        '==== varianty ====' : parse.Attr(4, 'variants'),
        '==== slovní spojení ====' : parse.Attr(4, 'word_combos'),
        '==== zkratky ====' : parse.Attr(4, 'abbreviations'),
        #'==== zkratka ====' : parse.Attr(4, 'abbreviations')
        '==== skloňování ====': parse.Attr(4, 'declensions'),
        '==== skloňování (1) ====': parse.Attr(4, 'declensions'),
        #'==== skloňování (2) ====': parse.Attr(4, 'declensions'),
        #'==== skloňování (3) ====': parse.Attr(4, 'declensions'),
        '==== kolokace ====' : parse.Attr(4, 'collocations'),
        #'==== skloňování jednotného čísla ====': 'declensions',

        '=== podstatné jméno ===' : parse.Attr(4, 'part_of_speech_info',
                                               'noun'),
        '=== přídavné jméno ===' : parse.Attr(4, 'part_of_speech_info',
                                             'adjective'),
        '=== zájmeno ===' : parse.Attr(4, 'part_of_speech_info', 'pronoun'),
        '=== číslovka ===' : parse.Attr(4, 'part_of_speech_info', 'numeral'),
        '=== sloveso ===' : parse.Attr(4, 'part_of_speech_info', 'verb'),
        '=== příslovce ===' : parse.Attr(4, 'part_of_speech_info', 'adverb'),
        '=== předložka ===' : parse.Attr(4, 'part_of_speech_info',
                                        'preposition'),
        '=== spojka ===' : parse.Attr(4, 'part_of_speech_info', 'conjunction'),
        '=== částice ===' : parse.Attr(4, 'part_of_speech_info', 'particle'),
        '=== citoslovce ===' : parse.Attr(4, 'part_of_speech_info',
                                          'interjection'),
        '=== slovní spojení ===' : parse.Attr(4, 'part_of_speech_info',
                                              'word combination'),
        '=== fráze ===' : parse.Attr(4, 'part_of_speech_info', 'phrase'),
        '=== idiom ===' : parse.Attr(4, 'part_of_speech_info', 'idiom'),
        '=== přísloví ===' : parse.Attr(4, 'part_of_speech_info', 'proverb'),
        '=== zkratka ===' : parse.Attr(4, 'part_of_speech_info',
                                       'abbreviation'),
        '=== předpona ===' : parse.Attr(4, 'part_of_speech_info', 'prefix'),
        '=== přípona ===' : parse.Attr(4, 'part_of_speech_info', 'suffix'),
        '=== číslo ===' : parse.Attr(4, 'part_of_speech_info', 'number'),
        '=== značka ===' : parse.Attr(4, 'part_of_speech_info', 'mark'),
        '=== symbol ===' : parse.Attr(4, 'part_of_speech_info', 'symbol'),
        '[[Kategorie:' : parse.Attr(0, 'IGNORE')
        #'=== starší varianta zápisu ===' : 'IGNORE',
        #'' : 'hyponyms',
        #'' : 'hypernyms',
        #'' : 'syntax',
        #'' : 'meronyms',
        #'' : 'holonyms',
        #'' : 'cautions',
    }
    # TODO: optimize this
    dict_items = [ val for val in line_to_attrib_dict.items()]
    #print(dict_items)
    for k, v in dict_items:
        if v[1] == 'part_of_speech_info':
            for i in range(1,10):
                line_to_attrib_dict[f'{k[0:len(k)-4]} ({i}) ==='] = (
                    parse.Attr(v[0], v[1], v[2]))

    h2_target_str: str = r'^== čeština ==$'
    h2_str: str = r'^== .* ==$'
    #h3_german_str: str = r'^=== .* ===$'
    def in_target_lang(line: str) -> bool:
        return bool(re.search(h2_target_str, line)
                   or line == '== poznámky =='
                   or line == '== externí odkazy =='
                   )
    def out_target_lang(line: str) -> bool:
        return bool(re.search(h2_str, line))

    def start_new_entry(line: str) -> bool:
        val = line_to_attrib_dict.get(line, (0, '', ''))
        return val[1] == 'part_of_speech_info'

    def start_new_attrib(line: str) -> bool:
        return bool(line.startswith('===')
                    or line == '== poznámky =='
                    or line == '== externí odkazy =='
                    or line.startswith('[[Kategorie:')
                    )

    def do_on_each_line(self: CzechWord, attr: Optional[parse.Attr],
                        line: str) -> None:
        # Assign noun part of speech
        if attr is not None:
            if  attr.level == 4 and attr.name == 'part_of_speech_info':
                self.entries[-1].part_of_speech = attr.info
            if attr.info == 'noun' and line.startswith("* ''rod "):
                entry = self.entries[-1]
                if not entry.noun_gender:
                    if line == "* ''rod mužský neživotný''":
                        entry.noun_gender = 'm'
                        entry.noun_gender_subcat = 'm: inanimate'
                    elif line == "* ''rod mužský životný''":
                        entry.noun_gender = 'm'
                        entry.noun_gender_subcat = 'm: animate'
                    elif line == "* ''rod mužský''":
                        entry.noun_gender = 'm'
                        entry.noun_gender_subcat = 'm'
                    elif line == "* ''rod střední''":
                        entry.noun_gender = 'n'
                        entry.noun_gender_subcat = 'n'
                    elif line == "* ''rod ženský''":
                        entry.noun_gender = 'f'
                        entry.noun_gender_subcat = 'f'
                    else:
                        logger.warning('Unknown noun gender: line=%s, word=%s',
                                       line, self.headword)
            # Assign verb aspect
            if attr.info == 'verb':
                entry = self.entries[-1]
                if line == "* ''nedokonavé''":
                    if entry.verb_aspect == 'perfective':
                        logger.warning('Conflicting aspect ignored: word=%s',
                                       self.headword)
                    else:
                        entry.verb_aspect = 'imperfective'
                elif line == "* ''dokonavé''":
                    if entry.verb_aspect == 'imperfective':
                        logger.warning('Conflicting aspect ignored: word=%s',
                                       self.headword)
                    else:
                        entry.verb_aspect = 'perfective'

        # Parse the noun, adjective, or verb template
        if line.startswith('{{Substantivum (cs)|'):
            _parse_noun_template(self, line)
        elif line.startswith('{{Stupňování (cs)|'):
            _parse_adjective_template(self, line)
        elif line.startswith('{{Sloveso (cs)|'):
            _parse_verb_template(self, line)

    def ignore_template(line: str) -> bool:
        if (line.startswith('{{Adjektivum (cs)|') or
           line == '==== homofony ====' or
           line.startswith('[[Kategorie:')):
            return True
        else:
            return False

    def process_other_templates(self: CzechWord, # pylint: disable=unused-argument
                                line: str) -> bool: # pylint: disable=unused-argument
        return False

    parse._parse_multi(self, line_to_attrib_dict=line_to_attrib_dict,
        in_target_lang=in_target_lang,
        start_new_entry=start_new_entry,
        out_target_lang=out_target_lang,
        start_new_attrib=start_new_attrib,
        ignore_template=ignore_template,
        allow_data_after_template=False,
        do_on_each_line=do_on_each_line,
        process_other_templates=process_other_templates)

