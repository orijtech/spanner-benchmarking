# spanner-benchmarking
Benchmarking utilities for Cloud Spanner tools

### To get started, you'll need

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
