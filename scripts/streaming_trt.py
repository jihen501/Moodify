from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, to_timestamp, lit, collect_list, struct, expr,from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, ArrayType

def main():
    spark = SparkSession.builder.appName("StreamingMoodDetectionWithRecs").getOrCreate()
    spark.sparkContext.setLogLevel("INFO")

    # Load the batch-processed mood data for recommendations
    df_mood = spark.read.json("output/advanced_kaggle_tracks_by_mood.json")
    df_mood = df_mood.cache()

    # Prepare recommendations - collect all tracks by mood
    mood_recs = df_mood.groupBy("mood") \
        .agg(collect_list(struct("track_name", "track_artist")).alias("tracks")) \
        .withColumn("recommendations", expr("slice(tracks, 1, 3)")).select("mood", "recommendations")

    # Define the schema for the streaming data
    schema = StructType([
        StructField("user_id", StringType()),
        StructField("track_id", StringType()),
        StructField("valence", DoubleType()),
        StructField("energy", DoubleType()),
        StructField("danceability", DoubleType()),
        StructField("acousticness", DoubleType()),
        StructField("instrumentalness", DoubleType()),
        StructField("speechiness", DoubleType()),
        StructField("duration_ms", LongType()),
        StructField("timestamp", StringType())
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "spotify-stream") \
        .option("startingOffsets", "latest") \
        .load()



    df_stream = df_kafka.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json(col("json"), schema).alias("data")) \
        .select("data.*")


    # Detect mood for each incoming track
    df_with_mood = df_stream.withColumn("mood",
        when((col("danceability") > 0.7) & (col("energy") > 0.7), "Dance Party")
        .when((col("valence") > 0.6) & (col("energy") > 0.5), "Happy Vibes")
        .when((col("valence") < 0.3) & (col("energy") < 0.4), "Sad")
        .when((col("acousticness") > 0.6) & (col("instrumentalness") > 0.5), "Chill / Instrumental")
        .when((col("speechiness") > 0.66), "Talkative / Rap")
        .when((col("acousticness") > 0.7) & (col("energy") < 0.4), "Calm Acoustic")
        .when((col("valence").between(0.3, 0.6)) & (col("acousticness") > 0.5) & (col("energy") < 0.5), "Dreamy / Ambient")
        .otherwise("Mixed"))

    # Convert timestamp and set watermark
    df_with_mood = df_with_mood.withColumn("timestamp", to_timestamp(col("timestamp")))
    df_with_mood = df_with_mood.withWatermark("timestamp", "10 minutes")

    # Join with pre-prepared recommendations
    df_with_recs = df_with_mood.join(mood_recs, "mood", "left")

    # Write the output with exactly 3 recommendations per track
    # query = df_with_recs.writeStream \
    #     .format("json") \
    #     .option("path", "output/stream_output_with_recs/") \
    #     .option("checkpointLocation", "checkpoint/streaming_moodify_with_recs") \
    #     .outputMode("append") \
    #     .trigger(processingTime="15 seconds") \
    #     .start()
    df_mongo = df_with_recs.select(

    "user_id",
    "track_id",
    "track_name",
    "mood",
    col("recommendations.track_name").alias("recommended_track_names"),
    col("recommendations.track_artist").alias("recommended_track_artists"),
    "timestamp")

    query = df_mongo.writeStream \
        .format("mongodb") \
        .option("spark.mongodb.connection.uri", "mongodb://localhost:27017") \
        .option("spark.mongodb.database", "moodify") \
        .option("spark.mongodb.collection", "recommendations") \
        .option("checkpointLocation", "checkpoint/streaming_mongo") \
        .outputMode("append") \
        .trigger(processingTime="15 seconds") \
        .start()
    query.awaitTermination()

if __name__ == "__main__":
    main()