#!/usr/bin/env python3

"""
malimporter.py is part of animedb. The purpose of this program is to import an
Copyright (C) 2018 Daniel Jones daniel@danieljon.es 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import argparse;
import xml.etree.ElementTree;
import codecs;

class Anime:
    """
    each anime imported gets its own instance of Anime
    meta data stored here
    """
    userid = 0;
    username = "";
    watchingcount = 0;
    completedcount = 0;
    onholdcount = 0;
    droppedcount = 0;
    plantowatchcount = 0;
    animecount = 0;
    def __init__(self, animeobj):
        self.title = animeobj.find("series_title").text;
        self.episodes = animeobj.find("series_episodes").text;
        self.type = animeobj.find("series_type").text;
        self.watched = animeobj.find("my_watched_episodes").text;
        self.score = animeobj.find("my_score").text;
        self.status = animeobj.find("my_status").text;
        self.notes = animeobj.find("my_comments").text;

if __name__ == "__main__":
    """
    argument parse
    xml parse
    collect meta data (total anime, etc)
    append each anime to animes[]
    """

    parser = argparse.ArgumentParser();
    parser.add_argument("-i", "--import", type=str, action="store", dest="xmlfile",
            required=True,
            help="XML anime export file from MAL to be imported");
    args = parser.parse_args();

    print("importing {}".format(args.xmlfile));

    animelist = [];

    try:
        e = xml.etree.ElementTree.parse(args.xmlfile).getroot();
    except FileNotFoundError as e:
        exit(e);

    for metadata in e.findall("myinfo"):
        Anime.userid = metadata.find("user_id").text;
        Anime.username = metadata.find("user_name").text;
        Anime.watchingcount = metadata.find("user_total_watching").text;
        Anime.completedcount = metadata.find("user_total_completed").text;
        Anime.onholdcount = metadata.find("user_total_onhold").text;
        Anime.droppedcount = metadata.find("user_total_dropped").text;
        Anime.animecount = metadata.find("user_total_anime").text;

    for animes in e.findall("anime"):
        animelist.append(Anime(animes));

    print("{} - {}\n" \
            "total anime {}\n" \
            "total watching {}\n" \
            "total completed {}\n" \
            "total on hold {}\n" \
            "total dropped {}" \
            .format(
                Anime.username,
                Anime.userid,
                Anime.animecount,
                Anime.watchingcount,
                Anime.completedcount,
                Anime.onholdcount,
                Anime.droppedcount));

