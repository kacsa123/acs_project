import java.math.BigDecimal;
import java.math.RoundingMode;
import java.io.PrintWriter;

import org.apache.spark.ml.feature._
import org.apache.spark.rdd.RDD
import org.apache.spark.sql._
import org.apache.spark.sql.expressions._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.functions.{abs, count, min, max}
import org.apache.spark.sql.Row
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType, DecimalType}


object MatchCSVFilesAll extends App {

  val file1 = args(0)
  val file2 = args(1)
  val file3 = args(2)
  // outdir: args(3)
  val ignore_before = args(4)
  
  val spark:SparkSession = SparkSession.builder()
    .master("local[*]")
    .appName("MatchPackets")
    .config("spark.driver.memory", "16g")
    .config("spark.local.dir", "/local/scratch/tpe23/spark-temp")
    .getOrCreate()
  
  import spark.implicits._

  spark.sparkContext.setLogLevel("ERROR")

  val customSchema = StructType(Array(
    StructField("count", StringType, true),
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

  val df2 = spark.read
         .format("csv")
         .option("header", "true") //first line in file has headers
         .option("mode", "DROPMALFORMED")
         .schema(customSchema)
         .load(file2).as("file2")
         .filter($"data".substr(47, 2) === "06" || $"data".substr(47, 2) === "11") // only UDP/TCP packets

  val df3 = spark.read
         .format("csv")
         .option("header", "true") //first line in file has headers
         .option("mode", "DROPMALFORMED")
         .schema(customSchema)
         .load(file3).as("file3")
         .filter($"data".substr(47, 2) === "06" || $"data".substr(47, 2) === "11") // only UDP/TCP packets


  val joinedData = df.join(df2, $"file1.data" === $"file2.data")
                     .select($"file1.data" as "data", $"file1.len" as "len",
                             $"file1.secPs" as "secPs1", $"file1.portId" as "port1",
                             $"file2.secPs" as "secPs2", $"file2.portId" as "port2")
                     // To server
                     .withColumn("diff", 'secPs1.minus('secPs2))
                     .withColumn("nsDiff", 'diff.multiply(new BigDecimal(1000000000)))
                     // To client
                     //.withColumn("diff", 'secPs2.minus('secPs1))
                     .where($"nsDiff" > 300 && $"nsDiff" < 10000000)
                     .as("join1")
                     .join(df3, $"join1.data" === $"file3.data")
                     .select($"join1.data" as "data", $"join1.len" as "len",
                             $"join1.secPs1" as "secPs1", $"join1.port1" as "port1",
                             $"join1.secPs2" as "secPs2", $"join1.port2" as "port2",
                             $"file3.secPs" as "secPs3", $"file3.portId" as "port3",
                             $"join1.nsDiff" as "nsDiff2",
                             $"file3.count" as "count")
                     .withColumn("diff1", 'secPs2.minus('secPs3))
                     .withColumn("diffAll", 'secPs1.minus('secPs3))
                     .withColumn("nsDiff1", 'diff1.multiply(new BigDecimal(1000000000)))
                     .withColumn("nsDiffAll", 'diffAll.multiply(new BigDecimal(1000000000)))
                     .where($"count" > ignore_before)
 
  //joinedData.show()
  val outdir = args(3)
  

  val row = joinedData.agg(min("nsDiff1") as "min", max("nsDiff1") as "max",
                           avg("nsDiff1") as "avg",
                           stddev_pop("nsDiff1") as "stddev",
                           skewness("nsDiff1") as "skew",
                           kurtosis("nsDiff1") as "kurtosis").head
  val minDiff1 = row.getDecimal(0)
  
  val maxDiff1 = row.getDecimal(1)

  val splits_init = (1 to 505)
  val bigTwoHundred = new BigDecimal("500")
  val diffMult1 = maxDiff1.subtract(minDiff1).divide(bigTwoHundred, 12, RoundingMode.HALF_UP)

  val diffSplits = splits_init.map(e => minDiff1.add((new BigDecimal(e-1)).multiply(diffMult1)).doubleValue()).toArray

  val diffBucketizer = new Bucketizer()
    .setInputCol("nsDiff1")
    .setOutputCol("diff_bucket1")
    .setSplits(diffSplits)

  val diffBucketed = diffBucketizer.transform(joinedData)
  

  val row2 = joinedData.agg(min("nsDiff2") as "min", max("nsDiff2") as "max",
                           avg("nsDiff2") as "avg",
                           stddev_pop("nsDiff2") as "stddev",
                           skewness("nsDiff2") as "skew",
                           kurtosis("nsDiff2") as "kurtosis").head
  val minDiff2 = row2.getDecimal(0)
  
  val maxDiff2 = row2.getDecimal(1)
  
  val diffMult2 = maxDiff2.subtract(minDiff2).divide(bigTwoHundred, 12, RoundingMode.HALF_UP)
  
  val diffSplits2 = splits_init.map(e => minDiff2.add((new BigDecimal(e-1)).multiply(diffMult2)).doubleValue()).toArray

  val diffBucketizer2 = new Bucketizer()
    .setInputCol("nsDiff2")
    .setOutputCol("diff_bucket2")
    .setSplits(diffSplits2)

  val diffBucketed2 = diffBucketizer2.transform(diffBucketed)

  val delays_bucket = diffBucketed2.groupBy($"diff_bucket1", $"diff_bucket2").agg(count($"*") as "count")
                            .withColumn("diff_bucket1_val", 'diff_bucket1.multiply(diffMult1).plus(minDiff1))
                            .withColumn("diff_bucket2_val", 'diff_bucket2.multiply(diffMult2).plus(minDiff2))


  /*val row = joinedData.agg(min("nsDiffAll") as "min", max("nsDiffAll") as "max").head
  val minDiff1 = row.getDecimal(0)

  val maxDiff1 = row.getDecimal(1)

  val splits_init = (1 to 505)
  val bigTwoHundred = new BigDecimal("500")
  val diffMult1 = maxDiff1.subtract(minDiff1).divide(bigTwoHundred, 12, RoundingMode.HALF_UP)

  val diffSplits = splits_init.map(e => minDiff1.add((new BigDecimal(e-1)).multiply(diffMult1)).doubleValue()).toArray

  val diffBucketizer = new Bucketizer()
    .setInputCol("nsDiffAll")
    .setOutputCol("diff_bucket")
    .setSplits(diffSplits)

  val diffBucketed = diffBucketizer.transform(joinedData)
  val delays_bucket = diffBucketed.groupBy($"diff_bucket").agg(count($"*") as "count")
                            .withColumn("diff_bucket_val", 'diff_bucket.multiply(diffMult1).plus(minDiff1))

*/

  delays_bucket.coalesce(1).write
    .format("csv")
    .option("header", "false")
    .save(outdir+"/delays_all")

  val rowS = row.mkString(",")
  val row2S = row2.mkString(",")
  new PrintWriter(outdir+"/all_match_stats.txt") { 
    write("min, max, avg, stddev, skew, kurtosis\n");
    write(rowS+"\n");
    write(row2S+"\n");
    close }

}
