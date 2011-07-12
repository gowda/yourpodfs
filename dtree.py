import logging
import sqlite3

def subdirs (path=None, s=None):
    if path is None:
        return ['.', '..'];

    elif path == "/":
        logging.debug ("subdirs of /");
        return [('.',), ('..',), ('artists',), ('albums',),
                ('no - spaces - please',)];

    elif path == "/artists":
        try:
            c = s.cursor();
        except sqlite3.Error, e:
            logging.error ("failed to open cursor: %s" % e.args[0]);

        c.execute ("""select name from artists""");

        rows = list(c.fetchall());

        c.close();

        return rows;

    elif path == "/albums":
        try:
            c = s.cursor();
        except sqlite3.Error, e:
            logging.error ("failed to open cursor: %s" % e.args[0]);

        c.execute ("""select name from albums""");

        rows = list(c.fetchall());

        c.close();

        return rows;

    else:
        return [("later",)];


