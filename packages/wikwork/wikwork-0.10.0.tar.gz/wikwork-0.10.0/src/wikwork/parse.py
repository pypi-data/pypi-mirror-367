#    Utility functions used for parsing multiple language files
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

"""Utility functions used for parsing multiple language files."""

#------------------------------------------------------------------------------
# File:    parse.py
# Author:  Ray Griner
# Date:    2024-03-04
# Changes:
# 20240311RG: (1) Add Attr namedtuple to hold information about the current
#   attribute being processed (since we now need not just the name, but level
#   in the object [ie, is it an attribute at the top-level or inside the entry
#   object]). Change `saved_attr_name` to `saved_attr` in _parse_multi.
#   (2) Attributes derived from potentially multiple lines in the wikitext
#   file are now stored as lists of strings. The code joining the strings on
#   '; ' before assignment is removed.
#   (3) Pass attr as parameter to do_on_each_line function.
#   (4) Change functionality of determining whether a line is in the target
#   language. Previously, status was deemed 'in' the first time
#   in_target_lang(line) returned True and permanently 'out' the first time
#   out_target_lang(line) returned False. Now, however also need the line to
#   not be present in line_to_attrib_dict. This is because usually
#   out_target_lang will check if the line is a level two header (ie, starts
#   with ('== '), but Czech stores references and external links in such
#   headers, and we want to inclue these as part of the target language.
#   (5) Remove entry_index from various functions, since we always are updating
#   the last entry, we can just use index=-1.
# 20240314RG: Fix bug in _parse_multi, the last call to _put_results_in_attrib
#   should always be done rather than doing if in_target_lang_bool.
#------------------------------------------------------------------------------
__author__ = 'Ray Griner'
#__all__ = ['AudioFile','Headword']

# Standard modules
import re
import logging
import collections
from typing import Optional, Generator, Callable, Dict, Any

WikiTemp = collections.namedtuple('WikiTemp','name params')
Attr = collections.namedtuple('Attr','level name info', defaults=[''])

logger = logging.getLogger(__name__)

def _put_results_in_attrib(self, attr: Optional[Attr],
                           results: list[str]) -> None:
    #value = '; '.join(results)
    value = results

    if attr is not None and attr.name != 'IGNORE' and attr.level == 4:
        if not self.entries: return
        if not hasattr(self.entries[-1], attr.name):
            logger.error('Attribute %s does not exist in entry', attr.name)
            return

        if not getattr(self.entries[-1], attr.name):
            setattr(self.entries[-1], attr.name, value)
        else:
            logger.warning(('Ignoring attribute %s already set'
                           'in entry: Word: %s'), attr.name, self.headword)
    elif (attr is not None and attr.name != 'IGNORE'
            and (attr.level == 3 or attr.level == 2)):
        if not hasattr(self, attr.name):
            logger.error('Attribute %s does not exist', attr.name)
            return
        if not getattr(self, attr.name):
            setattr(self, attr.name, value)
        else:
            logger.warning('Ignoring attribute %s already set: Word %s',
                           attr.name, self.headword)

