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
Object for collecitng basic statistics.
'''

# pylint: disable=too-many-instance-attributes


from datetime import datetime


class Stats():
    '''
    Statistics from all operations of a given tool.
    '''
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = datetime.now()
        self.source_dirs = 0
        self.source_files = 0
        self.source_skipped = 0
        self.album_count = 0
        self.track_count = 0
        self.files_written = 0
        self.process_id = 0

    def close(self):
        '''
        Save the end time for the program run.
        '''
        self.end_time = datetime.now()

    def header(self) -> str:
        '''
        Generate a simple run header.
        '''
        out = ''
        out += "\n\n"
        out += "===================================\n"
        out += " --- Program Start ---\n"
        out += "===================================\n"
        out += f"{'Start Time':20s}: {self.start_time}\n"
        out += f"{'Process Id':20s}: {self.process_id}\n\n"
        return out

    def report(self) -> str:
        '''
        Generate a simple report string.
        '''
        out = "\n\n"
        out += "===================================\n"
        out += " --- Operations Statistics ---\n"
        out += "===================================\n"
        out += "\nInput Files\n===========\n"
        out += f"{'Directories Scanned':20s}: {self.source_dirs}\n"
        out += f"{'Files Scanned':20s}: {self.source_files}\n"
        out += "\nMusic Breakdown\n===============\n"
        out += f"{'Album Count':20s}: {self.album_count}\n"
        out += f"{'Total Tracks':20s}: {self.track_count}\n"
        out += "\nOutput Files\n============\n"
        out += f"{'Files Written':20s}: {self.files_written}\n"
        out += "\nTimes\n=====\n"
        out += f"{'Start Time':20s}: {self.start_time}\n"
        out += f"{'End Time':20s}: {self.end_time}\n"
        out += f"{'Run Duration':20s}: {self.end_time - self.start_time}\n"
        out += f"{'Process Id':20s}: {self.process_id}\n"
        out += "\n\n"
        out += "===================================\n"
        out += " --- Program End ---\n"
        out += "===================================\n"
        return out
