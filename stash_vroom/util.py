# Copyright 2025 Zyquo Onrel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module has common and frequently-used functions, which have no big dependencies.
"""

import os
import re
import logging

log = logging.getLogger(__name__)

def get_vid_re(extensions=('mp4', 'm4v', 'mkv', 'avi', 'webm', 'wmv', 'mov')):
    """
    Return a regular expression pattern to match file extensions.

    This is useful both for examining Python strings and also to submit to Stash as
    to find scenes with a regex filter. That is why this function returns a string and not
    a Python regex object.

    :param extensions: Optional list of 
    :return: A regex pattern that matches video file extensions.
    :rtype: str
    """

    if isinstance(extensions, str):
        extensions = [ extensions ]
    
    if isinstance(extensions, (tuple, list)):
        extensions = [ X for X in extensions if X ] # Remove empty strings
        extensions = list(dict.fromkeys(extensions)) # Remove duplicates

    extensions = [ re.escape(X) for X in extensions ]
    extensions = '|'.join(extensions)
    return r'\.(' + extensions + r')$'