def parse_one_template(template: str) -> tuple[Optional[WikiTemp], str]:
    """Parse a string formatted (approximately) as a MediaWiki template.

    Parse the template and extract the name and parameter names/numbers
    and values. For simplicity, the parser will not parse more complicated
    templates, even if they have valid Mediawiki syntax. For example,
    if a parameter value contains a template, the contained template is
    not parsed or transcluded by the function.
    Function assumes:
        1. The string is a correctly formed template ('{{...}}')
        2. Template name contains alphanumeric characters or '_','-','(',
           ')', ' ', '/'
        3. No unmatched braces or brackets in parameter names or values
        4. Any '=' or '|' inside braces or brackets in parameter names or
           values are not treated as parameter delimiters or name=value
           delimiters in the template being parsed.
        6. Nested templates will not be transcluded or parsed.
        7. Template cannot contain '<nowiki>'.

    Parameters
    ----------
    template : str
        Template to parse

    Returns
    -------
    2-tuple as (str, `WikiTemp`), where the first element is an error
    message if parsing wasn't successful and the second is a `WikiTemp`
    object (if successful) or None if not. The `WikiTemp` object is
    a named tuple with elements `name` and `params`, where `params`
    is a dictionary of the parameter name or number (as str) mapped
    to the parameter value.
    """
    if not template.startswith('{{') or not template.endswith('}}'):
        return (None, "template should look like '{{...}}'")
    if template.find('<nowiki>')>-1:
        return (None, 'Cannot parse template with <nowiki>')
    #if template.find('"') > -1:
    #    return (None, 'Cannot parse template with double quotes')

    name_status = 0  # 0=not started, 1=in middle, 2=done
    name_list: list[str] = []
    space_list: list[str] = []
    name = ''
    param_brace_ctr = 0
    param_bracket_ctr = 0
    # list of characters in parameter name or value, not including leading or
    #  trailing whitespace
    param_list: list[str] = []
    # list of whitespace before first non-whitespace character in parameter
    # name/value
    pre_param_space_list: list[str] = []
    # list of whitespace after last non-whitespace character in parameter
    # name/value. Unlike for template name, we need to preserve both the
    # leading and trailing whitespace for unnamed paramaters, so need two
    # lists.
    post_param_space_list: list[str] = []
    # 0 is prior to first non-whitespace character for parameter name/value
    param_status: int = 0
    # 'part1' = before equal sign, 'part2' is after equal sign
    param_part: str = 'name'
    # dictionary of results
    param_dict: dict[str, str] = {}
    param_number = 1
    param_name: str = ''
    for char in template[2:len(template)-2]:
        # First parse the template name
        if name_status < 2:
            if char.isspace() and name_status == 0:
                pass
            elif char.isspace() and name_status == 1:
                space_list.append(char)
            elif char=='|' and name_status == 0:
                return (None, 'empty template')
            elif char == '|' and name_status == 1:
                name_status = 2
                name = ''.join(name_list)
                param_part = 'part1'
            elif char.isalnum() or char in [' ','-','_','(',')','.', '/']:
                name_status = 1
                for item in space_list:
                    name_list.append(item)
                space_list = []
                name_list.append(char)
            else:
                return (None, 'character not expected in name')
        else:  # Now parsing template parameters
            if char.isspace():
                if param_status == 0:
                    pre_param_space_list.append(char)
                else:
                    post_param_space_list.append(char)
            else:
                param_status = 1
                if char == '{':
                    param_brace_ctr += 1
                    param_list.append(char)
                elif char == '[':
                    param_bracket_ctr += 1
                    param_list.append(char)
                elif char == '}':
                    param_brace_ctr -= 1
                    if param_brace_ctr < 0:
                        return(None, 'unmatched extra right brace')
                    param_list.append(char)
                elif char == ']':
                    param_bracket_ctr -= 1
                    if param_bracket_ctr < 0:
                        return(None, 'unmatched extra right bracket')
                    param_list.append(char)
                elif (char == '|' and param_brace_ctr == 0
                        and param_bracket_ctr == 0):
                    # we have found value. Save parameter name and value to
                    # param_dict and reset the variables used to hold the
                    # spaces and parameter name/value for next parameter
                    if param_part == 'part1':
                        # Values of unnamed parameters preserve leading and
                        # trailing whitespace.
                        dict_val = ''.join(pre_param_space_list +
                            param_list + post_param_space_list)
                        if str(param_number) in param_dict:
                            return (None, f'{param_number=} in template twice')
                        else:
                            param_dict[str(param_number)] = dict_val
                        param_number += 1
                        param_list = []
                        pre_param_space_list = []
                        post_param_space_list = []
                        param_status = 0
                    elif param_part == 'part2':
                        # Values of named parameters don't preserve leading
                        # or trailing whitespace.
                        dict_val = ''.join(param_list)
                        if param_name in param_dict:
                            return (None, f'{param_name=} in template twice')
                        else:
                            param_dict[param_name] = dict_val
                        param_list = []
                        pre_param_space_list = []
                        post_param_space_list = []
                        param_status = 0
                    param_part = 'part1'
                elif (char == '=' and param_part == 'part1'
                        and param_brace_ctr == 0 and param_bracket_ctr == 0):
                    # found parameter name. leading/trailing whitespace are
                    # not part of the name
                    param_part = 'part2'
                    param_name = ''.join(param_list)
                    if re.search(r'=|\|', param_name):
                        return (None, f'{param_name=} contains = or |')
                    param_list = []
                    pre_param_space_list = []
                    post_param_space_list = []
                    param_status = 0
                else:
                    for item in post_param_space_list:
                        param_list.append(item)
                    post_param_space_list = []
                    param_list.append(char)

    name = ''.join(name_list)
    if param_brace_ctr > 0 or param_bracket_ctr > 0:
        return(None, 'unmatched brace or bracket')

    # Same logic as above when finding a '|', but no need to reinitialize the
    #   status variables or lists
    if param_part == 'part1':
        dict_val = ''.join((pre_param_space_list + param_list
                            + post_param_space_list))
        if str(param_number) in param_dict:
            return (None, f'{param_number=} in template twice')
        else:
            param_dict[str(param_number)] = dict_val
    elif param_part == 'part2':
        dict_val = ''.join(param_list)
        if param_name in param_dict:
            return (None, f'{param_name=} in template twice')
        else:
            param_dict[param_name] = dict_val
    return (WikiTemp(name=name, params=param_dict), '')

