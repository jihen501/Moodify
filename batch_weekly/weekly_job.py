from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, expr, collect_list, size, map_from_entries
from pyspark.sql.types import TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import udf, row_number
from pyspark.sql.types import MapType, StringType, IntegerType , DoubleType


def main():
    spark = SparkSession.builder \
        .appName("WeeklyMoodAnalysisWithBreakdown") \
        .config("spark.mongodb.read.connection.uri", "mongodb://mongo:27017/moodify.recommendations") \
        .config("spark.mongodb.write.connection.uri", "mongodb://mongo:27017/moodify.weekly_reports") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")


    # Load the past week's data
    df = spark.read.format("mongodb").load()
    df = df.withColumn("timestamp", col("timestamp").cast(TimestampType()))
    df = df.filter(col("timestamp") >= expr("current_timestamp() - interval 7 days"))

    # Compute total track count and duration
    agg_base = df.groupBy("user_id") \
        .agg(
            count("*").alias("track_count"),
            sum("duration_ms").alias("total_duration_ms")
        )

    # Create mood count table per user
    mood_counts_df = df.groupBy("user_id", "mood").agg(count("*").alias("count"))

    # Pivot mood counts to map-style structure
    mood_map_df = mood_counts_df.groupBy("user_id") \
        .agg(
            collect_list(expr("struct(mood, count)")).alias("mood_counts_structs")
        ) \
        .withColumn("mood_counts", map_from_entries(col("mood_counts_structs"))) \
        .drop("mood_counts_structs")

    # Compute most common mood per user
    window = Window.partitionBy("user_id").orderBy(col("count").desc())
    mood_counts_df = mood_counts_df.withColumn("rn", row_number().over(window))
    most_common_df = mood_counts_df.filter(col("rn") == 1) \
        .select("user_id", col("mood").alias("most_common_mood"), col("count").alias("most_common_mood_count"))

    # Combine all analyses
    final = agg_base \
        .join(mood_map_df, on="user_id", how="left") \
        .join(most_common_df, on="user_id", how="left")

    final = final.withColumn("total_duration_min", col("total_duration_ms") / 60000) \
        .withColumn("mood_variety", size(col("mood_counts"))) 
    def map_long_to_int(m):
        if m is None:
            return None
        return {k: int(v) for k, v in m.items()}

    map_long_to_int_udf = udf(map_long_to_int, MapType(StringType(), IntegerType()))

    final = final.withColumn("total_duration_min", col("total_duration_ms") / 60000) \
        .withColumn("mood_variety", size(col("mood_counts"))) \
        .withColumn("mood_counts", map_long_to_int_udf(col("mood_counts"))) \
        .withColumn("track_count", col("track_count").cast(IntegerType())) \
        .withColumn("total_duration_ms", col("total_duration_ms").cast(IntegerType())) \
        .withColumn("most_common_mood_count", col("most_common_mood_count").cast(IntegerType())) \
        .withColumn("total_duration_min", col("total_duration_min").cast(DoubleType())) \
        .withColumn("mood_variety", col("mood_variety").cast(IntegerType()))

    # Save report to MongoDB
    final.write.format("mongodb") \
        .mode("append") \
        .option("database", "moodify") \
        .option("collection", "weekly_reports") \
        .save()

if __name__ == "__main__":
    main()
