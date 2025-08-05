#!/usr/bin/env python

#
# Copyright 2025 Chris Josephes
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
Data objects for music.
'''

# pylint: disable=too-many-instance-attributes

from __future__ import annotations
from datetime import timedelta
from typing import TYPE_CHECKING
from tinytag import TinyTag  # type: ignore
from musicscan.data.flags import TrackFlags, TrackFlagCodes
from musicscan.data.stringtools import sanitize_year


if TYPE_CHECKING:
    from musicscan.data.cd import Album


class Track():
    '''
    A track identifies a single musical track on an album,
    created through ID3 data.
    '''
    def __init__(self, in_tag: TinyTag):
        self.title: str | None = ''
        self.artist: str | None = ''
        self.album: str | None = ''
        self.album_o: Album | None = None
        self.track_no = 0
        self.track_total = 0
        self.disc_no = 0
        self.disc_total = 0
        self.bpm = 0
        self.short_title = ''
        self.album_artist = ''
        self.composer = ''
        self.year = '0000'
        self.flags = TrackFlags()
        self.duration_t: timedelta | None = None
        self.duration_s: str = ''
        # self.indices = []
        self._process(in_tag)

    def _process(self, in_tag: TinyTag):
        self.title = in_tag.title
        self.genre = in_tag.genre
        self.artist = in_tag.artist
        self._process_integer_values(in_tag)
        self.album = in_tag.album
        if in_tag.albumartist:
            self.album_artist = in_tag.albumartist
        if in_tag.composer:
            self.composer = in_tag.composer
        self._process_duration(in_tag)
        if in_tag.year:
            self.year = sanitize_year(in_tag.year)
        else:
            self.flags.add_flag(TrackFlagCodes.m_year)

    def _process_duration(self, in_tag: TinyTag):
        '''
        Reduce the duration value to 2 decimals of a second.
        '''
        duration: float | None = in_tag.duration
        if duration is not None:
            limited_duration: float = duration * 100 / int(100)
            self.duration_t = timedelta(seconds=float(limited_duration))
            self.duration_s = Track._make_iso_interval(self.duration_t)

    def _process_integer_values(self, in_tag: TinyTag):
        '''
        Process integer values and make sure they are valid.
        '''
        if in_tag.track:
            self.track_no = int(in_tag.track)
        if in_tag.track_total:
            self.track_total = int(in_tag.track_total)
        if in_tag.disc:
            self.disc_no = int(in_tag.disc)
        if in_tag.disc_total:
            self.disc_total = int(in_tag.disc_total)

    def set_album_object(self, in_album_object: Album):
        '''
        The album object is a reference back to the object that
        contains the track.
        '''
        self.album_o = in_album_object

    @classmethod
    def _make_iso_interval(cls, in_delta: timedelta):
        '''
        Generate an ISO duration value based on
        a Python timedelta object.
        '''
        string1 = str(in_delta)
        fld = string1.split(':')
        minutes = int(fld[1])
        seconds = float(fld[2])
        return f"PT{minutes}M{seconds:.2f}S"

    def get_album_artist(self) -> str | None:
        '''
        Return an artist value, whether it exists or not.
        '''
        return self.album_artist or self.artist

    def track_id(self) -> str:
        '''
        Return track information.
        '''
        return f"[ {self.track_no:02d} / {self.track_total:02d} " +\
               f" {self.disc_no} / {self.disc_total} ]"

    def __lt__(self, other) -> bool:
        return self.track_no < other.track_no

    def __rt__(self, other) -> bool:
        return self.track_no > other.track_no

    def __str__(self) -> str:
        return f"{self.track_id()} {self.title} ({self.artist})"
