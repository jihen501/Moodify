from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, expr, collect_list, size, map_from_entries
from pyspark.sql.types import TimestampType

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
    most_common_df = mood_counts_df.groupBy("user_id") \
        .agg(expr("first(mood) keep (dense_rank first order by count desc)").alias("most_common_mood"),
             expr("max(count)").alias("most_common_mood_count"))

    # Combine all analyses
    final = agg_base \
        .join(mood_map_df, on="user_id", how="left") \
        .join(most_common_df, on="user_id", how="left")

    final = final.withColumn("total_duration_min", col("total_duration_ms") / 60000) \
        .withColumn("mood_variety", size(col("mood_counts"))) \
        .withColumn("dominance_ratio", col("most_common_mood_count") / col("track_count"))

    # Save report to MongoDB
    final.write.format("mongodb") \
        .mode("append") \
        .option("database", "moodify") \
        .option("collection", "weekly_reports") \
        .save()

if __name__ == "__main__":
    main()
