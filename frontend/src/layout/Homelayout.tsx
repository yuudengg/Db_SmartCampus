import { Outlet } from "react-router";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";

export const HomeLayout = () => {
  return (
    <div className="h-dvh flex flex-col">
      <NavBar />
      <main className="flex-1 mt-18">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
