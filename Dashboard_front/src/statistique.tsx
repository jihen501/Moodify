import { useEffect, useState, useMemo } from "react";
import { fetchWeeklyStats, fetchCurentRecommendations} from "./BackendApi";
import { FaPlay, FaPause } from "react-icons/fa";


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
        <h2 className="text-3xl font-bold mb-10 text-gray-800 text-center pt-14">
          Ta musique du moment 
        </h2>
      <section className="flex justify-center mt-6">

        <div className="w-full max-w-7xl p-4 rounded-2xl bg-gradient-to-br from-indigo-100 to-white shadow-xl">
          <div className="flex items-center space-x-6">
            <img
              src="../src/assets/songs.avif"
              alt="cover"
              className="w-24 h-24 rounded-xl shadow-md object-cover"
            />

            {/* Infos musique */}
            <div className="flex-1">
              <p className="text-xl font-bold text-gray-800 truncate">jihen</p>
              <p className="text-sm text-gray-500 italic">aa</p>

              {/* Barre de progression */}
              <div className="relative w-full h-2 mt-4 bg-gray-300 rounded-full">
                <div className="absolute top-0 left-0 h-2 w-1/3 bg-indigo-500 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>

          {/* Contrôle play/pause centré */}
          <div className="flex justify-center mt-6">
            <button className="text-indigo-600 hover:text-indigo-800 text-3xl transition-transform transform hover:scale-110">
              <FaPlay />
            </button>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold mb-10 text-gray-800 text-center pt-14">
          Recommandations
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
          {/* 📊 Répartition des moods */}
          <section>
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
            <div className="space-y-4 mx-50">
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
