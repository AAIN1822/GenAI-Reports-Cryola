
import React from "react";
import { useRoutes } from "react-router-dom";
import appRoutes from "./routes/AppRoutes";
import './App.css'

const App: React.FC = () => {
  const routes = useRoutes(appRoutes);
  return routes
}

export default App
