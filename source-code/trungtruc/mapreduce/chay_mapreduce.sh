#!/bin/bash
# Chay 2 chuong trinh MapReduce (Hadoop Streaming + Python)
DIR=$(cd "$(dirname "$0")" && pwd)
STREAM=$(ls $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar | head -1)
RAW=/user/nhom06/movies/raw
OUT=/user/nhom06/movies/out

hdfs dfs -rm -r -f -skipTrash $OUT/inverted_index $OUT/join_tmdb_imdb >/dev/null 2>&1

echo "=== MR1: Inverted index ten phim + overview"
hadoop jar $STREAM \
  -files $DIR/inverted_index_mapper.py,$DIR/inverted_index_reducer.py \
  -mapper "python3 inverted_index_mapper.py" -reducer "python3 inverted_index_reducer.py" \
  -input $RAW/movies -output $OUT/inverted_index 2>&1 | grep -E "completed successfully|ERROR|Error"

echo "=== MR2: Join TMDB voi IMDb theo imdb_id"
hadoop jar $STREAM \
  -files $DIR/join_mapper.py,$DIR/join_reducer.py \
  -mapper "python3 join_mapper.py" -reducer "python3 join_reducer.py" \
  -input $RAW/movies -input $RAW/imdb -output $OUT/join_tmdb_imdb 2>&1 | grep -E "completed successfully|ERROR|Error"

echo "=== Ket qua:"
echo "inverted_index: $(hdfs dfs -cat $OUT/inverted_index/part-* | wc -l) tu khoa"
echo "join_tmdb_imdb: $(hdfs dfs -cat $OUT/join_tmdb_imdb/part-* | wc -l) phim ghep duoc"
hdfs dfs -cat $OUT/join_tmdb_imdb/part-* | head -3
