#!/usr/bin/env python3

"""
generatewebpages.py is part of animedb.
The purpose of this program is to generate all our html pages.
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
import sqlite3;
import os;
import re;
from os import fdopen, remove;
from shutil import copyfile;
from tempfile import mkstemp;
from shutil import move;

class Anime:
    """
    every anime from the database will get an instance of this class
    """
    colors = {  
            "Plan to Watch": "gray", 
            "On-Hold": "orange", 
            "Watching": "blue", 
            "Completed": "green",
            };

    def __init__(self, animeobj):
        self.dbpos = animeobj[0];
        self.animeid = animeobj[1];
        self.title = animeobj[2].replace("\"", "&quot;");
        self.episodes = animeobj[3];
        self.type = animeobj[4];
        self.watched = animeobj[5];
        self.score = animeobj[6];
        self.status = animeobj[7];
        self.notes = str(animeobj[8]).replace("\"", "&quot;");
        self.output = ""; # our final html string

    def setstatuscolor(self, status):
        try:
            self.statuscolor = Anime.colors[status];
        except KeyError:
            self.statuscolor = "black";

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

def dbclose(db):
    """
    close database
    """
    db.close();

def dbcollectanimedata(db):
    """
    collect anime data from the database
    """
    animelist = [];
    c = db.cursor();
    for anime in c.execute("SELECT * FROM anime;"):
        animelist.append(anime);
    return animelist;

def replacestringinfile(file_path, string, substr):
    """
    replaces contents in a file
    """
    fh, abs_path = mkstemp();
    with fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(string, substr));
    remove(file_path);
    move(abs_path, file_path);

def replacestring(string, substr, replacement):
    return string.replace(substr, replacement);

def insertanimedata(anime):
    tmp = animetemplate;
    tmp = replacestring(tmp, "{ANIME_UNDERLINED_TITLE}", re.sub(r'[^\x00-\x7f]',r'', anime.title.replace(" ", "_")));
    tmp = replacestring(tmp, "{ANIME_ID}", str(anime.animeid));
    tmp = replacestring(tmp, "{ANIME_TITLE}", re.sub(r'[^\x00-\x7f]',r'', anime.title));
    tmp = replacestring(tmp, "{TOTAL_EPISODES}", str(anime.episodes));
    tmp = replacestring(tmp, "{EPISODES_WATCHED}", str(anime.watched));
    tmp = replacestring(tmp, "{WATCH_STATUS_COLOR}", anime.statuscolor);
    tmp = replacestring(tmp, "{WATCH_STATUS}", anime.status);
    tmp = replacestring(tmp, "{RATING}", str(anime.score));
    tmp = replacestring(tmp, "{NOTES}", re.sub(r'[^\x00-\x7f]',r'', str(anime.notes)));
    anime.output = tmp;

# this template is used for every anime we display
animetemplate = (
        "<div class=\"box\">\n"
        "<div class=\"anime\">\n"
        "<div id=\"{ANIME_UNDERLINED_TITLE}\">\n"
        "<img width=96 height=137 src=\"covers/{ANIME_ID}.jpg\" alt=\"{ANIME_TITLE} cover\">\n"
        "<div class=\"viewing\">\n"
        "{ANIME_TITLE} <br>\n"
        "{TOTAL_EPISODES} episodes ({EPISODES_WATCHED} watched) <br>\n"
        "status: <font color=\"{WATCH_STATUS_COLOR}\">{WATCH_STATUS}</font> <br>\n"
        "rating: {RATING}/10 <br>\n"
        "notes: {NOTES}<br>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n"
        "</div>\n");

if __name__ == "__main__":
    """
    parse arguments
    connect to database
    generate anime strings from template and database
    close database
    """

    parser = argparse.ArgumentParser();
    parser.add_argument("-d", "--database", type=str, action="store", dest="dbfile",
            default="userdb.db", required=False,
            help="sqlite3 database file containing anime information");
    parser.add_argument("-o", "--output", type=str, action="store", dest="outdir",
            default="output", required=False,
            help="directory to output generated pages");
    args = parser.parse_args();

    # if our database (file) doesn't exist, exit
    if not os.path.isfile(args.dbfile):
        exit("file doesn't exist {}".format(args.dbfile));

    db = dbconnect(args.dbfile);

    # collect anime from database
    animelist = dbcollectanimedata(db);

    # create an instance of Anime for each anime
    formattedanimelist = [];
    for anime in animelist:
        formattedanimelist.append(Anime(anime));

    # set the status color for each anime
    for anime in formattedanimelist:
        anime.setstatuscolor(anime.status);

    # insert anime data for each Anime instance
    for anime in formattedanimelist:
        insertanimedata(anime);
    
    # copy index.txt to output/index.html
    copyfile("index.txt", "output/index.html");

    # generate string containing all anime output strings
    output = [];
    for anime in formattedanimelist:
        output.append(anime.output);

    # place output into index.html
    replacestringinfile("output/index.html", "{CONTENT}", " ".join(output));

    dbclose(db);


