#!/bin/bash
# Kafka: producer day review phim vao topic, consumer doc ra va ghi len HDFS.
# Chay tu thu muc goc repo: bash source-code/trungtruc/kafka/kafka_reviews.sh
BS=localhost:9092
TOPIC=reviews_phim
SRC=dataset/clean/reviews.tsv
OUT=/user/nhom06/movies/raw/kafka

kafka-topics.sh --bootstrap-server $BS --delete --if-exists --topic $TOPIC 2>/dev/null; sleep 5
kafka-topics.sh --bootstrap-server $BS --create --topic $TOPIC --partitions 3 --replication-factor 1
kafka-topics.sh --bootstrap-server $BS --describe --topic $TOPIC

echo "=== Producer: gui review (movie_id, author, rating, created_at)"
tail -n +2 $SRC | cut -f2-5 | kafka-console-producer.sh --bootstrap-server $BS --topic $TOPIC

echo "=== Consumer: doc tu dau topic, ghi len HDFS"
hdfs dfs -mkdir -p $OUT
kafka-console-consumer.sh --bootstrap-server $BS --topic $TOPIC --from-beginning --timeout-ms 20000 2>/dev/null \
  | hdfs dfs -put -f - $OUT/reviews_kafka.tsv

echo "Gui: $(tail -n +2 $SRC | wc -l) dong | Nhan tren HDFS: $(hdfs dfs -cat $OUT/reviews_kafka.tsv | wc -l) dong"
hdfs dfs -cat $OUT/reviews_kafka.tsv | head -3
