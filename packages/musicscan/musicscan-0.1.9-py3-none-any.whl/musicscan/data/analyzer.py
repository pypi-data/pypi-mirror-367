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
Testing code to identify possible edit flags.
'''

# pylint: disable=too-many-public-methods

import re
from musicscan.data.cd import Album
from musicscan.data.flags import AlbumFlagCodes, TrackFlagCodes
from musicscan.data.track import Track


class Analyzer():
    '''
    Perform tests against the data and
    add flags when appropriate.
    '''

    def main_test(self, in_album: Album):
        '''
        Main album testing routine.
        '''
        self.album_tests(in_album)
        self.track_tests(in_album)
        self.album_closing_tests(in_album)

    def album_tests(self, in_album: Album):
        '''
        Perform tests against the album.
        '''
        self.check_album_values(in_album)
        self.test_album_title(in_album)
        self.test_album_artist(in_album)
        self.test_soundtrack(in_album)
        self.test_score(in_album)
        self.test_tribute(in_album)

    def track_tests(self, in_album: Album):
        '''
        Perform tests against every track.
        '''
        for dsc in sorted(in_album.discs):
            for trk in sorted(in_album.discs[dsc].tracks,
                              key=lambda x: x.track_no):
                self.check_track_values(trk)
                self.test_album_track_chrs(trk)
                self.test_album_track_featured(trk)
                self.test_album_track_live(trk)
                self.test_track_genre(trk)
                self.test_album_track_blank(trk)
                self.test_album_track_bonus(trk)
                self.test_album_track_intro(trk)
                self.test_album_track_reprise(trk)

    def album_closing_tests(self, in_album: Album):
        '''
        Perform additional tests after all
        tracks are analzed.
        '''
        self.test_intro_reprise_presence(in_album)

    def check_album_values(self, in_album: Album):
        '''
        If album values are missing, put in placeholder
        values.
        '''
        if not in_album.title:
            in_album.title = 'PLACEHOLDER ALBUM TITLE'
            in_album.flags.add_flag(TrackFlagCodes.m_album_title)

    def check_track_values(self, in_track: Track):
        '''
        If track values are missing, put in placeholder
        values.
        '''
        if not in_track.artist:
            in_track.artist = 'PLACEHOLDER TRACK ARTIST'
            in_track.flags.add_flag(TrackFlagCodes.m_track_artist)

    def test_album_title(self, in_album: Album):
        '''
        Test album title for keywords that may indicate
        a compilation of some kind.
        '''
        greatest_p = re.compile(r'Greatest', re.IGNORECASE)
        hits_p = re.compile(r'\s+Hit', re.IGNORECASE)
        if greatest_p.search(in_album.title):
            in_album.flags.add_flag(AlbumFlagCodes.p_greatest)
        if hits_p.search(in_album.title):
            in_album.flags.add_flag(AlbumFlagCodes.p_hits_compo)

    def test_soundtrack(self, in_album: Album):
        '''
        Test album title for keywords that may indicate
        a soundtrack album.
        '''
        first_track = in_album.first_track()
        soundtrack_p = re.compile(r'\s+Soundtrack\s+', re.IGNORECASE)
        if soundtrack_p.search(in_album.title):
            in_album.flags.add_flag(AlbumFlagCodes.p_soundtrack)
        if first_track.genre == 'Soundtrack':
            if AlbumFlagCodes.p_soundtrack not in in_album.flags.flags:
                in_album.flags.add_flag(AlbumFlagCodes.p_soundtrack)

    def test_score(self, in_album: Album):
        '''
        Test album title for keywords that may indicate
        a score album.
        '''
        score_p = re.compile(r'\s+Score\s+', re.IGNORECASE)
        if score_p.search(in_album.title):
            in_album.flags.add_flag(AlbumFlagCodes.p_score)

    def test_tribute(self, in_album: Album):
        '''
        Test if the album title suggests that it is a
        tribute to another artist.
        '''
        tribute_p = re.compile(r'\s+Tribute\s+', re.IGNORECASE)
        if tribute_p.search(in_album.title):
            in_album.flags.add_flag(AlbumFlagCodes.p_tribute)

    def test_album_artist(self, in_album: Album):
        '''
        Test the name of the artist for indicators
        the band may be a group.
        '''
        and_p = re.compile(r'\s+and\s+', re.IGNORECASE)
        if and_p.search(str(in_album.artist)):
            in_album.flags.add_flag(TrackFlagCodes.l_group)

    def test_album_track_chrs(self, in_track: Track):
        '''
        Test the track title to indicate metadata may
        have been embeded in the track name in parenthesis.
        '''
        if in_track.title is not None:
            if '[' in in_track.title or ']' in in_track.title:
                in_track.flags.add_flag(TrackFlagCodes.d_sq_brackets)
        if in_track.title is not None:
            if '(' in in_track.title or ')' in in_track.title:
                in_track.flags.add_flag(TrackFlagCodes.d_parenthesis)

    def test_album_track_featured(self, in_track: Track):
        '''
        Test the track title or track artist to see if
        there may be additional artists for this particular track.
        '''
        feature_p = re.compile(r'Feat', re.IGNORECASE)
        with_p = re.compile(r'With\s+', re.IGNORECASE)
        if in_track.title is not None:
            if (feature_p.search(in_track.title) or
                    with_p.search(in_track.title)):
                in_track.flags.add_flag(TrackFlagCodes.p_feat_artist)
        if in_track.artist is not None:
            if (feature_p.search(in_track.artist) or
                    with_p.search(in_track.artist)):
                in_track.flags.add_flag(TrackFlagCodes.p_feat_artist)

    def test_album_track_live(self, in_track: Track):
        '''
        Test the track title to see if it might
        indicate a live recording.
        '''
        live_p = re.compile(r'Live\s+', re.IGNORECASE)
        if in_track.title is not None:
            if live_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_live)

    def test_track_genre(self, in_track: Track):
        '''
        Test the track for bad genre values.
        '''
        country_p = re.compile(r'Country & Folk', re.IGNORECASE)
        if in_track.genre:
            if country_p.search(in_track.genre):
                in_track.flags.add_flag(TrackFlagCodes.p_genre_country_folk)

    def test_album_track_demo(self, in_track: Track):
        '''
        Test the track title to see if it might
        be a demo recording.
        '''
        demo_p = re.compile(r'Demo', re.IGNORECASE)
        if in_track.title is not None:
            if demo_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_demo)

    def test_album_track_blank(self, in_track: Track):
        '''
        Test the track title to see if it might
        be a blank track to pad the CD content.
        '''
        blank_p = re.compile(r'Blank', re.IGNORECASE)
        if in_track.title is not None:
            if blank_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_blank_track)

    def test_album_track_bonus(self, in_track: Track):
        '''
        Test the track title to see if it might
        indicate the track is a bonus track
        (which could also indicate a re-issue)
        '''
        bonus_p = re.compile(r'\W+Bonus', re.IGNORECASE)
        if in_track.title is not None:
            if bonus_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_bonus_track)

    def test_album_track_intro(self, in_track: Track):
        '''
        Test the track to see if it is an introduction to
        another track, or possibly for the album itself.
        '''
        intro_p = re.compile(r'[\s\W]?Intro', re.IGNORECASE)
        if in_track.title is not None:
            if intro_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_intro)

    def test_album_track_reprise(self, in_track: Track):
        '''
        Test the track to see if it is labeled as a
        reprise, either to the album, or to a previous
        track on the album.
        '''
        reprise_p = re.compile(r'[\s\W]?Reprise', re.IGNORECASE)
        if in_track.title is not None:
            if reprise_p.search(in_track.title):
                in_track.flags.add_flag(TrackFlagCodes.p_reprise)

    def test_intro_reprise_presence(self, in_album: Album):
        '''
        Test to see if both an intro and reprise is
        contained in the album, and add an additional
        album level flag to identify it.
        '''
        reprise = False
        intro = False
        for dsc in sorted(in_album.discs):
            for trk in sorted(in_album.discs[dsc].tracks,
                              key=lambda x: x.track_no):
                if TrackFlagCodes.p_intro in trk.flags:
                    intro = True
                if TrackFlagCodes.p_reprise in trk.flags:
                    reprise = True
                if intro and reprise:
                    in_album.flags.add_flag(AlbumFlagCodes.p_intro_reprise)
                    break
