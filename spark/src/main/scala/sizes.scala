
import java.math.BigDecimal;
import java.math.RoundingMode;

import org.apache.spark.ml.feature._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql._
import org.apache.spark.sql.expressions._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.functions.{abs, count, min, max}
import org.apache.spark.sql.Row
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType, DecimalType}


object Sizes extends App {
  println("aaaaaaaaaaaaaaa")
  val file1 = args(0)
  //val file2 = args(1)
  //outdir: args(1)
  val ignore_before = args(2).toInt
  val last_packet = args(3).toInt
  //val filter_diff_time = args(5).toDouble

  val spark:SparkSession = SparkSession.builder()
    .master("local[*]")
    .appName("MatchPackets")
    .config("spark.driver.memory", "16g")
    .config("spark.local.dir", "/local/scratch/tpe23/spark-temp")
    .getOrCreate()

  import spark.implicits._

  spark.sparkContext.setLogLevel("ERROR")

  val customSchema = StructType(Array(
    StructField("count", IntegerType, true),
    //StructField("timedeltaNs", StringType, true),
    //StructField("secNs", DecimalType(25,10), true),
    StructField("caplen", IntegerType, true),
    StructField("len", IntegerType, true),
    StructField("devId", IntegerType, true),
    StructField("portId", IntegerType, true),
    StructField("secPs", DecimalType(25,13), true),
    StructField("data", StringType, true)))


  val df = spark.read
         .format("csv")
         .option("header", "true") //first line in file has headers
         .option("mode", "DROPMALFORMED")
         .schema(customSchema)
         .load(file1).as("file1")
         .filter($"data".substr(47, 2) === "06" || $"data".substr(47, 2) === "11") // only UDP/TCP packets
         .filter($"data".substr(53, 8) === "c0a80008" || $"data".substr(53, 8) === "c0a8000b" ||
                 $"data".substr(61, 8) === "c0a80008" || $"data".substr(61, 8) === "c0a8000b") // packets to or from nf08 or quorum301
         .filter($"count" > ignore_before && $"count" < last_packet)


  //joinedData.show()
  val outdir = args(1)

  val windowSpec = Window.orderBy("count")

  val sizes_dir0 = df.filter($"portId" === 0)
		     .select($"len")
 
  val sizes_dir1 = df.filter($"portId" === 1)
                     .select($"len")
  
  
  val splits_init = (1 to 2000)
  
  val splits = splits_init.map(e => e.doubleValue()).toArray

  val bucketizer = new Bucketizer()
    .setInputCol("len")
    .setOutputCol("bucket")
    .setSplits(splits)

  val bucketed0 = bucketizer.transform(sizes_dir0)
  val bucketed1 = bucketizer.transform(sizes_dir1)

  val sizes_bucket0 = bucketed0.groupBy($"bucket").agg(count($"*") as "count")
                            .withColumn("bucket_val", 'bucket.plus(1))
  
  val sizes_bucket1 = bucketed1.groupBy($"bucket").agg(count($"*") as "count")
                            .withColumn("bucket_val", 'bucket.plus(1))
  
  sizes_bucket0.coalesce(1).write
    .format("csv")
    .option("header", "false")
    .save(outdir+"/sizes_port0")

  sizes_bucket1.coalesce(1).write
    .format("csv")
    .option("header", "false")
    .save(outdir+"/sizes_port1")
}
