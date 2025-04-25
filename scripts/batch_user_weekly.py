from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum as spark_sum, count, round

def main():
    spark = SparkSession.builder.appName("UserWeeklyMoodStats").getOrCreate()

    # 🔹 Lire le JSON utilisateur contenant déjà mood + duration_ms
    df = spark.read.json("data/user_week_log.json")

    # 🔹 Ajouter une colonne 'date' pour éventuel filtrage ou regroupement
    df = df.withColumn("date", to_date("timestamp"))

    # 🔹 Calculs : nombre de morceaux + temps total en minutes par user et mood
    stats = df.groupBy("user_id", "mood").agg(
        count("*").alias("number_of_tracks"),
        round(spark_sum("duration_ms") / 60000, 2).alias("total_minutes_listened")
    ).orderBy("user_id", "number_of_tracks", ascending=False)

    stats.show(truncate=False)


    stats.write.mode("overwrite").json("output/user_weekly_mood_stats.json")

    spark.stop()

if __name__ == "__main__":
    main()
