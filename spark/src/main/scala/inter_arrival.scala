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


object CalculateIAT extends App {
  println("aaaaaaaaaaaaaaa")
  val file1 = args(0)
  val file2 = args(1)
  //outdir: args(2)
  val ignore_before = args(3).toInt
  val last_packet = args(4).toInt
  val filter_diff_time = args(5).toDouble

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
         .filter($"count" > ignore_before)


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
                     // To client
                     //.withColumn("diff", 'secPs2.minus('secPs1))
                     .where($"diff" > 0 && $"diff" < 1)
                     .where($"count" > ignore_before)

  //joinedData.show()
  val outdir = args(2)

  val windowSpec = Window.orderBy("count")

  var df_diffs = df.filter($"portId" === 0)
                 .withColumn("diff_time_with_prev", ($"secPs" - when((lag("secPs", 1).over(windowSpec)).isNull, 0)
                                                                          .otherwise(lag("secPs", 1).over(windowSpec)) )
                                                       .multiply(new BigDecimal(1000000000))
                                                       .minus(  when((lag("len", 1).over(windowSpec)).isNull, 0)
                                                                .otherwise(lag("len", 1).over(windowSpec))
                                                                .plus(20).divide(1.25).cast(new DecimalType(10,5)) )    )
                 .where($"count"> ignore_before + 2 && $"count" < last_packet)
  
  //df_diffs = df_diffs.withColumn("diff_time_with_prev", 'diff_time_with_prev_ps.multiply(new BigDecimal(1000000000)).minus( $"len".plus(20).divide(1.25).cast(new DecimalType(10,5)) ) )
                     //.where($"diff_time_with_prev" < filter_diff_time && $"diff_time_with_prev" > 0)
   
  //if (args(6) == "client") {
  //   df_diffs = joinedData //.filter($"port1" === 0)
  //               .withColumn("diff_time_with_prev", $"secPs2" - when((lag("secPs2", 1).over(windowSpec)).isNull, 0)
  //                                                                        .otherwise(lag("secPs2", 1).over(windowSpec)))
  //               .where($"count"> ignore_before + 2 && $"count" < last_packet && $"diff_time_with_prev" < filter_diff_time)
  //}

  val row = df_diffs.agg(min("diff_time_with_prev") as "min", max("diff_time_with_prev") as "max").head
  val minValue = row.getDecimal(0)
  val maxValue = row.getDecimal(1).min(new BigDecimal(filter_diff_time))
  
  df_diffs.show()
  println(row.mkString(","))
  val splits_init = (1 to 2000)
  val bigTwoHundred = new BigDecimal(1950)
  val mult = maxValue.subtract(minValue).divide(bigTwoHundred, 12, RoundingMode.HALF_UP)

  val splits = splits_init.map(e => minValue.add((new BigDecimal(e-1)).multiply(mult)).doubleValue()).toArray :+ Double.PositiveInfinity

  val bucketizer = new Bucketizer()
    .setInputCol("diff_time_with_prev")
    .setOutputCol("bucket")
    .setSplits(splits)

  val bucketed = bucketizer.transform(df_diffs)

  val delays_bucket = bucketed.groupBy($"bucket").agg(count($"*") as "count")
                            .withColumn("bucket_val", 'bucket.multiply(mult).plus(minValue))
  
  delays_bucket.coalesce(1).write
    .format("csv")
    .option("header", "false")
    .save(outdir+"/ipg")
}
