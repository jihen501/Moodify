const Statistique = () => {
  const weeklySongs = [
    {
      title: "Sunflower",
      artist: "Post Malone",
      duration: "3:30",
      mood: "Happy",
    },
    {
      title: "Someone Like You",
      artist: "Adele",
      duration: "4:45",
      mood: "Sad",
    },
    {
      title: "Stayin’ Alive",
      artist: "Bee Gees",
      duration: "3:57",
      mood: "Energetic",
    },
    {
      title: "Shape of You",
      artist: "Ed Sheeran",
      duration: "3:53",
      mood: "Happy",
    },
    {
      title: "Lose Yourself",
      artist: "Eminem",
      duration: "5:20",
      mood: "Energetic",
    },
    {
      title: "Someone You Loved",
      artist: "Lewis Capaldi",
      duration: "3:02",
      mood: "Sad",
    },
    {
      title: "Rolling in the Deep",
      artist: "Adele",
      duration: "3:48",
      mood: "Sad",
    },
    {
      title: "Uptown Funk",
      artist: "Mark Ronson ft. Bruno Mars",
      duration: "4:30",
      mood: "Energetic",
    },
  ];

  const moodStats = [
    { mood: "Happy", duration: 80, color: "bg-yellow-400" },
    { mood: "Sad", duration: 45, color: "bg-blue-400" },
    { mood: "Energetic", duration: 65, color: "bg-red-400" },
    
  ];

  const totalDuration = moodStats.reduce((acc, m) => acc + m.duration, 0);

  const moodRecommendations = {
    Happy: ["Blinding Lights – The Weeknd", "Good as Hell – Lizzo"],
    Sad: ["Let Her Go – Passenger", "Skinny Love – Bon Iver"],
    Energetic: ["Can’t Hold Us – Macklemore", "Levitating – Dua Lipa"],
  };

  return (
    <div className="px-6 py-12 mt-16 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-10 text-gray-800 text-center">
        Statistiques hebdomadaires 
      </h1>

      {/* Section principale : deux colonnes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
        {/* Morceaux joués */}
        <section>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            🎵 Morceaux joués cette semaine
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {weeklySongs.map((song, idx) => (
              <div
                key={idx}
                className="border border-gray-200 p-4 rounded-md bg-white shadow-sm flex flex-col justify-between"
              >
                <div>
                  <p className="text-base font-semibold text-gray-800">
                    {song.title}
                  </p>
                  <p className="text-sm text-gray-500 mb-2">{song.artist}</p>
                </div>

                <div className="flex justify-between items-end text-xs text-gray-500 mt-auto pt-2 border-t">
                  <span>⏱ {song.duration}</span>
                  <span className="italic">{song.mood}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Répartition des moods */}
        <section>
          <h2 className="text-xl font-semibold text-gray-700 mb-8">
            📊 Répartition des moods
          </h2>
          <div className="space-y-4">
            {moodStats.map((mood, idx) => {
              const percentage = (
                (mood.duration / totalDuration) *
                100
              ).toFixed(1);
              return (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1 text-gray-600">
                    <span>{mood.mood}</span>
                    <span>{mood.duration} min</span>
                  </div>
                  <div className="w-full h-3 bg-gray-200 rounded-sm overflow-hidden">
                    <div
                      className={`${mood.color} h-3 rounded-sm`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* Recommandations par mood */}
      <section>
        <h2 className="text-xl font-semibold text-gray-700 mb-6 text-center">
          🔮 Recommandations par mood
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {Object.entries(moodRecommendations).map(([mood, tracks], index) => (
            <div
              key={index}
              className="border bg-white rounded-md p-5 shadow-sm"
            >
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                {mood}
              </h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {tracks.map((track, i) => (
                  <li key={i}>{track}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Statistique;
