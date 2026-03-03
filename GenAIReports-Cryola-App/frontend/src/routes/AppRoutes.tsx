import type { RouteObject } from "react-router-dom";

import AuthScreen from "../features/auth/Pages/AuthScreen";
import CreativeStudio from "../features/creative_studio/Pages/CreativeStudio";
import ProjectHistory from "../features/project/Pages/ProjectHistory";


const appRoutes: RouteObject[] = [
  {
    path: "/",
    element: <AuthScreen />,
  },
  {
    path: "/ProjectHistory",
    element: <ProjectHistory />,
  },
  {
    path: "/creative-studio/:project_id",
    element: <CreativeStudio />,
  },
];

export default appRoutes;
