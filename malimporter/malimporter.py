#!/usr/bin/env python3

"""
malimporter.py is part of animedb.
The purpose of this program is to import an anime profile export from MAL into a database for use by animedb.
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

import sys;
import argparse;
import xml.etree.ElementTree;
import sqlite3;

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
        self.animeid = animeobj.find("series_animedb_id").text
        self.title = animeobj.find("series_title").text;
        self.episodes = animeobj.find("series_episodes").text;
        self.type = animeobj.find("series_type").text;
        self.watched = animeobj.find("my_watched_episodes").text;
        self.score = animeobj.find("my_score").text;
        self.status = animeobj.find("my_status").text;
        self.notes = animeobj.find("my_comments").text;

def metadata(meta):
    """
    collect meta data
    """
    for data in meta.findall("myinfo"):
        Anime.userid = data.find("user_id").text;
        Anime.username = data.find("user_name").text;
        Anime.watchingcount = data.find("user_total_watching").text;
        Anime.completedcount = data.find("user_total_completed").text;
        Anime.onholdcount = data.find("user_total_onhold").text;
        Anime.droppedcount = data.find("user_total_dropped").text;
        Anime.animecount = data.find("user_total_anime").text;

def dbconnect(dbname):
    """
    connect to our database and return the object
    """
    try:
        dbcon = sqlite3.connect(dbname);
    except:
        e = sys.exc_info()[0];
        exit(e);
    return dbcon; 

def dbcommitclose(db):
    """
    commit and close database
    """
    db.commit();
    db.close();

def dbcreatetables(db):
    """
    create our required tables if they don't exist
    """
    metaquery = ("CREATE TABLE IF NOT EXISTS meta (maluserid TEXT, " \
                 "malusername TEXT, " \
                 "watchingcount INTEGER, " \
                 "completedcount INTEGER, " \
                 "onholdcount INTEGER, " \
                 "droppedcount INTEGER, " \
                 "animecount INTEGER)");
    animequery = ("CREATE TABLE IF NOT EXISTS anime (id INTEGER PRIMARY KEY AUTOINCREMENT, "\
                  "animeid INTEGER, " \
                  "title TEXT, " \
                  "episodes INTEGER, " \
                  "type TEXT, " \
                  "watched INTEGER, "
                  "score INTEGER, " \
                  "status TEXT, " \
                  "notes TEXT)");
    db.execute(metaquery);
    db.execute(animequery);

def dbinsertmetadata(db):
    """
    insert our meta data
    """
    metadata = (Anime.userid,
                Anime.username,
                Anime.watchingcount,
                Anime.completedcount,
                Anime.onholdcount,
                Anime.droppedcount,
                Anime.animecount);
    db.execute("INSERT INTO meta VALUES(?, ?, ?, ?, ?, ?, ?)", metadata);

def dbinsertanimedata(db, animelist):
    """
    insert anime data
    """
    animedata = [];
    for anime in animelist:
        animedata.append([anime.animeid,
                          anime.title,
                          anime.episodes,
                          anime.type,
                          anime.watched,
                          anime.score,
                          anime.status,
                          anime.notes]);
    db.executemany("INSERT INTO anime ('animeid', " \
                    "'title', " \
                    "'episodes', " \
                    "'type', " \
                    "'watched', " \
                    "'score', " \
                    "'status', " \
                    "'notes') " \
                    "VALUES(?, ?, ?, ?, ?, ?, ?, ?)", animedata);


if __name__ == "__main__":
    """
    argument parse
    xml parse
    collect meta data (total anime, etc)
    append each anime to animelist[]
    connect to database
    create our tables if they don't exist
    insert meta data into the meta table
    insert anime data into the anime table
    commit and close database
    """

    parser = argparse.ArgumentParser();
    parser.add_argument("-i", "--import", type=str, action="store", dest="xmlfile",
            required=True,
            help="XML anime export file from MAL to be imported");
    parser.add_argument("-d", "--database", type=str, action="store", dest="dbfile",
            default="../userdb.db", required=False,
            help="sqlite3 database file to import into");
    args = parser.parse_args();

    print("importing {} into {}".format(args.xmlfile, args.dbfile));

    animelist = [];

    try:
        e = xml.etree.ElementTree.parse(args.xmlfile).getroot();
    except FileNotFoundError as e:
        exit(e);

    # collect meta data
    metadata(e);

    # collect anime data
    for animes in e.findall("anime"):
        animelist.append(Anime(animes));

    # connect to our database
    db = dbconnect(args.dbfile);

    # create the anime table if required
    dbcreatetables(db);

    # insert meta data into the database
    dbinsertmetadata(db);

    # insert anime data into the database
    dbinsertanimedata(db, animelist);

    # commit and close db
    dbcommitclose(db);

    print("MAL name: {}\n" \
            "MAL id: {}\n" \
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

