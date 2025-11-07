import { createBrowserRouter, RouterProvider } from "react-router";
import "./App.css";
import { HomeLayout } from "./layout/Homelayout";
import { HomePage } from "./pages/HomePage";
import { SignupPage } from "./pages/SignupPage";
import { LoginPage } from "./pages/LoginPage";
import { SpaceReservation } from "./pages/SpaceReservation";
import { NotFoundPage } from "./pages/NotFoundPage";

export function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <HomeLayout />,
      errorElement: <NotFoundPage />,
      children: [
        { index: true, element: <HomePage /> },
        { path: "signup", element: <SignupPage /> },
        { path: "login", element: <LoginPage /> },
        { path: "reservation", element: <SpaceReservation /> },
      ],
    },
  ]);

  return (
    <>
      <RouterProvider router={router} />
    </>
  );
}
