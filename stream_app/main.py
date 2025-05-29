import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, to_timestamp, lit, collect_list, struct, expr, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, ArrayType
from pyspark.sql.functions import from_unixtime
from pyspark.sql.types import IntegerType
from pyspark.sql.functions import to_json, struct


def main():
    spark = SparkSession.builder.appName(
        "StreamingMoodDetectionWithRecs")\
        .config("spark.mongodb.read.connection.uri", "mongodb://mongo:27017") \
        .config("spark.mongodb.write.connection.uri", "mongodb://mongo:27017").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Load batch data
    df_mood = spark.read.format("mongodb") \
        .option("uri", "mongodb://mongo:27017/moodify.advanced_kaggle_tracks_by_mood") \
        .option("database", "moodify") \
        .option("collection", "advanced_kaggle_tracks_by_mood") \
        .load()

    # Prepare recommendations
    mood_recs = df_mood.groupBy("mood") \
        .agg(collect_list(struct(col("track_name"), col("track_artist"))).alias("tracks")) \
        .withColumn("tracks", expr("shuffle(tracks)")) \
        .withColumn("recommendations", expr("slice(tracks, 1, 3)")) \
        .select("mood", "recommendations")

    # Streaming setup
    schema = StructType([
        StructField("user_id", StringType()),
        StructField("track_id", StringType()),
        StructField("track_name", StringType()),
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
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "spotify-stream") \
        .option("startingOffsets", "latest") \
        .load()

    df_stream = df_kafka.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json(col("json"), schema).alias("data")) \
        .select("data.*")

    # Detect mood
    df_with_mood = df_stream.withColumn("mood",
                                        when((col("danceability") > 0.7) & (
                                            col("energy") > 0.7), "Dance")
                                        .when((col("valence") > 0.6) & (col("energy") > 0.5), "Happy")
                                        .when((col("valence") < 0.3) & (col("energy") < 0.4), "Sad")
                                        .when((col("acousticness") > 0.6) & (col("instrumentalness") > 0.5), "Chill")
                                        .when((col("speechiness") > 0.66), "Rap")
                                        .when((col("acousticness") > 0.7) & (col("energy") < 0.4), "Calm")
                                        .when((col("valence").between(0.3, 0.6)) & (col("acousticness") > 0.5) & (col("energy") < 0.5), "Dreamy")
                                        .otherwise("Mixed"))

    df_with_mood = df_with_mood.withColumn(
        "timestamp", from_unixtime(col("timestamp").cast("long"))
    )

    # Join with recommendations
    df_with_recs = df_with_mood.join(mood_recs, "mood", "left")

    # Fixed selection
    df_mongo = df_with_recs.select(
        "user_id",
        "track_id",
        "track_name",  # <-- REMOVE THIS LINE if present!
        col("duration_ms").cast(IntegerType()).alias("duration_ms"),
        "mood",
        "recommendations",
        "timestamp"
    )

    query = df_mongo.writeStream \
        .format("mongodb") \
        .option("uri", "mongodb://mongo:27017") \
        .option("database", "moodify") \
        .option("collection", "recommendations") \
        .option("checkpointLocation", "checkpoint/streaming_mongo") \
        .outputMode("append") \
        .trigger(processingTime="15 seconds") \
        .start()

    df_kafka_out = df_with_recs.select(
        col("user_id").alias("key"),  # optional: use user_id as key
        to_json(struct(
            "user_id",
            "track_id",
            "track_name",
            col("duration_ms").cast(IntegerType()),
            "mood",
            "recommendations",
            "timestamp"
        )).alias("value")
    )

    kafka_query = df_kafka_out.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "moodify-updates") \
        .option("checkpointLocation", "checkpoint/streaming_kafka") \
        .outputMode("append") \
        .trigger(processingTime="15 seconds") \
        .start()

    query.awaitTermination()
    kafka_query.awaitTermination()


if __name__ == "__main__":
    main()
