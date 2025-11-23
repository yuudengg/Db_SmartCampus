import { Outlet } from "react-router";
import { PrivateRoute } from "../components/PrivateRoute";

export const AdminLayout = () => {
  return (
    <PrivateRoute>
      <div className="h-dvh flex flex-col">
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </PrivateRoute>
  );
};
