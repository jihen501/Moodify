import AppRoutes from "./AppRoutes";
import { useEffect } from "react";



function App() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const userId = params.get("user_id");
    if (userId) {
      localStorage.setItem("spotify_user_id", userId);
    }
  }, []);

  return <AppRoutes />;
}

export default App;
