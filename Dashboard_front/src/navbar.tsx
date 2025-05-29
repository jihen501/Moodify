import { useEffect, useState } from "react";

const Navbar = () => {
  const [isSpotifyConnected, setIsSpotifyConnected] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem("spotify_user_id");
    setIsSpotifyConnected(!!userId);
  }, []);
  return (
    <nav className="bg-white p-4 shadow-sm">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo Moodify */}
        <div className="flex items-center space-x-3">
          <div className="relative w-6 h-6">
            <div className="absolute inset-0 bg-pink-500 rounded-sm shadow-md animate-pulse"></div>
            <div className="absolute inset-1 bg-yellow-300 rounded-sm"></div>
          </div>
          <span className="font-bold text-lg text-pink-600">Moodify</span>
        </div>

        {/* Navigation */}
        <div className="flex space-x-4 md:space-x-8 items-center">
          <a
            href="/"
            className="text-sm md:text-base text-gray-700 hover:text-pink-500 transition-colors duration-200"
          >
            Home
          </a>

          <a
            href="/Recommendation"
            className="text-sm md:text-base text-gray-700 hover:text-pink-500 transition-colors duration-200"
          >
            Recommandations
          </a>

          {/* Connexion Spotify */}
          {!isSpotifyConnected && (
          <a
            href="http://localhost:5000/auth_spotify"
            target="_blank"
            rel="noopener noreferrer"
            className="relative group cursor-pointer"
          >
            <div className="bg-green-500 px-3 py-1 rounded-sm shadow-md hover:bg-green-600 transition-colors duration-200 flex items-center space-x-2">
              <img
                src="https://cdn-icons-png.flaticon.com/512/174/174872.png"
                alt="Spotify"
                className="w-4 h-4"
              />
              <span className="text-xs md:text-sm text-white font-medium">
                Se connecter à Spotify
              </span>
            </div>
          </a>
          )}
          {isSpotifyConnected && (
            <div
              className="text-sm md:text-base text-pink-500 font-bold transition-colors duration-200"
            >
              Bienvenue
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
