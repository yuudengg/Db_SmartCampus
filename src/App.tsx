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

export function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <HomeLayout />,
      errorElement: <NotFoundPage />,
      children: [
        { index: true, element: <HomePage /> },
        { path: "signup", element: <SignupPage /> },
        { path: "login/user", element: <UserLoginPage /> },
        { path: "user", element: <UserPage /> },
        { path: "user/edit", element: <EditUserPage /> },
        { path: "login/admin", element: <AdminLoginPage /> },
        { path: "admin", element: <AdminPage /> },
        { path: "admin/edit", element: <EditAdminPage /> },
        { path: "admin/manageuser", element: <ManageUserPage /> },
        { path: "user/reservation", element: <SpaceReservation /> },
        { path: "user/reservation/check", element: <CheckResrevPage /> },
      ],
    },
  ]);

  return (
    <>
      <RouterProvider router={router} />
    </>
  );
}
