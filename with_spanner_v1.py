#!/bin/env python3

import os
import time

from google.cloud import spanner_v1
from opencensus.ext.ocagent import stats_exporter
from common import N, clean_up_then_populate, do, register_all, tag_value_DQL, tag_value_SPANNER_V1

def main():
    project, instance, db, table = os.environ.get('SPANNER_PROJECT', 'orijtech'), 'django', 'db1', 'for_spanner_v1'
    clean_up_then_populate(project, instance, db, table)

    register_all('spannerv1')

    db = spanner_v1.Client(project=project).instance(instance).database(db)
        
    with db.snapshot(multi_use=True) as snapshot:
        for i in range(N):
            do(tag_value_DQL, tag_value_SPANNER_V1, lambda: list(snapshot.execute_sql('SELECT * from for_spanner_v1 where age <= 200')))
            print('%d\r' % i, end='')
            if i%100 == 0:
                time.sleep(1.7)

    time.sleep(100)

if __name__ == '__main__':
    main()
