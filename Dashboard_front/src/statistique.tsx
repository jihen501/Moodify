import { useEffect, useState, useMemo } from "react";
import { fetchWeeklyStats, fetchCurentRecommendations} from "./BackendApi";



type MoodStat = {
  mood: string;
  duration: number | string;
  color: string;
};

type Song = {
  title: string;
  duration: string;
  mood: string;
};

type WeeklyStats = {
  mood_counts: Record<string, number>;
  total_duration_min: number;
  most_common_mood: string;
  weeklySongs?: Song[];
};
const weeklySongs = [
  { title: "Sunflower", duration: "3:30", mood: "Happy" },
  { title: "Someone Like You", duration: "4:45", mood: "Sad" },
  { title: "Stayin'' Alive", duration: "3:57", mood: "Energetic" },
  { title: "Shape of You", duration: "3:53", mood: "Happy" },
  { title: "Lose Yourself", duration: "5:20", mood: "Energetic" },
];
type MoodRecommendation = {
    track_name: string,
    track_artist: string
};
const Statistique = ({ userId = "abc123" }) => {
  const [moodStats, setMoodStats] = useState<MoodStat[]>([]);
  const [totalDurationMin, setTotalDurationMin] = useState<string>("0");
  const [mostCommonMood, setMostCommonMood] = useState<string | null>(null);
  const [dynamicRecommendations, setDynamicRecommendations] = useState<
    MoodRecommendation[]
  >([]);

  const moodColors = useMemo(
    () => ({
      Dance: "bg-yellow-400",
      Sad: "bg-blue-400",
      Energetic: "bg-red-400",
      Happy: "bg-green-400",
      Chill: "bg-purple-400",
      Rap: "bg-pink-400",
      Calm: "bg-gray-400",
      Dreamy: "bg-indigo-400",
      Mixed: "bg-orange-400",
    }),
    []
  );

  const moodRecommendations = {
    Happy: ["Blinding Lights – The Weeknd", "Good as Hell – Lizzo"],
    Sad: ["Let Her Go – Passenger", "Skinny Love – Bon Iver"],
    Energetic: ["Can’t Hold Us – Macklemore", "Levitating – Dua Lipa"],
    Relaxed: ["Weightless – Marconi Union", "Ocean Eyes – Billie Eilish"],
    Angry: ["Killing In The Name – RATM", "Break Stuff – Limp Bizkit"],
  };


  useEffect(() => {
    async function loadStats() {
      try {
        const data: WeeklyStats = await fetchWeeklyStats(userId);
        console.log("Weekly Stats:", data);
        const moods = data.mood_counts || {};
        const moodStatsArr = Object.entries(moods).map(([mood, count]) => ({
          mood,
          duration: count,
          color: moodColors[mood as keyof typeof moodColors] || "bg-gray-400",
        }));

        const totalMin =
          parseFloat(String(data.total_duration_min ));

        setMoodStats(moodStatsArr);
        setTotalDurationMin(totalMin.toFixed(1));
        setMostCommonMood(data.most_common_mood);
       // setWeeklySongs(data.weeklySongs || []);
      } catch {
        setMoodStats([]);
        setTotalDurationMin("0");
        setMostCommonMood(null);
       // setWeeklySongs([]);
      }
    }

    loadStats();
  }, [userId, moodColors]);
  const totalMoodDuration = moodStats.reduce(
    (acc, m) => acc + parseFloat(String(m.duration)),
    0
  );
  useEffect(() => {
    async function loadRecommendations() {
      try {
        const response = await fetchCurentRecommendations(userId);
        console.log("Dynamic Recommendations:", response.recommendations);
        setDynamicRecommendations(response.recommendations || []);
      } catch (err) {
        console.error(
          "Erreur lors du chargement des recommandations dynamiques",
          err
        );
      }
    }

    loadRecommendations();
  }, [userId]);
  
  
  return (
    <div>
      <section>
        <h2 className="text-3xl font-bold mb-10 text-gray-800 text-center pt-14">
           Recommandations Actuelles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 px-36 py-4">
          {dynamicRecommendations.map((rec, idx) => (
            <div
              key={idx}
              className="border p-4 rounded-xl bg-white shadow-md flex flex-col"
            >
              <div>
                <p className="text-base font-semibold text-gray-800">
                  {rec.track_name}
                </p>
              </div>
              <div className="flex justify-between items-end text-xs text-gray-500 mt-auto pt-2 border-t">
                <span className="italic">{rec.track_artist}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="px-6 py-12 mt-16 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-10 text-gray-800 text-center">
          Statistiques de la semaine
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* 🎵 Morceaux joués */}
          <section>
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              🎵 Morceaux joués cette semaine
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {weeklySongs.length > 0 ? (
                weeklySongs.map((song, idx) => (
                  <div
                    key={idx}
                    className="border p-4 rounded-md bg-white shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      <p className="text-base font-semibold text-gray-800">
                        {song.title}
                      </p>
                    </div>
                    <div className="flex justify-between items-end text-xs text-gray-500 mt-auto pt-2 border-t">
                      <span>⏱ {song.duration}</span>
                      <span className="italic">{song.mood}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div>Aucun morceau cette semaine.</div>
              )}
            </div>
          </section>

          {/* 📊 Répartition des moods */}
          <section>
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              📊 Répartition des moods
            </h2>
            <div className="flex gap-4 mb-6">
              <div className="flex-1 bg-purple-100 text-purple-800 p-4 rounded-2xl shadow-md">
                <h2 className="text-lg font-semibold mb-2">
                  Temps total d'écoute
                </h2>
                <p className="text-2xl font-bold">{totalDurationMin}</p>
              </div>
              <div className="flex-1 bg-yellow-100 text-yellow-800 p-4 rounded-2xl shadow-md">
                <h2 className="text-lg font-semibold mb-2">Humeur dominante</h2>
                <p className="text-2xl font-bold">{mostCommonMood}</p>
              </div>
            </div>
            <div className="space-y-4">
              {moodStats.map((mood, idx) => {
                const percentage = totalMoodDuration
                  ? (
                      (parseFloat(String(mood.duration)) / totalMoodDuration) *
                      100
                    ).toFixed(1)
                  : 0;
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
      </div>
    </div>
  );

  
};

export default Statistique;
