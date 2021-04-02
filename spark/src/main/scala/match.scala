import org.apache.spark.sql.Row
import org.apache.spark.sql.functions.abs
import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType, DecimalType}

object MatchCSVFiles extends App {

  val file1 = args(0)
  val file2 = args(1)
  
  val spark:SparkSession = SparkSession.builder()
    .master("local[20]")
    .appName("MatchPackets")
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
  val df_filtered = df.filter($"data".substr(47, 2) === "06" || $"data".substr(47, 2) === "11") // only UDP/TCP packets
  //df.show()
  //df_filtered.show()
  val df2 = spark.read
         .format("csv")
         .option("header", "true") //first line in file has headers
         .option("mode", "DROPMALFORMED")
         .schema(customSchema)
         .load(file2).as("file2")
  val df2_filtered = df2.filter($"data".substr(47, 2) === "06" || $"data".substr(47, 2) === "11") // only UDP/TCP packets
  //df2.show()
  //df2_filtered.show()
  val joinedData = df.join(df2, $"file1.data" === $"file2.data")
                     .select($"file1.data" as "data", $"file1.len" as "len", $"file1.secPs" as "secPs1", $"file1.portId" as "port1",
                             $"file2.secPs" as "secPs2", $"file2.portId" as "port2")
                     .withColumn("diff", 'secPs1.minus('secPs2))
  val outdir = args(2)
  joinedData.write
    .format("csv")
    .option("header", "false")
    .save(outdir)

}
