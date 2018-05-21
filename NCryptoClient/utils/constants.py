# -*- coding: utf-8 -*-
"""
Module for client application constants.
"""
from pathlib import Path

DEBUG = True
if DEBUG:
    shift = 2
else:
    shift = 1

path_tokens = Path(__file__).parts
project_pos = path_tokens.index('NCryptoClient')
project_path = path_tokens[0:(project_pos + shift)]

logo_rel_path = '\\Img\\NCryptoLogo_750x206.png'
add_rel_path = '\\Img\\add_24x24.png'
remove_rel_path = '\\Img\\remove_24x24.png'
bold_rel_path = '\\Img\\bold.jpg'
italic_rel_path = '\\Img\\italic.jpg'
underlined_rel_path = '\\Img\\underlined.jpg'

NCRYPTOLOGO_IMG_PATH = '\\'.join(project_path) + logo_rel_path
ADD_CONTACT_IMG_PATH = '\\'.join(project_path) + add_rel_path
REMOVE_CONTACT_IMG_PATH = '\\'.join(project_path) + remove_rel_path

BOLD_IMG_PATH = '\\'.join(project_path) + bold_rel_path
ITALIC_IMG_PATH = '\\'.join(project_path) + italic_rel_path
UNDERLINED_IMG_PATH = '\\'.join(project_path) + underlined_rel_path
