import sqlite3
import gpod

def tracks_to_sqlite(db=None, sqlite=None):

    c = sqlite.cursor();

    def file_type(ipod_path):
        # FIXME: use regex-find instead of split

        if ipod_path.split(':')[-1].split('.')[-1] == 'mp4':
            return "video";
        else:
            return "audio";

    def insert_track (track):
        c.execute ("""SELECT id FROM albums WHERE name == ?""",
                   (track['album'],));

        al = c.fetchone();
        if al is None:
            c.execute ("""INSERT INTO albums (name) values (?)""",
                       (track['album'],));
            albumid = c.lastrowid;
        else:
            albumid = al[0];


        c.execute ("""SELECT id FROM artists WHERE name == ?""",
                   (track['artist'],));

        a = c.fetchone();
        if a is None:
            c.execute ("""INSERT INTO artists (name) values (?)""",
                       (track['artist'],));
            artistid = c.lastrowid;
        else:
            artistid = a[0];

        c.execute ("""INSERT INTO tracks(title, type, path,
        tracklen, trackid) VALUES
        (?, ?, ?, ?, ?)""", (track['title'], file_type(track['ipod_path']),
                             track['ipod_path'], track['tracklen'],
                             track['id']));
        trackid = c.lastrowid;

        c.execute ("""INSERT INTO relations (trackid, albumid, artistid)
        VALUES (?, ?, ?)""", (trackid, albumid, artistid));


    map (insert_track, db);

    sqlite.commit();



def sqlite_init(path):
    import os;

    os.unlink (path + '/itunesdb.sqlite');

    sqlite = sqlite3.connect(path + '/itunesdb.sqlite');

    c = sqlite.cursor();

    c.execute ("""create table tracks
    (id integer primary key, title text, type text,
    path text, tracklen int, trackid int)""");

    c.execute ("""create table artists
    (id integer primary key, name text)""");

    c.execute ("""create table albums
    (id integer primary key, name text)""");

    c.execute ("""create table relations
    (id integer primary key,
    trackid integer, albumid integer, artistid integer)""");

    sqlite.commit();

    c.close();

    sqlite.text_factory = str;

    return sqlite;

def itunesdb_to_sqlite(path=None):
    db = gpod.Database(path);

    sqlite = sqlite_init(path);

    tracks_to_sqlite(db, sqlite);


if __name__ == "__main__":
    import argparse;

    parser = argparse.ArgumentParser (description =
                                      """parse iTunesDB and dump sqlitedb""",
                                      epilog =
                                      """Distributed under GPL v2""");


    parser.add_argument ('--itunesdb', dest='itunesdb', action='store',
                         default='iTunesDB',
                         help='path to iTunesDB file');

    parser.add_argument ('--mountpoint', action='store',
                         default='/media/IPOD',
                         help='path to iPod mount-point');

    parser.add_argument ('-V', '--version', action='version',
                         version='%(prog)s 0.2');

    args = parser.parse_args()

    itunesdb_to_sqlite (args.mountpoint);

