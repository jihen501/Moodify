from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col, from_unixtime, to_timestamp

def main():
    spark = SparkSession.builder.appName("StreamingMoodDetection").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # Lecture streaming depuis un dossier (dépôt de fichiers JSON)
    df_stream = spark.readStream.schema(
        "user_id STRING, track_id STRING, valence DOUBLE, energy DOUBLE, danceability DOUBLE, acousticness DOUBLE, instrumentalness DOUBLE, speechiness DOUBLE, duration_ms LONG, timestamp STRING"
    ).json("data/streaming_input/")

    # Traitement mood
    df_with_mood = df_stream.withColumn("mood", when((col("danceability") > 0.7) & (col("energy") > 0.7), "Dance Party")
                                                  .when((col("valence") > 0.6) & (col("energy") > 0.5), "Happy Vibes")
                                                  .when((col("valence") < 0.3) & (col("energy") < 0.4), "Sad")
                                                  .when((col("acousticness") > 0.6) & (col("instrumentalness") > 0.5), "Chill / Instrumental")
                                                  .when((col("speechiness") > 0.66), "Talkative / Rap")
                                                  .when((col("acousticness") > 0.7) & (col("energy") < 0.4), "Calm Acoustic")
                                                  .when((col("valence").between(0.3, 0.6)) & (col("acousticness") > 0.5) & (col("energy") < 0.5), "Dreamy / Ambient")
                                                  .otherwise("Mixed"))

    # Conversion du timestamp
    df_final = df_with_mood.withColumn("timestamp", to_timestamp(col("timestamp")))

    # Sauvegarde en JSON (peut être PostgreSQL, MongoDB plus tard)
    query = df_final.writeStream \
        .format("json") \
        .option("path", "output/stream_output/") \
        .option("checkpointLocation", "checkpoint/streaming_moodify") \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
