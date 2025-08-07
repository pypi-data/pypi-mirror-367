#!/usr/bin/env python

#
# Copyright 2024 Chris Josephes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

'''
Flags represent additional data added to XML output for the purpose
of identifying likely data that will probably need closer scrutiny.

Each album and song has a flag object, which will contain zero or
more flags that will be output as an XML comment with the XML elements.
'''

# pylint: disable=R0903

from musicscan.data.flagcodes import AlbumFlagCodes, TrackFlagCodes


class AlbumFlags():
    '''
    Flags are warnings that are output in the XML
    so users can identify possible issues with
    the interpreted data.
    '''
    def __init__(self):
        self.flags = []

    def __contains__(self, in_flag: AlbumFlagCodes):
        return in_flag in self.flags

    def add_flag(self, in_code: int):
        '''
        Add a FlagCode to the array.
        '''
        self.flags.append(in_code)

    def to_xml_comment(self, in_padding: int = 3) -> str:
        '''
        Convert each flag code to an XML comment string value.
        '''
        p_str = ''
        if in_padding > 0:
            p_str = f"{' ' * in_padding}"
        if len(self.flags) > 0:
            flag_string = ''
            for f_code in self.flags:
                flag_string += AlbumFlagCodes.to_str(f_code) + ' '
            return f"{p_str}<!-- EDIT FLAGS: {flag_string} -->\n"
        return ''


class TrackFlags():
    '''
    Flags are warnings that are output in the XML
    so users can identify possible issues with
    the interpreted data.
    '''
    def __init__(self):
        self.flags = []

    def __contains__(self, in_flag: TrackFlagCodes):
        return in_flag in self.flags

    def add_flag(self, in_code: int):
        '''
        Add a FlagCode to the array.
        '''
        self.flags.append(in_code)

    def to_xml_comment(self, in_padding: int = 3) -> str:
        '''
        Convert each flag code to an XML comment string value.
        '''
        p_str = ''
        if in_padding > 0:
            p_str = f"{' ' * in_padding}"
        if len(self.flags) > 0:
            flag_string = ''
            for f_code in self.flags:
                flag_string += TrackFlagCodes.to_str(f_code) + ' '
            return f"{p_str}<!-- EDIT FLAGS: {flag_string} -->\n"
        return ''
