#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Input/output utilities and file management.

Provides functions for file operations, path handling, string transliteration
for filenames, and other I/O related utilities.
"""

import re
from pathlib import Path
from typing import Union
from unidecode import unidecode


_folders_were_created: bool = False  # Keep track of whether folders have been created.
_transliterate_special: dict[
    str, str
] = {  # Character transliteration rules when converting string to filename.
    '&': 'and',
    '@': 'at',
    r'{+': r'{',
    r'}+': r'}',
    r'\\langle': '<',
    r'\\rangle': '>',
    r'\\mathrm': '',
    r'\|([\w\-_\\]*)\|': r'Abs{\1}',
    r'\\ket{([\w\-_\\]*)}': r'\1',
    r'_{([\w\-_\\]*)}': r'_\1',
    r'\^{([\w\-_\\]*)}': r'\^\1',
    r'\\omega': 'w',
}


class PathDic:
    """
    Class for nested structure of dictionaries and lists representing folder structure.

    Script folder names can differ from disk folder names.
    """

    path: str  # Disk path of folder.
    _dic: dict  # Dictionary of subfolders.
    _key_tuples: dict  # Dictionary of keys to <_dic>.

    def __init__(
        self, dic_or_lst: Union[dict, list] = None, root_path: str = ''
    ) -> None:
        """
        Initialize with list or dictionary of sub folders and root path.

        Args:
            dic_or_lst: Dictionary or list of subfolder definitions
            root_path: Root path for this folder structure
        """
        if dic_or_lst is None:
            dic_or_lst = {}
        self.path = root_path
        self._dic = {}
        self._key_tuples = {}
        for name in dic_or_lst if dic_or_lst else {}:
            if isinstance(name, tuple) and len(name) >= 2:
                name_tuple = name
            else:
                name_tuple = (name, name)
            if isinstance(dic_or_lst, dict):
                self._dic[name_tuple] = dic_or_lst[name]
            elif isinstance(dic_or_lst, list):
                self._dic[name_tuple] = None
            self._key_tuples[name_tuple[0]] = name_tuple

    def __getitem__(self, key: str) -> 'PathDic':
        """
        Subscript as dictionary.

        Args:
            key: Key to access subfolder

        Returns:
            PathDic object for the requested subfolder

        Raises:
            Exception: If the requested folder key does not exist
        """
        if key not in self._key_tuples:
            raise Exception(
                'Attempted to find folder <'
                + str(key)
                + '>, but no such folder exists.'
            )
        key_tuple = self._key_tuples[key]
        path = self.path + '/' + str(key_tuple[1])
        simplified_path = re.sub(r'\/\.$', '', path)
        simplified_path = re.sub(r'\/\.\/', '/', simplified_path)
        return PathDic(self._dic[key_tuple], simplified_path)

    def keys(self) -> dict.keys:
        """
        Get dictionary keys.

        Returns:
            Keys of the subfolder dictionary
        """
        return self._key_tuples.keys()

    def iter_sub_paths(self) -> 'PathDic':
        """
        Iterate over subfolders.

        Yields:
            PathDic objects for each subfolder
        """
        for key in self.keys():
            yield self[key]

    def sub_paths(self) -> list['PathDic']:
        """
        Get list of sub folder paths.

        Returns:
            List of PathDic objects for subfolders
        """
        return list(self.iter_sub_paths())


def to_filename(
    string: str,
    to_lower: bool = True,
    allowed_chars: list[str] = None,
    extra_transliterate_special: dict[str, str] = None,
) -> str:
    """
    Convert any string to valid filename.

    Args:
        string: Input string to convert
        to_lower: Whether to convert to lowercase
        allowed_chars: List of additional characters to allow in filename
        extra_transliterate_special: Additional transliteration rules

    Returns:
        Valid filename string
    """
    if allowed_chars is None:
        allowed_chars = []
    if extra_transliterate_special is None:
        extra_transliterate_special = {}

    # Combine default and supplied transliteration rules, supplied takes precedence.
    transliterate_special = {**extra_transliterate_special, **_transliterate_special}

    # Transliterate special characters to custom text. N^2 passes.
    for _ in transliterate_special:
        for char in transliterate_special:
            string = re.sub(char, transliterate_special[char], string)

    # Transliterate unicode to ascii.
    string = unidecode(string)

    # Remove simple specials characters without substituting underscore.
    string = re.sub(r'(\\|"|!|\?|--|\$)+', '', string)

    # Substitute everything except alphanumerics, dash, underscore, and other allowed_chars for underscore.
    sub_pattern = r'[^\w\d_\-'
    for char in allowed_chars:
        sub_pattern += char
    sub_pattern += r']+'
    string = re.sub(sub_pattern, '_', string)

    # Remove leading and trailing underscores.
    string = re.sub(r'^_+', '', string)
    string = re.sub(r'_+$', '', string)

    # Remove repeated special characters.
    string = re.sub(r'([^A-Za-z\d])\1{1,}', r'\1', string)

    # Convert to lower case, unless told not to.
    if to_lower:
        string = string.lower()

    return string


def to_ascii(string: str) -> str:
    """
    Convert string by keeping only ascii characters dropping others.

    Args:
        string: Input string to convert

    Returns:
        ASCII-only version of the string
    """
    return string.encode('ascii', errors='ignore').decode()


def make_folders(folder_paths: list[str], print_nl: bool = False) -> None:
    """
    Make folders from list of folder names.

    Args:
        folder_paths: List of folder paths to create
        print_nl: Whether to print newline after folder creation messages
    """
    from .logging import log

    global _folders_were_created
    if print_nl:
        _folders_were_created = False
    for path in folder_paths:
        if not Path(path).is_dir():
            log(f'Making folder: <{path}>.')
            Path(path).mkdir(parents=True, exist_ok=True)
            _folders_were_created = True
    if print_nl and _folders_were_created:
        log()


def make_folders_from_dic(path_dic: PathDic, print_nl: bool = False) -> None:
    """
    Make folders from PathDic object.

    Args:
        path_dic: PathDic object defining folder structure
        print_nl: Whether to print newline after folder creation messages
    """
    from .logging import log

    global _folders_were_created
    if print_nl:
        _folders_were_created = False
    make_folders([path_dic.path], print_nl=False)
    for sub_dic in path_dic.iter_sub_paths():
        make_folders_from_dic(sub_dic, print_nl=False)
    if _folders_were_created and print_nl:
        log()
