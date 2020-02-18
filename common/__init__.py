#!/bin/env python3

import time

from google.cloud import spanner_v1

from opencensus.ext.ocagent import (
    stats_exporter,
    trace_exporter,
)
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_key as tag_key_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module

# Create the measures
# The latency in milliseconds
m_latency_ms = measure_module.MeasureFloat("spanner/latency", "The latency in milliseconds per method", "ms")
# The stats recorder
stats_recorder = stats_module.stats.stats_recorder

key_method = tag_key_module.TagKey("method")
key_status = tag_key_module.TagKey("status")
key_error  = tag_key_module.TagKey("error")
key_service = tag_key_module.TagKey("service")
status_OK = tag_value_module.TagValue("OK")
status_ERROR = tag_value_module.TagValue("ERROR")

tag_value_DDL = tag_value_module.TagValue("DDL")
tag_value_DML = tag_value_module.TagValue("DML")
tag_value_DQL = tag_value_module.TagValue("DQL")
tag_value_SPANNER_V1 = tag_value_module.TagValue("spanner_v1")
tag_value_DBAPI = tag_value_module.TagValue("spanner_dbapi")

N = 10000000
n_rows = 5000

def clean_up_then_populate(project, instance, db, table):
    db = spanner_v1.Client(project=project).instance(instance).database(db)
    sess = db.session()
    if not sess.exists():
        sess.create()

    try:
        with sess.transaction() as txn:
            # Purge it.
            res = txn.execute_sql('DELETE from %s WHERE 1=1' % table)
            _ = list(res)

        with sess.transaction() as txn:
            # Now populate it.
            txn.insert(table, columns=['name', 'age'], values=[('px%d' % i, i,) for i in range(n_rows)])
    finally:
        sess.delete()


def registerAllViews(vmgr):
    latency_view = view_module.View("latency", "The distribution of the latencies",
        [key_method, key_status, key_error, key_service],
        m_latency_ms,
        # Latency in buckets:
        # [>=0ms, >=25ms, >=50ms, >=75ms, >=100ms, >=200ms, >=400ms, >=600ms, >=800ms, >=1s, >=2s, >=4s, >=6s]
        aggregation_module.DistributionAggregation([1, 25, 50, 75, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000]))
    vmgr.register_view(latency_view)

def do(tag_method_value, tag_service_value, fn, *args, **kwargs):
    start = time.time()
    mm = stats_recorder.new_measurement_map()

    err = ''

    try:
        return fn(*args, **kwargs)
    except Exception as e:
        status_value = status_ERROR
        err = '%s' % e
    finally:
        tm = tag_map_module.TagMap()
        tm.insert(key_method, tag_method_value)
        tm.insert(key_service, tag_service_value)

        if not err:
            tm.insert(key_status, status_OK)
        else:
            tm.insert(key_error, err)
            tm.insert(key_status, status_ERROR)

        mm.measure_float_put(m_latency_ms, (time.time() - start) * 1000.0)
        mm.record(tm)

def register_all(service_name):
    view_manager = stats_module.stats.view_manager
    view_manager.register_exporter(
        stats_exporter.new_stats_exporter(
            service_name=service_name,
            endpoint='localhost:55678',
            interval=5))
    registerAllViews(view_manager)
