#!/bin/env python3

import os
import time

from common import N, clean_up_then_populate, do, register_all, tag_value_DQL, tag_value_DBAPI, tag_value_SPANNER_V1
from google.cloud import spanner_v1
from opencensus.ext.ocagent import stats_exporter
from spanner.dbapi import connect

def main():
    project, instance, database = os.environ.get('SPANNER_PROJECT', 'orijtech'), 'django', 'db1'
    table_for_spanner, table_for_dbapi = 'for_spanner_v1', 'for_dbapi'
    clean_up_then_populate(project, instance, database, table_for_spanner)
    clean_up_then_populate(project, instance, database, table_for_dbapi)

    register_all('spanner_benchmarking')

    conn = connect(project=project, instance=instance, database=database)
    cur = conn.cursor()

    db = spanner_v1.Client(project=project).instance(instance).database(database)

    try:
        with db.snapshot(multi_use=True) as snapshot:
            for i in range(N):
                do(tag_value_DQL, tag_value_SPANNER_V1, lambda: list(snapshot.execute_sql('SELECT * from for_spanner_v1 where age <= 200')))
                do(tag_value_DQL, tag_value_DBAPI, lambda: (cur.execute('SELECT * from for_dbapi where age <= 200'), list(cur.fetchall())))
                print('%d\r' % i, end='')
                if i>0 and (i%100 == 0):
                    time.sleep(3.7)

    finally:
        cur.close()
        conn.close()
        time.sleep(100)

if __name__ == '__main__':
    main()
