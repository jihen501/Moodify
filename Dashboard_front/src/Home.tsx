import { FiMusic } from "react-icons/fi";
import { useEffect, useState } from "react";
function Home() {
  const [isSpotifyConnected, setIsSpotifyConnected] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("spotify_user_id");
    setIsSpotifyConnected(!!userId);
  }, []);
  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-yellow-100 font-sans flex flex-col">
      <div className="container mx-auto flex-grow flex items-center px-6">
        <div className="flex flex-col lg:flex-row gap-12 items-center w-full py-12">
          <div className="w-full lg:w-1/2">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-pink-600 mb-4">
              Analyse ton humeur musicale
            </h1>
            <p className="text-xl md:text-2xl lg:text-3xl text-gray-700 mb-8 italic">
              Connecte ton compte Spotify et découvre les émotions de ta semaine
              musicale.
            </p>
            {!isSpotifyConnected && (
            <div className="flex justify-start">
              <button className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md transition-colors duration-200 inline-flex items-center space-x-2"
                onClick={() => {
                  window.location.href = "http://localhost:5000/auth_spotify";
                }}>
                <FiMusic className="text-xl" />
                <span>Se connecter à Spotify</span>
              </button>
            </div>
            )}
          </div>

          <div className="w-full lg:w-1/2 hidden md:block">
            <img
              src="../src/assets/undraw_happy-music_na4p.svg"
              alt="Moodify Dashboard"
              className="w-full h-auto object-cover rounded-lg"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
