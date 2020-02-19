# spanner-benchmarking
Benchmarking utilities for Cloud Spanner tools

- [Requirements](#requirements)
- [Results](#results)

### Requirements

To get started, you'll need

- [ ] Spanner DBAPI and Spanner_v1 installed
- [ ] [OpenCensus Agent](https://opencensus.io/agent)
    - [ ] Enable any of the metrics exporters e.g. [Prometheus](https://opencensus.io/service/exporters/prometheus/)
- [ ] OpenCensus Python and OpenCensus-Ext-Ocagent installed
- [ ] 2 Cloud Spanner Tables with the following DDL statements
```sql
CREATE TABLE for_dbapi (
    name STRING(MAX) NOT NULL,
    age INT64,
) PRIMARY KEY (name)

CREATE TABLE for_spanner_v1 (
    name STRING(MAX) NOT NULL,
    age INT64,
) PRIMARY KEY (name)
```

### Results

#### Comparing Reads

Comparing

    spanner.dbapi.cursor.execute('SELECT * from T where for_dbapi where age <= 200')

vs

    spanner_v1.Spanshot(multi_use=True).execute_sql('SELECT * from T where for_spanner_v1 where age <= 200')

by running

```shell
python3 main.py
```

and then applying some percentile aggregations:

For example, having used Prometheus as the metrics backend and apply a p95th aggregation with 
```shell
histogram_quantile(0.95, sum(rate(nz1_latency_bucket[5m])) by (service, error, le))
```

as of `Tue 18 Feb 2020 20:15:04 PST`, we get back a comparison that shows that the spanner.dbapi's
performance is worse than using spanner_v1, per

* spanner.dbapi p99th latency of 205.99999 ms
![](./assets/spanner-dbapi-p99th-SELECT.png)

* spanner_v1 p95th latency of 218.81818 ms
![](./assets/spanner-v1-p99th-SELECT.png)
