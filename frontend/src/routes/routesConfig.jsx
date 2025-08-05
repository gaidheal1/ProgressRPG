import React, { lazy } from "react";

// Lazy load pages
const Home = lazy(() => import("../pages/Home/Home"));
const LoginPage = lazy(() => import("../pages/LoginPage/LoginPage"));
const LogoutPage = lazy(() => import("../pages/LogoutPage/LogoutPage"));
const RegisterPage = lazy(() => import("../pages/RegisterPage/RegisterPage"));
const ConfirmationPage = lazy(() => import("../pages/ConfirmationPage"));
const OnboardingPage = lazy(() => import("../pages/OnboardingPage/OnboardingPage"));
const Game = lazy(() => import("../pages/Game/Game"));
const ProfilePage = lazy(() => import("../pages/Profile/Profile"));

import PrivateRoute from "../components/PrivateRoute";
import RequireOnboardingComplete from "../components/RequireOnboardingComplete";

const routes = [
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/logout",
    element: <LogoutPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/confirm_email/:key",
    element: <ConfirmationPage />,
  },
  {
    path: "/onboarding",
    element: (
      <PrivateRoute>
        <OnboardingPage />
      </PrivateRoute>
    ),
  },
  {
    path: "/game",
    element: (
      <PrivateRoute>
        <RequireOnboardingComplete>
          <Game />
        </RequireOnboardingComplete>
      </PrivateRoute>
    ),
  },
  {
    path: "/profile",
    element: (
      <PrivateRoute>
        <ProfilePage />
      </PrivateRoute>
    ),
  },
  {
    path: "*",
    element: <h2>404: Page Not Found</h2>,
  },
];

export default routes;
