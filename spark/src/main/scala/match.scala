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


object MatchCSVFiles extends App {

  val file1 = args(0)
  val file2 = args(1)
  val ignore_before = args(3)
  val filter_diff_time = args(4)
  
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


  val joinedData = df.join(df2, $"file1.data" === $"file2.data")
                     .select($"file1.data" as "data", $"file1.len" as "len",
                             $"file1.secPs" as "secPs1", $"file1.portId" as "port1",
                             $"file2.secPs" as "secPs2", $"file2.portId" as "port2",
                             $"file2.count" as "count")
                     // To server
                     .withColumn("diff", 'secPs1.minus('secPs2))
                     .withColumn("nsDiff", 'diff.multiply(new BigDecimal(1000000000)))
                     // To client
                     //.withColumn("diff", 'secPs2.minus('secPs1))
                     .where($"nsDiff" > 300 && $"nsDiff" < 10000000)
                     .where($"count" > ignore_before)

  //val df_test1 = joinedData.select(countDistinct("data"))
  //val df_test2 = joinedData.select(count("*"))
  //df_test1.show()
  //df_test2.show()


  //joinedData.show()
  val outdir = args(2)
  //joinedData.write
  //  .format("csv")
  //  .option("header", "false")
  //  .save(outdir)
  val row = joinedData.agg(min("nsDiff") as "min", max("nsDiff") as "max",
                           avg("nsDiff") as "avg",
                           stddev_pop("nsDiff") as "stddev",
                           skewness("nsDiff") as "skew",
                           kurtosis("nsDiff") as "kurtosis").head
  val minDiff = row.getDecimal(0)
  //val minDiff = new BigDecimal(10)
  val maxDiff = row.getDecimal(1).min(new BigDecimal(filter_diff_time))

  val splits_init = (1 to 2005)
  val bigTwoHundred = new BigDecimal("2000")
  val diffMult = maxDiff.subtract(minDiff).divide(bigTwoHundred, 12, RoundingMode.HALF_UP)
  //1ns
  //val diffMult = new BigDecimal(0.25)


  //val diffSplits = splits_init.map(e => minDiff.add((new BigDecimal(e-1)).multiply(diffMult)).doubleValue()).toArray
  val diffSplits = splits_init.map(e => minDiff.add((new BigDecimal(e-1)).multiply(diffMult)).doubleValue()).toArray :+ Double.PositiveInfinity

  val diffBucketizer = new Bucketizer()
    .setInputCol("nsDiff")
    .setOutputCol("diff_bucket")
    .setSplits(diffSplits)

  val diffBucketed = diffBucketizer.transform(joinedData)
  

  val delays_bucket = diffBucketed.groupBy($"diff_bucket").agg(count($"*") as "count")
                            .withColumn("diff_bucket_val", 'diff_bucket.multiply(diffMult).plus(minDiff))
  //println(delays_bucket.count())
  //val pw = new PrintWriter(new File(outdir+"/delays.json"))
  //pw.write(delays.toJson)
  //pw.close
  delays_bucket.coalesce(1).write
    .format("csv")
    .option("header", "false")
    .save(outdir+"/delays_filtered")

  val rowS = row.mkString(",")
  new PrintWriter(outdir+"/stats.txt") { 
    write("min, max, avg, stddev, skew, kurtosis");
    write(rowS);
    close }

}
