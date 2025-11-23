import { Outlet } from "react-router";
import Footer from "../components/Footer";
import { PrivateRoute } from "../components/PrivateRoute";

export const UserLayout = () => {
  return (
    <PrivateRoute>
      <div className="h-dvh flex flex-col">
        <main className="flex-1">
          <Outlet />
        </main>
        <Footer />
      </div>
    </PrivateRoute>
  );
};
