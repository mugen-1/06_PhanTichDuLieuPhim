# CRUD mau tren HBase. Chay: hbase shell -n crud_mau.rb
# CREATE
put 'movies', '999002', 'info:title', 'Phim Demo HBase'
put 'movies', '999002', 'info:genres', 'Drama'
put 'movies', '999002', 'info:release_year', '2025'
# READ
get 'movies', '999002'
# UPDATE
put 'movies', '999002', 'info:title', 'Phim Demo HBase (da sua)'
get 'movies', '999002', 'info:title'
# DELETE
deleteall 'movies', '999002'
get 'movies', '999002'
# Doc danh gia cua phim 1001 nho rowkey movieId_userId
scan 'ratings', {ROWPREFIXFILTER => '1001_', LIMIT => 5}
scan 'movies', {LIMIT => 3, COLUMNS => ['info:title', 'info:release_year']}
exit
