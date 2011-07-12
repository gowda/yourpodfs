import os, sys
from errno import *
from stat import *

import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

fuse.feature_assert('stateful_files', 'has_init')

# directory tree is implemented in dtree module
from dtree import subdirs

# put the log init to some nice place
import logging

LOGFILE="/tmp/python-ipod.log"
logging.basicConfig (filename=LOGFILE, level=logging.DEBUG);

class iFs(Fuse):

    def __init__(self, source, *args, **kw):

        Fuse.__init__(self, *args, **kw)

        self.source = source;

        # dump the iTunesDB to sqlite-db and store handles to both
        from itunesdb_to_sqlite import itunesdb_to_sqlite, sqlite_init

        itunesdb_to_sqlite (source);

        import sqlite3

        self.sqlitedb = sqlite3.connect(source + '/itunesdb.sqlite');

        logging.debug ("__init__: %s" % source);

    def getattr(self, path):
        logging.error ("getattr: %s", path);
        return os.lstat (self.source);

    def readdir(self, path, offset):
        logging.debug ("readdir: %s, %d" % (path, offset));
        l = subdirs(path, s=self.sqlitedb);

        for e in l:
            logging.debug ("""%s""" % e[0]);
            yield fuse.Direntry(name=e[0].encode('ascii'));


    def statfs(self):
        """
        Should return an object with statvfs attributes (f_bsize, f_frsize...).
        Eg., the return value of os.statvfs() is such a thing (since py 2.2).
        If you are not reusing an existing statvfs object, start with
        fuse.StatVFS(), and define the attributes.

        To provide usable information (ie., you want sensible df(1)
        output, you are suggested to specify the following attributes:

            - f_bsize - preferred size of file blocks, in bytes
            - f_frsize - fundamental size of file blcoks, in bytes
                [if you have no idea, use the same as blocksize]
            - f_blocks - total number of blocks in the filesystem
            - f_bfree - number of free blocks
            - f_files - total number of file inodes
            - f_ffree - nunber of free file inodes
        """

        return os.statvfs(self.source)

    def fsinit(self):
        pass;


    def main(self, *a, **kw):
        return Fuse.main(self, *a, **kw)


def main(source=None, mountpoint=None):

    usage = """
ipod-fs: provide the ipod's iTunesDB as a file-system.

""" + Fuse.fusage

    server = iFs(source=source,
                 version="%prog " + fuse.__version__,
                 usage=usage,
                 dash_s_do='setsingle')

    server.parser.add_option ('--itunesdb', dest='itunesdb', action='store',
                              default='iTunesDB',
                              help='path to iTunesDB file');

    server.parser.add_option ('--source', dest='source', action='store',
                              default='/media/IPOD',
                              help='path to raw mounted IPOD');


    server.parse(values=server, errex=1)

    server.main()


if __name__ == '__main__':
    import argparse;

    parser = argparse.ArgumentParser (description =
                                      """access audio/video/photos on iPod""",
                                      epilog =
                                      """Distributed under GPL v2""");

    parser.add_argument ('--itunesdb', dest='itunesdb', action='store',
                         default='iTunesDB',
                         help='path to iTunesDB file');

    parser.add_argument ('--source', dest='source', action='store',
                         default='/media/IPOD',
                         help='path to raw mounted IPOD');

    parser.add_argument ('-s', action='store_true',
                         help='single thread mode');

    parser.add_argument ('mountpoint', action='store',
                         default='/media/IPOD-FUSE',
                         help='path to mountpoint');


    args = parser.parse_args();

    main (source=args.source, mountpoint=args.mountpoint);
