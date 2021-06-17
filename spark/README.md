Set up a spark cluster (local or otherwise)
You can then run the scripts in src/main/scala, assuming each machine in the cluster has access to the csv files being processed.

E.g. running on local cluster:

```
$ sbt package
$ /home/tpe23/opt/spark/bin/spark-submit --class "MatchCSVFiles" --master local[*] --driver-memory 16G\
  --conf spark.local.dir=/temp/directory/for/spark\
  /your/jar/created/by/sbt_package.jar\
  "second/csv/file.csv"\
  "first/csv/file.csv"\
  "directory/for/results"\
  0 1000000000 # first packet (in file 1) to use; ignore matches with time difference bigger than x (ns) (Bad attempt at filtering
  out dublicate matches for e.g. dnsperf, where the exact same packet is sent at multiple times during the benchmark. Be very sure what you are doing when you set it.) 
