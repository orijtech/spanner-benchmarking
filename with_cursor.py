#!/bin/env python3

import os
import time

from spanner.dbapi import connect
from common import N, clean_up_then_populate, do, register_all, tag_value_DQL, tag_value_DBAPI

def main():
    project, instance, db, table = os.environ.get('SPANNER_PROJECT', 'orijtech'), 'django', 'db1', 'for_dbapi'
    clean_up_then_populate(project, instance, db, table)

    register_all('dbapi')

    with connect(project=project, instance=instance, database=db) as conn:
        with conn.cursor() as cur:
            for i in range(N):
                do(tag_value_DQL, tag_value_DBAPI, lambda: (cur.execute('SELECT * from for_dbapi where age <= 200'), list(cur.fetchall())))
                print('%d\r' % i, end='')
                if i%100 == 0:
                    time.sleep(1.7)

    time.sleep(100)

if __name__ == '__main__':
    main()
