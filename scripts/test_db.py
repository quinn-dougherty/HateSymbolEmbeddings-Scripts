#!/usr/bin/env python

import sqlite3
import os

DB_FILE = 'adlproj_db.sqlite3'
if __name__=='__main__':
    assert os.path.exists(DB_FILE)

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        x = c.execute('SELECT img_id, label, jpg_path FROM pictures LIMIT 20')

    print(x.fetchall())
