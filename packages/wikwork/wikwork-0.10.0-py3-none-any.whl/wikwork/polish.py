#    PolishWord subclass and related functions.
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

""" PolishWord subclass and related functions. """

#------------------------------------------------------------------------------
# File:    polish.py
# Author:  Ray Griner
# Date:    2024-03-03
# Changes:
# 20240311RG:
#   1. make attributes that are not derived from a single input line a list of
#   strings instead of a string joined on '; '.
#   2. Change value stored in line_to_attrib_dict a parse.Attr object instead
#   of a string.
#   3. Add attr as parameter to do_on_each_line function.
#   4. Remove entry_index from various functions, since we always are updating
#   the last entry, we can just use index=-1.
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
#HttpHeaders = Dict[str, str]
#MediaList = Any
#AudioReqs = Dict[str, Tuple[int, str]]
#SortKey = Callable[['AudioFile'], Any]

#------------------------------------------------------------------------------
# Class definition: GermanWord
#------------------------------------------------------------------------------
class PolishEntry():
    """Polish Wiktionary™ entry with selected attributes parsed from wikitext.

    Selected elements of the dictionary entries (for the same language as
    the Wiktionary) parsed from the wikitext. Unlike German, the Polish
    Wiktionary doesn't use third-level headings to delimit separate
    entries within a page and so the entries attribute list will only have
    one element. The wikitext appears to be well-organized for using
    a simple parser. For the most part, templates that indicate the start
    of a new field occur alone on a single line, although the conjugation/
    declension templates are usually associated a numbered definition and
    follow that on the line. Also, unlike German, these templates often
    span multiple lines (but a generator has been written to combine the
    lines so that the template ends up on a single line).

    The attributes attracted from the noun, verb, and adjective templates
    start with 'adj_', 'verb_', and 'noun_', respectively, and are
    a single string and likely do not contain wikitext. Other attributes
    are lists of lines obtained from the input file. These attributes still
    do contain wikitext, although it may be replaced in the future.

    Attributes
    ----------
    pronunciations : list[str]
        Lines after '{{wymova}}' template.
    definitions : list[str]
        Lines after '{{znaczenia}}' template.
    etymology : list[str]
        Lines after '{{etymologia}}' template.
    synonyms : list[str]
        Lines after '{{synonimy}}' template.
    antonyms : list[str]
        Lines after '{{antonimy}}' template.
    hyponyms : list[str]
        Hyponyms are more specific words. For example, the English
        word 'season' has the hyponym 'winter'. Lines after
        '{{hiponimy}}' template.
    hypernyms : list[str]
        Hypernyms are more general words. For example, the English
        word 'winter' has the hypernym 'season'.  Lines after
        '{{hiperonimy}} template.
    examples : list[str]
        Lines after '{{przykłady}}' template.
    expressions : list[str]
        Lines after '{{frazeologia}}' template.
    word_combos : list[str]
        Characteristic word combinations. Lines after
        '{{kolokacje}}' template.
    word_formations : list[str]
        Lines after '{{pokrewne}}' template.
    references : list[str]
        Lines after '{{źródła}}' template.
    syntax : list[str]
        Lines after '{{składnia}}' template.
    meronyms : list[str]
        Lines after '{{meronimy}}' template.
    holonyms : list[str]
        Lines after '{{holonimy}}' template.
    cautions : list[str]
        Lines after '{{uwagi}}' template.

    adj_def_id : str
        Definition id numbers corresponding to the `adj_comp` parameter.
        Definition id numbers in this variable and others include the ' : '
        wikitext indicating indication, although this may change in the
        future.
    adj_comp : str
        Comparative form of adjective. First parameter of
        '{{odmiana-przymiotnik-polski}} template. The following remappings
        are done :
            'brak' -> '[no comp.]' (ie, the adjective has no comparative
                                   form)
            'bardziej' -> 'bardziej ~'
            '' (absent or empty parameter) -> '[not listed]'.
    adj_def_id2 : str
        Definition id numbers corresponding to the `adj_comp2` parameter.
        See `adj_def_id` for additional notes.
    adj_comp2 : str
        Alternate comparative form of adjective. Parameter of second
        appearance of '{{odmiana-przymiotnik-polski}}' template. Same
        remappings as for `adj_comp` attribute.

    verb_def_id : str
        Definition id numbers corresponding to the `verb_...` parameters.
        The source template for attributes related to verbs is the
        'odmiana-czasownik-polski' template (for brevity, denoted as
        'the verb template' in the remainder of this section).
        See `adj_def_id` for additional notes.
    verb_ref_etal : str
        Information on the line between the verb_def_id and the verb
        template.
    verb_aspect : str
        Verb aspect. From 'dokonany' parameter of the verb template.
        Convert 'nie' to 'imperfective' and 'tak' to 'perfective'.
    verb_reflex : str
        Verb reflexive pronoun. From 'się' parameter of the verb template.
        The value will usually be 'się' or ''. Sometimes verbs have both a
        non-reflexive and reflexive form. However, because the 'verb_'
        attributes are only populated based one template, it is not
        currently possible to distinguish verbs that are never reflexive or
        always reflective vs those with both forms. This handling may be
        altered in the future.
    verb_inf : str
        Infinitive. From 'robić' or 'zrobić' paramaters of the verb
        template.
    verb_conj_group : str
        Conjugation group. From 'koniugacja' parameter of the verb
        template. See :
    https ://pl.wiktionary.org/wiki/Aneks :J%C4%99zyk_polski_-_koniugacja_[nn],
        where [nn] is the group, for details.
    verb_conj_1s : str
        Conjugated first person singular. From 'robię' or 'zrobię'
        parameters of the verb template.
    verb_conj_3s : str
        Conjugated third person singular. From 'robi' or 'zrobi'
        parameters of the verb template.
    verb_conj_3p : str
        Conjugated third person singular. From 'robią' or 'zrobią'
        parameters of the verb template.
    verb_past_m1s : str
        Masculine first person singular past. From 'robiłem' or 'zrobiłem'
        parameters of the verb template.
    verb_past_m3s : str
        Masculine third person singular past. From 'robił' or 'zrobił'
        parameters of the verb template.
    verb_past_f3s : str
        Feminine third person singular past. From 'robiła' or 'zrobiła'
        parameters of the verb template.
    verb_past_m3p : str
        Masculine third person plural past. From 'robiłi' or 'zrobiłi'
        parameters of the verb template.
    verb_past_imper : str
        Impersonal past. From 'robiono' or 'zrobiono' parameters of the
        verb template.
    verb_imper_s : str
        Imperative (second person) singular. From 'rób' or 'zrób'
        parameters of the verb template.
    verb_adv_imp : str
        Verbal adverb (imperfective verbs). From 'robiąc' parameter of the
        verb template.
    verb_adv_pf : str
        Verbal adverb (perfective verbs). From 'zrobiwszy' parameter of the
        verb template.
    verb_pass_adj_part_ms : str
        Passive adjectival participle masculine singular. From 'robiony' or
        'zrobiony' parameters of the verb template.
    verb_pass_adj_part_mp : str
        Passive adjectival participle masculine plural. From 'robieni' or
        'zrobieni' parameters of the verb template.
    verb_gerund : str
        Verbal noun / gerund. From 'robienie' or 'zrobienie' parameters of
        the verb template.
    verb_irr_temp : bool, optional
        True if the template includes parameters other than those listed
        above.

    noun_def_id : str
        Definition id numbers corresponding to the `noun_...` parameters
        (except `noun_gender`, which is not extracted from a template).
        See `adj_def_id` for additional notes.
    noun_ref_etal : str
        Information on the line between the noun_def_id and the noun template.
    noun_gender_subcat : str
        Detailed noun gender. Extracted from lines matching the patterns
        below. These tend to occur after the '{{znaczenia}}' template and
        in the future the logic might be updated to restrict to strings
        only in this section.
        "''rzeczownik, rodzaj żeński''", "''rzeczownik, rodzaj nijaki''",
        The following strings are processed and mapped to the following
        output :
            "''rzeczownik, rodzaj męskoosobowy''" -> 'm : person'
            "''rzeczownik, rodzaj męskoosobowy lub męskozwierzęcy''" ->
                'm : person or animal'
            "''rzeczownik, rodzaj męskorzeczowy''" -> 'm : thing'
            "''rzeczownik, rodzaj męskorzeczowy lub męskozwierzęcy''" ->
                'm : animal or thing'
            "''rzeczownik, rodzaj nijaki''" -> 'n'
            "''rzeczownik, rodzaj żeński''" -> 'f'
        A message is printed to the log for other strings that start with
            "''rzeczownik, rodzaj" that don't match the above.
    noun_gender : str
        The first character of noun_gender_subcat (so 'm', 'f', or 'n').
    noun_nom_s : str
        Noun nominative singular. 'Mianownik 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_nom_p : str
        Noun nominative plural. 'Mianownik 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_acc_s : str
        Noun accusative singular. 'Biernik 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_acc_p : str
        Noun accusative plural. 'Biernik 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_voc_s : str
        Noun vocative singular. 'Wołacz 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_voc_p : str
        Noun vocative plural. 'Wołacz 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_loc_s : str
        Noun locative singular. 'Miejscownik 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_loc_p : str
        Noun locative plural. 'Miejscownik 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_dat_s : str
        Noun dative singular. 'Celownik 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_dat_p : str
        Noun dative plural. 'Celownik 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_gen_s : str
        Noun genitive singular. 'Dopełniacz 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_gen_p : str
        Noun genitive plural. 'Dopełniacz 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_inst_s : str
        Noun instrumental singular. 'Narzędnik 1p' parameter of
        'odmiana-rzeczownik-polski' template.
    noun_inst_p : str
        Noun instrumental plural. 'Narzędnik 1m' parameter of
        'odmiana-rzeczownik-polski' template.
    """
    def __init__(self) -> None:
        """ Initialize entry. Set contents to empty lists or strings. """
        self.pronunciations: list[str] = []
        self.definitions: list[str] = []
        self.etymology: list[str] = []
        self.synonyms: list[str] = []
        self.antonyms: list[str] = []
        self.hyponyms: list[str] = []
        self.hypernyms: list[str] = []
        self.examples: list[str] = []
        self.expressions: list[str] = []
        self.word_combos: list[str] = []
        self.word_formations: list[str] = []
        self.references: list[str] = []
        self.syntax: list[str] = []
        self.meronyms: list[str] = []
        self.holonyms: list[str] = []
        self.cautions: list[str] = []

        self.adj_def_id: str = ''
        self.adj_comp: str = ''
        self.adj_def_id2: str = ''
        self.adj_comp2: str = ''

        self.verb_def_id: str = ''
        self.verb_ref_etal: str = ''
        self.verb_aspect = ''
        self.verb_inf: str = ''
        self.verb_conj_group: str = ''
        self.verb_conj_1s: str = ''
        self.verb_conj_3s: str = ''
        self.verb_conj_3p: str = ''
        self.verb_past_m1s: str = ''
        self.verb_past_m3s: str = ''
        self.verb_past_f3s: str = ''
        self.verb_past_m3p: str = ''
        self.verb_past_imper: str = ''
        self.verb_imper_s: str = ''
        self.verb_adv_imp: str = ''
        self.verb_adv_pf: str = ''
        self.verb_pass_adj_part_ms: str = ''
        self.verb_pass_adj_part_mp: str = ''
        self.verb_gerund: str = ''
        self.verb_irr_temp: Optional[bool] = None

        self.noun_def_id: str = ''
        self.noun_ref_etal: str = ''
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
        return 'PolishEntry(' + ', '.join(output_list) + ')'

