import pandas as pd

# Charger les deux fichiers CSV
low_popularity = pd.read_csv('data/low_popularity_spotify_data.csv')
high_popularity = pd.read_csv('data/high_popularity_spotify_data.csv')

# Combiner les deux DataFrames
combined_data = pd.concat([low_popularity, high_popularity], ignore_index=True)

# Sauvegarder le résultat combiné dans un nouveau fichier CSV
combined_data.to_csv('data/combined_spotify_data.csv', index=False)

print("Les données ont été combinées avec succès !")
