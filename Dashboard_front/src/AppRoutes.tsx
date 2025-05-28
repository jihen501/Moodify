import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import Statistique from "./Statistique";
import Layout from "./Layout";


const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/Recommendation" element={<Statistique />} />
        {/* autres routes ici */}
      </Route>
    </Routes>
  );
};

export default AppRoutes;
