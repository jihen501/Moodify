from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col


def main():
    print("Starting the Advanced Kaggle Moodify Batch Job")

    spark = SparkSession.builder \
        .appName("AdvancedKaggleMoodifyBatch") \
        .config("spark.mongodb.output.uri", "mongodb://mongo:27017/moodify.tracks_by_mood") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    print("Spark session created")

    # Lecture CSV combiné
    df = spark.read.csv("data/combined_spotify_data.csv",
                        header=True, inferSchema=True)

    # Sélection des colonnes utiles
    df = df.select(
        "track_name", "track_artist", "track_popularity",
        "valence", "energy", "danceability", "tempo", "acousticness",
        "instrumentalness", "speechiness", "liveness", "loudness", "duration_ms"
    )

    # Détection de l'humeur
    df = df.withColumn("mood", when((col("danceability") > 0.7) & (col("energy") > 0.7), "Dance Party")
                       .when((col("valence") > 0.6) & (col("energy") > 0.5), "Happy Vibes")
                       .when((col("valence") < 0.3) & (col("energy") < 0.4), "Sad")
                       .when((col("acousticness") > 0.6) & (col("instrumentalness") > 0.5), "Chill / Instrumental")
                       .when((col("speechiness") > 0.66), "Talkative / Rap")
                       .when((col("acousticness") > 0.7) & (col("energy") < 0.4), "Calm Acoustic")
                       .when((col("loudness") > -5) & (col("energy") > 0.8), "Energetic Rock")
                       .when((col("valence").between(0.3, 0.6)) & (col("acousticness") > 0.5) & (col("energy") < 0.5), "Dreamy / Ambient")
                       .otherwise("Mixed"))

    # Affichage d'un échantillon
    df.select("track_name", "track_artist", "mood",
              "duration_ms").show(20, truncate=False)

    # Sauvegarde locale JSON
    df.coalesce(1).write.mode("overwrite").json(
        "output/advanced_kaggle_tracks_by_mood.json")

    # Sauvegarde dans MongoDB
    df.write \
        .format("mongodb") \
        .option("spark.mongodb.connection.uri", "mongodb://mongo:27017") \
        .option("spark.mongodb.database", "moodify") \
        .option("spark.mongodb.collection", "advanced_kaggle_tracks_by_mood") \
        .mode("overwrite") \
        .save()

    spark.stop()


if __name__ == "__main__":
    main()
