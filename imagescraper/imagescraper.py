#!/usr/bin/env python3

"""
imagescraper.py is part of animedb.
The purpose of this program is to scrape images from MAL for each anime inside our database.
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
import os.path;
import urllib.request;
import re;

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

def dbgetanimeids(db):
    """
    collect anime ids from the database and return a list of them
    """
    ids = [];
    c = db.cursor();
    for id in c.execute("SELECT animeid FROM anime;"):
        ids.append(id[0]);
    return ids;

def createlinks(ids):
    """
    create MAL links from the ids and return a list of them
    """
    links = [];
    for anime in ids:
        links.append("https://myanimelist.net/anime/{}".format(anime));
    return links;

def scrapelinks(animelinks):
    """
    scrape MAL link for the anime cover links
    regex on html, what could go wrong?
    """
    links = [];
    for link in animelinks:
        src = urllib.request.urlopen(link).read().decode("utf-8");
        for l in re.findall('https:\/\/myanimelist\.cdn-dena\.com\/images\/anime\/[0-9]*\/[0-9]*.jpg', src):
            links.append(l);
            break;
    return links;

def getcoverimage(link, directory, animeid):
    """
    download the cover image file and save it
    """
    print("downloading {}".format(link));
    urllib.request.urlretrieve(link, directory + "/{}.jpg".format(animeid))

if __name__ == "__main__":
    """
    retrieve anime id's from the database
    construct urls to scrape
    scrape url for cover image link
    download cover images and save them to a given or default directory
    """

    parser = argparse.ArgumentParser();
    parser.add_argument("-d", "--database", type=str, action="store", dest="dbfile",
            default="../userdb.db", required=False,
            help="sqlite3 database file containing anime information");
    parser.add_argument("-o", "--output", type=str, action="store", dest="outdir",
            default="../output/covers", required=False,
            help="directory to save images");
    args = parser.parse_args();

    # if our database (file) doesn't exist, exit
    if not os.path.isfile(args.dbfile):
        exit("file doesn't exist {}".format(args.dbfile));

    db = dbconnect(args.dbfile);

    # collect anmie ids
    animeids = dbgetanimeids(db);
    # create MAL anime links
    animelinks = createlinks(animeids);

    # scrape links for the cover image link
    print("scraping MAL pages... this may take some time...");
    coverlinks = scrapelinks(animelinks);

    # download cover images
    x = 0;
    for link in coverlinks:
        getcoverimage(link, args.outdir, animeids[x]);
        x += 1;

    dbclose(db);