class PolishWord(page_media.Headword):
    """Headword information and associated audio files for German headword.

    Attributes
    ----------
    entries : list[PolishEntry]
        Information from the entries on the word page that are from the
        same language as `lang_code`. A new entry is defined as the start
        of a new second or third level heading (ie, lines that start with
        '== ' or '=== ').
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
        self.entries: list[PolishEntry] = []

    def __repr__(self) -> str:
        return ('PolishWord('
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
        self.entries.append(PolishEntry())
        return len(self.entries) - 1

#------------------
# Private functions
#------------------
def _parse_verb_template(self: PolishWord, line: str) -> bool:
    """Parse line containing verb template and update entry.
    """
    current_entry = self.entries[-1]
    res = re.search((r'^(: \([0123456789\.\,-]*\))(.*)'
                     r'(\{\{odmiana-czasownik-polski\|.*\}\})$'), line)
    if res:
        verb_def_id = str.strip(res.group(1))
        verb_ref_etal = str.strip(res.group(2))
        template = str.strip(res.group(3))
        if verb_def_id and current_entry.verb_def_id:
            logger.info('Word %s: Template not handled: already found %s: %s',
                self.headword, current_entry.verb_aspect, line)
            return True

        wiki_temp, err_msg = parse.parse_one_template(template)
        if wiki_temp is None:
            logger.warning('Word: %s: Template parser: %s',
                            self.headword, err_msg)
            return False

        temp_dict = wiki_temp.params
        verb_aspect = temp_dict.get('dokonany', '')
        if verb_aspect == 'tak':
            aspect = 'perfective'
        elif verb_aspect == 'nie':
            aspect = 'imperfective'
        else:
            logger.info(('Word %s: Template not handled: aspect %s (dokonany '
                         "parameter) must be 'tak' or 'nie': %s"),
                self.headword, current_entry.verb_aspect, line)
            return True

        current_entry.verb_def_id = verb_def_id
        current_entry.verb_ref_etal = verb_ref_etal
        current_entry.verb_conj_group = temp_dict.get('koniugacja', '')
        if aspect == 'imperfective' and not current_entry.verb_aspect:
            current_entry.verb_aspect = aspect
            current_entry.verb_inf = temp_dict.get('robić', '')
            current_entry.verb_conj_1s = temp_dict.get('robię', '')
            current_entry.verb_conj_3s = temp_dict.get('robi', '')
            current_entry.verb_conj_3p = temp_dict.get('robią', '')
            current_entry.verb_past_m1s = temp_dict.get('robiłem', '')
            current_entry.verb_past_m3s = temp_dict.get('robił', '')
            current_entry.verb_past_f3s = temp_dict.get('robiła', '')
            current_entry.verb_past_m3p = temp_dict.get('robili', '')
            current_entry.verb_past_imper = temp_dict.get('robiono', '')
            current_entry.verb_imper_s = temp_dict.get('rób', '')
            current_entry.verb_adv_imp = temp_dict.get('robiąc', '')
            current_entry.verb_pass_adj_part_ms = temp_dict.get('robiony', '')
            current_entry.verb_pass_adj_part_mp = temp_dict.get('robieni', '')
            current_entry.verb_gerund = temp_dict.get('robienie', '')
            regular_keys = ['dokonany','się','koniugacja','robić','robię',
            'robi','robią','robiłem','robił','robiła','robili','robiono','rób',
            'robiąc','robiony','robieni','robienie']
            set_diff = set(temp_dict.keys()) - set(regular_keys)
            if len(set_diff) > 0:
                current_entry.verb_irr_temp = True
                logger.info('Word %s: verb irreg template, has keys: %s',
                             self.headword, str(set_diff))
            else:
                current_entry.verb_irr_temp = False

        if aspect == 'perfective' and not current_entry.verb_aspect:
            current_entry.verb_inf = temp_dict.get('zrobić', '')
            current_entry.verb_conj_1s = temp_dict.get('zrobię', '')
            current_entry.verb_conj_3s = temp_dict.get('zrobi', '')
            current_entry.verb_conj_3p = temp_dict.get('zrobią', '')
            current_entry.verb_past_m1s = temp_dict.get('zrobiłem', '')
            current_entry.verb_past_m3s = temp_dict.get('zrobił', '')
            current_entry.verb_past_f3s = temp_dict.get('zrobiła', '')
            current_entry.verb_past_m3p = temp_dict.get('zrobili', '')
            current_entry.verb_past_imper = temp_dict.get('zrobiono', '')
            current_entry.verb_imper_s = temp_dict.get('zrób', '')
            current_entry.verb_adv_pf = temp_dict.get('zrobiwszy', '')
            current_entry.verb_pass_adj_part_ms = temp_dict.get('zrobiony', '')
            current_entry.verb_pass_adj_part_mp = temp_dict.get('zrobieni', '')
            current_entry.verb_gerund = temp_dict.get('zrobienie', '')
            regular_keys = ['dokonany','się','koniugacja','zrobić','zrobię',
            'zrobi','zrobią','zrobiłem','zrobił','zrobiła','zrobili',
            'zrobiono','zrób','zrobiwszy','zrobiony','zrobieni','zrobienie']
            set_diff = set(temp_dict.keys()) - set(regular_keys)
            if len(set_diff) > 0:
                current_entry.verb_irr_temp = True
                logger.info('Word %s: verb irreg template, has keys: %s',
                             self.headword, str(set_diff))
            else:
                current_entry.verb_irr_temp = False
        return True
    else:
        return False

def _parse_noun_template(self: PolishWord, line: str) -> bool:
    """Parse line containing noun template and update entry.
    """
    current_entry = self.entries[-1]
    res = re.search((r'^(: \([0123456789\.\,-]*\))(.*)'
                     r'(\{\{odmiana-rzeczownik-polski\|.*\}\})$'), line)
    if res:
        noun_def_id = res.group(1)
        noun_ref_etal = res.group(2)
        template = res.group(3)
        if noun_def_id and current_entry.noun_def_id:
            logger.info('Word %s: Template not handled: already found %s: %s',
                self.headword, current_entry.verb_aspect, line)
            return True
        wiki_temp, err_msg = parse.parse_one_template(template)
        if wiki_temp is None:
            logger.warning('Word: %s: Template parser: %s',
                            self.headword, err_msg)
            return False

        temp_dict = wiki_temp.params

        current_entry.noun_def_id = noun_def_id
        current_entry.noun_ref_etal = noun_ref_etal
        current_entry.noun_nom_s = temp_dict.get('Mianownik lp', '')
        current_entry.noun_nom_s = temp_dict.get('Mianownik lp', '')
        current_entry.noun_nom_p = temp_dict.get('Mianownik lm', '')
        current_entry.noun_acc_s = temp_dict.get('Biernik lp', '')
        current_entry.noun_acc_p = temp_dict.get('Biernik lm', '')
        current_entry.noun_voc_s = temp_dict.get('Wołacz lp', '')
        current_entry.noun_voc_p = temp_dict.get('Wołacz lm', '')
        current_entry.noun_loc_s = temp_dict.get('Miejscownik lp', '')
        current_entry.noun_loc_p = temp_dict.get('Miejscownik lm', '')
        current_entry.noun_dat_s = temp_dict.get('Celownik lp', '')
        current_entry.noun_dat_p = temp_dict.get('Celownik lm', '')
        current_entry.noun_gen_s = temp_dict.get('Dopełniacz lp', '')
        current_entry.noun_gen_p = temp_dict.get('Dopełniacz lm', '')
        current_entry.noun_inst_s = temp_dict.get('Narzędnik lp', '')
        current_entry.noun_inst_p = temp_dict.get('Narzędnik lm', '')
        return True
    else:
        return False

def _remap_adjective_value(input_str: str) -> str:
    if input_str == 'brak':
        return '[no comp.]'
    elif input_str == '':
        return '[not listed]'
    elif input_str == 'bardziej':
        return 'bardziej ~'
    else:
        return input_str

def _parse_adjective_template(self: PolishWord, line: str) -> bool:
    """Parse line containing adjective template and update entry.
    """
    res = re.search((r'^(: \([0123456789\.\,-]*\))\s*'
                     r'(\{\{odmiana-przymiotnik-polski(\|.*|)\}\})$'), line)
    if res:
        adj_def_id = str.strip(res.group(1))
        template = str.strip(res.group(2))
        wiki_temp, err_msg = parse.parse_one_template(template)
        if wiki_temp is None:
            logger.warning('Word: %s: Template parser: %s',
                            self.headword, err_msg)
            return False
        temp_dict = wiki_temp.params
        current_entry = self.entries[-1]

        # If two unnamed parameters, then the first might not be the title
        # page, so check.
        if '2' in temp_dict:
            if temp_dict.get('1') != self.headword:
                logger.info('Word %s: Skipping 2-parameter adj template: %s',
                    self.headword, line)
                return False
            else:
                adj_comp = _remap_adjective_value(temp_dict.get('2',''))
        else:
            adj_comp = _remap_adjective_value(temp_dict.get('1',''))

        if not self.entries[-1].adj_comp and adj_comp:
            current_entry.adj_def_id = adj_def_id
            current_entry.adj_comp = adj_comp
            return True
        elif not self.entries[-1].adj_comp2 and adj_comp:
            current_entry.adj_def_id2 = adj_def_id
            current_entry.adj_comp2 = adj_comp
            return True
        else:
            logger.info('Word %s: Template not handled: already found: %s',
                self.headword, line)
            return True
    else:
        return False

def _parse_wikitext(self: PolishWord) -> None:
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
#        '{{XXXX}}' : 'word_separations',
        '{{wymowa}}' : parse.Attr(4, 'pronunciations'),
        '{{znaczenia}}' : parse.Attr(4, 'definitions'),
        '{{etymologia}}' : parse.Attr(4, 'etymology'),
        '{{synonimy}}' : parse.Attr(4, 'synonyms'),
        '{{antonimy}}' : parse.Attr(4, 'antonyms'),
        '{{hiponimy}}' : parse.Attr(4, 'hyponyms'),
        '{{hiperonimy}}' : parse.Attr(4, 'hypernyms'),
        '{{przykłady}}' : parse.Attr(4, 'examples'),
        '{{frazeologia}}' : parse.Attr(4, 'expressions'),
        '{{kolokacje}}' : parse.Attr(4, 'word_combos'),
        '{{pokrewne}}' : parse.Attr(4, 'word_formations'),
        '{{źródła}}' : parse.Attr(4, 'references'),
        '{{składnia}}' : parse.Attr(4, 'syntax'),
        '{{meronimy}}' : parse.Attr(4, 'meronyms'),
        '{{holonimy}}' : parse.Attr(4, 'holonyms'),
        '{{uwagi}}' : parse.Attr(4, 'cautions'),
    }
    h2_target_str: str = r'^== .* \(\{\{język polski\}\}\) ==$'
    h2_str: str = r'^== .* ==$'
    #h3_german_str: str = r'^=== .* ===$'
    h4_str: str = r'^==== .* ====$'
    def in_target_lang(line: str) -> bool:
        return bool(re.search(h2_target_str, line))
    def out_target_lang(line: str) -> bool:
        return bool(re.search(h2_str, line) or bool(re.search(h4_str, line)))
    def start_new_attrib(line: str) -> bool:
        return bool(line.startswith('{{') or re.search(r'\{\{odmiana-', line))
    def do_on_each_line(self: PolishWord,
                        attr: Optional[parse.Attr], # pylint: disable=unused-argument
                        line: str) -> None:
        entry = self.entries[-1]
        if not entry.noun_gender_subcat:
            res = re.search(r"^''rzeczownik, rodzaj.*''$", line)
            if res:
                if res.group(0) == "''rzeczownik, rodzaj męskoosobowy''":
                    entry.noun_gender_subcat = 'm: person'
                elif res.group(0) == ("''rzeczownik, rodzaj męskoosobowy "
                                      "lub męskozwierzęcy''"):
                    entry.noun_gender_subcat = 'm: person or animal'
                elif res.group(0) == "''rzeczownik, rodzaj męskorzeczowy''":
                    entry.noun_gender_subcat = 'm: thing'
                elif res.group(0) == ("''rzeczownik, rodzaj męskorzeczowy lub "
                                      "męskozwierzęcy''"):
                    entry.noun_gender_subcat = 'm: animal or thing'
                elif res.group(0) == "''rzeczownik, rodzaj nijaki''":
                    entry.noun_gender_subcat = 'n'
                elif res.group(0) == "''rzeczownik, rodzaj żeński''":
                    entry.noun_gender_subcat = 'f'
                else:
                    logger.info('Word %s: gender mapping not defined: %s',
                                self.headword, res.group(0))
                if entry.noun_gender_subcat:
                    entry.noun_gender = entry.noun_gender_subcat[0]
                else:
                    entry.noun_gender = ''

    def ignore_template(line: str) -> bool:
        return bool(re.search((r'^\{\{odmiana\}\}$|'
                              r'^\{\{tłumaczenia\}\}$'), line))

    def process_other_templates(self: PolishWord, line: str) -> bool:
        if line.find('odmiana-przymiotnik-polski') != -1:
            return _parse_adjective_template(self, line)
        elif line.find('odmiana-rzeczownik-polski') != -1:
            return _parse_noun_template(self, line)
        elif line.find('odmiana-czasownik-polski') != -1:
            return _parse_verb_template(self, line)
        else:
            return False

    parse._parse_multi(self, line_to_attrib_dict=line_to_attrib_dict,
        in_target_lang=in_target_lang,
        start_new_entry=in_target_lang,
        out_target_lang=out_target_lang,
        start_new_attrib=start_new_attrib,
        ignore_template=ignore_template,
        allow_data_after_template=True,
        do_on_each_line=do_on_each_line,
        process_other_templates=process_other_templates)

