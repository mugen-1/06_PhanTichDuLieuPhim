#!/bin/bash
# Tao bang HBase va nap du lieu tu HDFS bang ImportTsv (chay MapReduce).
#   movies       rowkey = movie_id            cf info
#   ratings      rowkey = movieId_userId      cf r
#   search_index rowkey = tu khoa             cf i   (ket qua MapReduce inverted index)
# Chay: bash tao_bang_va_nap.sh           (nap movies + ratings)
#       bash tao_bang_va_nap.sh index     (nap them search_index sau khi chay MapReduce)
RAW=/user/nhom06/movies/raw
TMP=/user/nhom06/movies/hbase_in
export HBASE_CLASSPATH=$HADOOP_HOME/etc/hadoop

tao_bang() {  # $1 = ten bang, $2 = column family
  if echo "exists '$1'" | hbase shell -n 2>/dev/null | grep -q "does exist"; then
    echo "truncate '$1'" | hbase shell -n >/dev/null 2>&1 && echo "Da lam rong bang $1"
  else
    echo "create '$1', '$2'" | hbase shell -n >/dev/null 2>&1 && echo "Da tao bang $1"
  fi
}

nap() {  # $1 = cot, $2 = bang, $3 = thu muc HDFS
  hbase org.apache.hadoop.hbase.mapreduce.ImportTsv -Dimporttsv.columns="$1" "$2" "$3" 2>&1 \
    | grep -E "Job .* completed|Bad Lines|ERROR|Exception" || true
}

if [ "$1" = "index" ]; then
  tao_bang search_index i
  nap HBASE_ROW_KEY,i:ids search_index /user/nhom06/movies/out/inverted_index
else
  tao_bang movies info
  tao_bang ratings r
  nap HBASE_ROW_KEY,info:imdb_id,info:title,info:release_date,info:release_year,info:runtime,info:genres,info:language,info:budget,info:revenue,info:overview movies $RAW/movies
  # rowkey ratings = movieId_userId (ghep 2 cot truoc khi nap)
  hdfs dfs -rm -r -f -skipTrash $TMP >/dev/null 2>&1
  hdfs dfs -mkdir -p $TMP/ratings
  hdfs dfs -cat $RAW/ratings/* | awk -F'\t' -v OFS='\t' 'NF==4 {print $2"_"$1, $3, $4}' \
    | hdfs dfs -put -f - $TMP/ratings/ratings.tsv
  nap HBASE_ROW_KEY,r:rating,r:ts ratings $TMP/ratings
fi
for t in movies ratings search_index; do
  echo "count '$t'" | hbase shell -n 2>/dev/null | grep -E "row\(s\)" | sed "s/^/$t: /"
done
