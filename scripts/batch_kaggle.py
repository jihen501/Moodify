from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
def main():
    print("Starting the Advanced Kaggle Moodify Batch Job")
    spark = SparkSession.builder.appName("AdvancedKaggleMoodifyBatch").getOrCreate()
    print("Spark session created")
    # Lire les deux fichiers
    df1 = spark.read.csv("data/high_popularity_spotify_data.csv", header=True, inferSchema=True)
    df2 = spark.read.csv("data/low_popularity_spotify_data.csv", header=True, inferSchema=True)
    print("Dataframes loaded")
    # Fusionner
    df = df1.unionByName(df2)
    df.show(5)
    df.printSchema()
    # Sélection des colonnes utiles
    df = df.select(
        "track_name", "track_artist", "track_popularity",
        "valence", "energy", "danceability", "tempo", "acousticness",
        "instrumentalness", "speechiness", "liveness", "loudness"
    )

    df = df.withColumn("mood", when((col("danceability") > 0.7) & (col("energy") > 0.7), "Dance Party")
                             .when((col("valence") > 0.6) & (col("energy") > 0.5), "Happy Vibes")
                             .when((col("valence") < 0.3) & (col("energy") < 0.4), "Sad")
                             .when((col("acousticness") > 0.6) & (col("instrumentalness") > 0.5), "Chill / Instrumental")
                             .when((col("speechiness") > 0.66), "Talkative / Rap")
                             .when((col("acousticness") > 0.7) & (col("energy") < 0.4), "Calm Acoustic")
                             .when((col("loudness") > -5) & (col("energy") > 0.8), "Energetic Rock")
                             .when((col("valence").between(0.3, 0.6)) & (col("acousticness") > 0.5) & (col("energy") < 0.5), "Dreamy / Ambient")
                             .otherwise("Mixed"))

    # Afficher un échantillon
    df.select("track_name", "track_artist", "mood", "duration_ms").show(20, truncate=False)
    # Sauvegarde (optionnelle)
    df.coalesce(1).write.mode("overwrite").json("output/advanced_kaggle_tracks_by_mood.json")

    spark.stop()

if __name__ == "__main__":
    main()  