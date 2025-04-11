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
This module provides utility functions for working with JAV files and filenames.
"""

import os
import re
import logging

from . import util
from . import slr

log = logging.getLogger(__name__)

def get_is_jav(filepath):
    """
    Determine if the given file is a JAV (Japanese Adult Video) file.

    This function checks if the provided file matches the criteria for a JAV file
    by leveraging the `get_jav_info` function. If the file is identified as a JAV,
    the function returns `True`; otherwise, it returns `False`.

    :param filepath: The path to the file to be checked.
    :type filepath: str
    :return: `True` if the file is a JAV, `False` otherwise.
    """
    return not not get_jav_info(filepath)

def get_jav_info(filepath):
    if get_is_stream(filepath):
        #log.debug(f'  - Not JAV; matched stream: {repr(filepath)}')
        return None

    filename = os.path.basename(filepath)
    mtch = match_jav_filename(filename)
    if not mtch:
        #log.debug(f'  - Not JAV; no regex match')
        return None

    years = [ str(X) for X in range(2010, 2030) ]
    if mtch[3] in years:
        # log.info(f'  - Not JAV for year match {repr(filename)}: "{mtch[1]}" "{mtch[2]}" {mtch[3]}')
        return None
    part = mtch[5] if mtch[5] else ''
    part = re.sub(r'^part', '', part, flags=re.IGNORECASE)
    part = part.upper()
    # log.debug(f'  - JAV match {repr(filename)}: "{mtch[1]}" "{mtch[2]}" {mtch[3]} {repr(mtch[4])} {repr(part)}')
    return {'studio':mtch[1].upper(), 'id':mtch[3], 'mid':mtch[2], 'filename':filename, 'part':part}

def match_jav_filename(filename):
    ok_extension_re = util.get_vid_re()

    studio_info = slr.get_studio_info(filename)
    if studio_info:
        #log.debug(f'  - Not JAV; matched studio: {studio_info}')
        return None

    if filename.endswith('-181_180x180_3dh_LR.mp4'):
        #log.debug(f'  - Not JAV; matched suffix')
        return None

    prefixes = ['SLR-', 'SLR_', 'JillVR_', 'realhotvr-', 'wankzvr-', 'reality-lovers-', 'sexbabesvr-', 'only2xvr-']
    for prefix in prefixes:
        if filename.startswith(prefix):
            #log.debug(f'  - Not JAV; matched prefix: {prefix}')
            return None

    fname = filename

    # Fix all the WVR variants first.
    #fname = re.sub(r'^wvr0(\d)'                    , r'WVR1-\1', fname, flags=re.IGNORECASE)
    fname = re.sub(r'^2DSVR\b'                     , r'DSVR'   , fname, flags=re.IGNORECASE)

    fname = re.sub(r'^WVR-11-(\d\d\d)'             , r'WVR1-\1', fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-2-(\d\d\d)'              , r'WVR1-\1', fname, flags=re.IGNORECASE)

    fname = re.sub(r'^WVR-101(\d\d\d)'             , r'WVR1\1' , fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-11(\d\d\d)'              , r'WVR1\1' , fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-2(\d)'                   , r'WVR1\1' , fname, flags=re.IGNORECASE)

    fname = re.sub(r'^WVR5D-'                      , r'WVR6-'  , fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR5-D(\d)'                  , r'WVR6-\1', fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR5D(\d\d\d)'               , r'WVR6\1' , fname, flags=re.IGNORECASE)

    fname = re.sub(r'^WVR7(\d\d\w)\b'              , r'WVR80\1',fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-9(\d\d\d)'              , r'WVR8\1', fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-9(\d\d\d)'               , r'WVR8\1', fname, flags=re.IGNORECASE)

    fname = re.sub(r'^WVR8d\b'                     , r'WVR9'  , fname, flags=re.IGNORECASE)
    fname = re.sub(r'^WVR-91(\d\d\d)'              , r'WVR9\1', fname, flags=re.IGNORECASE)

    # Fix all the rest.
    fname = re.sub(ok_extension_re                    , ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'[-_\b]mkx199'                    , ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'[-_\b]mkx219'                    , ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'[-_]*(299|320|640|720|\d\d\d\d)p', ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'179-SBS\b'                       , ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'179_LR\b'                        , ''      , fname, flags=re.IGNORECASE)
    fname = re.sub(r'_\d+-SLR\b'                      , ''      , fname, flags=re.IGNORECASE) # SLR downloads
    #fname = re.sub(r'abc122', '', fname)

    #log.debug(f'-- fname = {repr(fname)}')
    connector_re = r'[-_-1\s\.]*'
    part_re = f'({connector_re})' + r'(\d{0,2}\b|[a-z]\b|part\d+)'
    jav_re = (''
        + r'\b'
        #+ r'(2?[a-z]{3,9}(?:6|6D|8|9D)?)'
        #+ r'(2?[a-z]{3,9})'
        #+ r'(WVR0|WVR4|WVR8|WVR9|WVR6)'
        + r'(WVR0|WVR4|WVR8|WVR9|WVR6|[a-z]{3,9})'
        + f'({connector_re})'
        + r'(\d{2,6})'
        + r'(?:' + part_re + r')?'
    )
    mtch = re.search(jav_re, fname, re.IGNORECASE)
    return mtch