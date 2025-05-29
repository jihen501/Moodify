import { useEffect, useState, useMemo, type JSX } from "react";
import { fetchWeeklyStats } from "./BackendApi";
import { io, Socket } from "socket.io-client"; // Add this import
import { FaPlay } from "react-icons/fa";

import { FaSmile, FaRegFrown, FaBolt, FaLeaf, FaMusic } from "react-icons/fa";

// Exemple de correspondance mood -> couleur + icône
const moodMap: Record<string, { color: string; icon: JSX.Element }> = {
  Happy: { color: "bg-green-200 text-green-800", icon: <FaSmile /> },
  Sad: { color: "bg-blue-200 text-blue-800", icon: <FaRegFrown /> },
  Energetic: { color: "bg-red-200 text-red-800", icon: <FaBolt /> },
  Chill: { color: "bg-purple-200 text-purple-800", icon: <FaLeaf /> },
  Default: { color: "bg-gray-200 text-gray-800", icon: <FaMusic /> },
};

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
type MoodRecommendation = {
  track_name: string;
  track_artist: string;
};
const Statistique = ({ userId = "1" }) => {
  const [moodStats, setMoodStats] = useState<MoodStat[]>([]);
  const [totalDurationMin, setTotalDurationMin] = useState<string>("0");
  const [mostCommonMood, setMostCommonMood] = useState<string | null>(null);
  const [dynamicRecommendations, setDynamicRecommendations] = useState<
    MoodRecommendation[]
  >([]);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string>("");
  const [currentMood, setCurrentlyMood] = useState<string>("");
  const [currentlyTime, setCurrentlyTime] = useState<number>(0);
  useEffect(() => {
    // Connect to Socket.IO backend
    const socket: Socket = io("http://localhost:5000"); // Adjust port if needed

    socket.on("recommendation_update", (data) => {
      // Filter by userId if needed
      console.log(
        "thsi is data user id ",
        data.user_id,
        "and userId is",
        userId
      );
      if (data.user_id === userId) {
        setCurrentlyPlaying(data.track_name || "");
        setCurrentlyTime(data.duration_ms / 60000 || 0);
        setCurrentlyMood(data.mood || "");
        setDynamicRecommendations(data.recommendations || []);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [userId]);
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

        const totalMin = parseFloat(String(data.total_duration_min));

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
              <p className="text-xl font-bold text-gray-800 truncate">
                {currentlyPlaying}
              </p>
              <p className="text-sm text-gray-500 italic">{currentlyTime}</p>

              {/* Barre de progression */}
              <div className="relative w-full h-2 mt-4 bg-gray-300 rounded-full">
                <div className="absolute top-0 left-0 h-2 w-1/3 bg-indigo-500 rounded-full animate-pulse"></div>
              </div>
            </div>
            {/* Badge Mood */}
            <div
              className={`flex items-center space-x-2 px-4 py-4 rounded-2xl font-medium text-xl shadow-md ${
                moodMap[currentMood]?.color ?? moodMap.Default.color
              }`}
            >
              <span>{moodMap[currentMood]?.icon ?? moodMap.Default.icon}</span>
              <span>{currentMood}</span>
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

        <div className="">
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
