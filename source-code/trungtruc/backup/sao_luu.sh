#!/bin/bash
# Sao luu: HDFS snapshot thu muc du lieu + HBase snapshot 2 bang
TEN=${1:-snap_2026_bigdata}
DIR=/user/nhom06/movies
hdfs dfsadmin -allowSnapshot $DIR
hdfs dfs -createSnapshot $DIR $TEN
echo "--- HDFS snapshot:"; hdfs dfs -ls $DIR/.snapshot
for t in movies ratings; do
  echo "snapshot '$t', '${t}_$TEN'" | hbase shell -n >/dev/null 2>&1
done
echo "--- HBase snapshot:"; echo "list_snapshots" | hbase shell -n 2>/dev/null | grep "$TEN"
