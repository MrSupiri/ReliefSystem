import sqlite3
import os
import logging
import sys


class Storage(object):
    def __init__(self, Database):
        self.conn = sqlite3.connect(Database)
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS "History" ( `ID` INTEGER PRIMARY KEY AUTOINCREMENT,'
                       ' `Teacher_ID` INTEGER, `Date` NUMERIC, FOREIGN KEY(`Teacher_ID`)'
                       ' REFERENCES `Teachers`(`Teacher_ID`) )')
        self.c.execute('CREATE TABLE IF NOT EXISTS "Teachers" ( `Teacher_ID` INTEGER, `Teacher_Name` TEXT,'
                       ' `Telephone_Number` INTEGER, `D1P1-C` TEXT, `D1P1-S` TEXT, `D1P2-C` TEXT, `D1P2-S` TEXT,'
                       ' `D1P3-C` TEXT, `D1P3-S` TEXT, `D1P4-C` TEXT, `D1P4-S` TEXT, `D1P5-C` TEXT, `D1P5-S` TEXT,'
                       ' `D1P6-C` TEXT, `D1P6-S` TEXT, `D1P7-C` TEXT, `D1P7-S` TEXT, `D1P8-C` TEXT, `D1P8-S` TEXT,'
                       ' `D2P1-C` TEXT, `D2P1-S` TEXT, `D2P2-C` TEXT, `D2P2-S` TEXT, `D2P3-C` TEXT, `D2P3-S` TEXT,'
                       ' `D2P4-C` TEXT, `D2P4-S` TEXT, `D2P5-C` TEXT, `D2P5-S` TEXT, `D2P6-C` TEXT, `D2P6-S` TEXT,'
                       ' `D2P7-C` TEXT, `D2P7-S` TEXT, `D2P8-C` TEXT, `D2P8-S` TEXT, `D3P1-C` TEXT, `D3P1-S` TEXT,'
                       ' `D3P2-C` TEXT, `D3P2-S` TEXT, `D3P3-C` TEXT, `D3P3-S` TEXT, `D3P4-C` TEXT, `D3P4-S` TEXT,'
                       ' `D3P5-C` TEXT, `D3P5-S` TEXT, `D3P6-C` TEXT, `D3P6-S` TEXT, `D3P7-C` TEXT, `D3P7-S` TEXT,'
                       ' `D3P8-C` TEXT, `D3P8-S` TEXT, `D4P1-C` TEXT, `D4P1-S` TEXT, `D4P2-C` TEXT, `D4P2-S` TEXT,'
                       ' `D4P3-C` TEXT, `D4P3-S` TEXT, `D4P4-C` TEXT, `D4P4-S` TEXT, `D4P5-C` TEXT, `D4P5-S` TEXT,'
                       ' `D4P6-C` TEXT, `D4P6-S` TEXT, `D4P7-C` TEXT, `D4P7-S` TEXT, `D4P8-C` TEXT, `D4P8-S` TEXT,'
                       ' `D5P1-C` TEXT, `D5P1-S` TEXT, `D5P2-C` TEXT, `D5P2-S` TEXT, `D5P3-C` TEXT, `D5P3-S` TEXT,'
                       ' `D5P4-C` TEXT, `D5P4-S` TEXT, `D5P5-C` TEXT, `D5P5-S` TEXT, `D5P6-C` TEXT, `D5P6-S` TEXT,'
                       ' `D5P7-C` TEXT, `D5P7-S` TEXT, `D5P8-C` TEXT, `D5P8-S` TEXT, PRIMARY KEY(`Teacher_ID`) )')

        self.c.execute('CREATE TABLE IF NOT EXISTS "Metadata" ( `Teacher_ID` INTEGER, `Section` TEXT, `Grade` '
                       'INTEGER, `Subject` TEXT, `Classes` TEXT, FOREIGN KEY(`Teacher_ID`) REFERENCES '
                       '`Teachers`(`Teacher_ID`) )')

    def get(self, query, *pars, readOne=False):
        LOG.log.debug("Reading Data --> {} - {}".format(query, pars))
        try:
            self.c.execute(query, pars)
            if readOne:
                return self.c.fetchone()
            else:
                return self.c.fetchall()
        except Exception as e:
            LOG.log.critical('{}, {}'.format(query, pars))
            LOG.log.exception(e)
            return str(type(e).__name__) + " : " + str(e)

    def put(self, query, *pars):
        LOG.log.debug("Writing Data --> {} - {}".format(query, pars))
        try:
            self.c.execute(query, pars)
            self.conn.commit()
        except Exception as e:
            LOG.log.critical('{}, {}'.format(query, pars))
            LOG.log.exception(e)
            return str(type(e).__name__) + " : " + str(e)


class Logger(object):
    def __init__(self):
        try:
            self.buildFailed = False

            logFormatter = logging.Formatter(
                fmt='%(asctime)-10s %(levelname)-10s: %(module)s:%(lineno)-d -  %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

            self.log = logging.getLogger()
            self.log.setLevel(logging.INFO)

            fileHandler = logging.FileHandler('data/RCGAdmin.log', 'a')
            fileHandler.setFormatter(logFormatter)
            self.log.addHandler(fileHandler)
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            self.log.addHandler(consoleHandler)
        except Exception as e:
            self.log.critical(str(type(e).__name__) + " : " + str(e))
            self.log.critical(self.getError())

    def getError(self):
        self.buildFailed = True
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error = "{} {} {}".format(exc_type, fname, exc_tb.tb_lineno)
        return error


LOG = Logger()
DB = Storage('data/database.db')
