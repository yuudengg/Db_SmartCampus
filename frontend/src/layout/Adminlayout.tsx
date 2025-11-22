import { Outlet } from "react-router";
import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import { PrivateRoute } from "../components/PrivateRoute";

export const AdminLayout = () => {
  return (
    <PrivateRoute>
      <div className="h-dvh flex flex-col">
        <NavBar />
        <main className="flex-1 mt-18">
          <Outlet />
        </main>
        <Footer />
      </div>
    </PrivateRoute>
  );
};
