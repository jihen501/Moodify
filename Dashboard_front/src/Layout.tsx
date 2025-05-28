import { Outlet } from "react-router-dom";
import Navbar from "./navbar";

const Layout = () => {
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Navbar />
      <main  >
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
