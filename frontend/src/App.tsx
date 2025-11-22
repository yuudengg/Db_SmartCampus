import { createBrowserRouter, RouterProvider } from "react-router";
import "./App.css";
import { HomeLayout } from "./layout/Homelayout";
import { HomePage } from "./pages/HomePage";
import { SignupPage } from "./pages/User/SignupPage";
import { UserLoginPage } from "./pages/User/UserLoginPage";
import { SpaceReservation } from "./pages/User/SpaceReservation";
import { NotFoundPage } from "./pages/NotFoundPage";
import { AdminLoginPage } from "./pages/Admin/AdminLoginPage";
import { UserPage } from "./pages/User/UserPage";
import { EditUserPage } from "./pages/User/EditUserPage";
import { AdminPage } from "./pages/Admin/AdminPage";
import { EditAdminPage } from "./pages/Admin/EditAdminPage";
import { ManageUserPage } from "./pages/Admin/ManageUserPage";
import { CheckResrevPage } from "./pages/User/CheckResrevPage";
import { ManageSpacePage } from "./pages/Admin/ManageSpacePage";
import { ManageReservPage } from "./pages/Admin/ManageReservPage";
import { ReservStaticPage } from "./pages/Admin/ReservStaticPage";
import { SpaceStopListPage } from "./pages/Admin/SpaceStopListPage";
import { PublicOnlyRoute } from "./components/PublicOnlyRoute";
import { UserLayout } from "./layout/Userlayout";
import { AdminLayout } from "./layout/Adminlayout";

export function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <HomeLayout />,
      errorElement: <NotFoundPage />,
      children: [
        {
          index: true,
          element: (
            <PublicOnlyRoute>
              <HomePage />
            </PublicOnlyRoute>
          ),
        },
        { path: "signup", element: <SignupPage /> },
        { path: "login/user", element: <UserLoginPage /> },
        { path: "login/admin", element: <AdminLoginPage /> },

        {
          path: "user",
          element: <UserLayout />,
          children: [
            { index: true, element: <UserPage /> },
            { path: "edit", element: <EditUserPage /> },
            { path: "reservation", element: <SpaceReservation /> },
            { path: "reservation/check", element: <CheckResrevPage /> },
          ],
        },

        {
          path: "admin",
          element: <AdminLayout />,
          children: [
            { index: true, element: <AdminPage /> },
            { path: "edit", element: <EditAdminPage /> },
            { path: "manage/user", element: <ManageUserPage /> },
            { path: "manage/space", element: <ManageSpacePage /> },
            { path: "manage/reservation", element: <ManageReservPage /> },
            { path: "static", element: <ReservStaticPage /> },
            { path: "manage/space/stop", element: <SpaceStopListPage /> },
          ],
        },
      ],
    },
  ]);

  return (
    <>
      <RouterProvider router={router} />
    </>
  );
}