def _oneline_templates(word: str, text: str) -> Generator[str, None, None]:
    lines = text.splitlines()
    cumlines = []
    cum_open = 0
    cum_close = 0
    for current in lines:
        cum_open += current.count('{')
        cum_close += current.count('}')
        if cum_open == cum_close:
            cumlines.append(current)
            yield ''.join(cumlines)
            cumlines = []
        else:
            cumlines.append(current)
            logger.debug('Word %s: multi-line template', word)
    yield ''.join(cumlines)

def _parse_multi(self, line_to_attrib_dict: Dict[str, Attr],
        in_target_lang: Callable[[str], bool],
        out_target_lang: Callable[[str], bool],
        start_new_entry: Callable[[str], bool],
        start_new_attrib: Callable[[str], bool],
        do_on_each_line: Callable[[Any, Optional[Attr], str], None],
        ignore_template: Callable[[str], bool],
        allow_data_after_template: bool,
        process_other_templates: Callable[[Any, str], bool]) -> None:
    """Parse the wikitext and put results in the entries attribute.

    Parameters
    ----------
    line_to_attrib_dict: dict[str, Attr]
        Dictionary that maps input lines to attributes. Many attributes
        contain all the lines in a section of the wikitext file, where
        a section definition depends on the language but is typically
        identified by wikitext headers or templates that span the whole
        line.
    in_target_lang : Callable[[str], bool]
        Function that returns True if the input line indicates the
        following section is in the target language.
    out_target_lang : Callable[[str], bool]
        Function that returns True if the output line indicates the
        following section is not in the target language and otherwise,
        False. (This function is not called if in_target_lang returns
        True.)
    start_new_entry : Callable[[str], bool]
        Function that returns True if the line indicates the start of
        a new dictionary entry. Otherwise, False.
    start_new_attrib : Callable[[str], bool]
        Function that returns True if the line indicates the start of
        a new attribute (either at the word level or entry level) and
        otherwise, False.
    do_on_each_line : Callable[[Any, Optional[Attr], str], None]
        Function that is called on each line
    ignore_template : Callable[[str], bool]
        Among lines where start_new_attrib is True and not in
        line_to_attrib_dict, return True if the template should be
        ignored.
    process_other_templates: Callable[[Any, str], bool]
        Among lines where start_new_attrib is True and not in
        line_to_attrib_dict and ignore_template is False, return True
        if the line was processed.
    allow_data_after_template : bool
        If True, for lines still not yet processed
        (start_new_attrib = True, not in line_to_attrib_dict,
        ignore_template = False, process_other_templates = False), check
        if the start of the line matches a key in line_to_attrib_dict.
        If it does, treat the remainder of the line as the first line
        of the results.

    Returns
    -------
    None
    """

    lines = _oneline_templates(self.headword, self.wikitext)

    in_target_lang_bool: bool = False
    target_lang_counter: int = 0
    saved_attr: Optional[Attr] = None
    results: list[str] = []
    for line in lines:
        if in_target_lang(line):
            if line_to_attrib_dict.get(line, None) is None:
                target_lang_counter += 1
            if target_lang_counter>1:
                logger.info(('Target language found twice, will be ignored:'
                             'Word %s'), self.headword)
                in_target_lang_bool = False
            else:
                in_target_lang_bool = True
        elif (out_target_lang(line)
                and line_to_attrib_dict.get(line, None) is None):
            in_target_lang_bool = False

        if start_new_entry(line):
            _put_results_in_attrib(self, saved_attr, results)
            results = []
            self.add_new_entry()
            #self.entries.append(entry_constructor())
            saved_attr = None

        if in_target_lang_bool:
            if start_new_attrib(line):
                # New template, so write contents of results to attribute
                _put_results_in_attrib(self, saved_attr, results)
                # Done writing, so process current line
                results = []
                do_on_each_line(self, saved_attr, line)
                val = line_to_attrib_dict.get(line, None)
                if val is not None:
                    saved_attr = val
                else:
                    saved_attr = None
                    if ignore_template(line):
                        pass
                    elif process_other_templates(self, line):
                        pass
                    elif allow_data_after_template:
                        for k, v in line_to_attrib_dict.items():
                            if line.startswith(k):
                                rest = str.strip(line[len(k):])
                                if rest:
                                    results.append(rest)
                                saved_attr = v
                                break
                        if saved_attr is None:
                            logger.info('Word %s: Template not handled: %s',
                                        self.headword, line)
                    else:
                        logger.info('Word %s: Template not handled: %s',
                                    self.headword, line)
            else:
                do_on_each_line(self, saved_attr, line)
                if line:
                    results.append(line)
    # [20240314RG]
    #if in_target_lang_bool:
    #    _put_results_in_attrib(self, saved_attr, results)
    _put_results_in_attrib(self, saved_attr, results)

