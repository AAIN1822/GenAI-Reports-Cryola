import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material";
import type { FC } from "react";

import crayola_logo from '../../../assets/images/crayola_logo.png';
import SSOLogin from "./SSOLogin";

interface LoginScreenProps {
  updateScreen: React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;
  setLoginEmail: React.Dispatch<React.SetStateAction<string>>;
}

const LoginScreen: FC<LoginScreenProps> = ({ updateScreen: _updateScreen, setLoginEmail: _setLoginEmail }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  const [loading, _setLoading] = useState<boolean>(false);
  
  useEffect(() => {
    if (localStorage.getItem("loggedIn") === "true") {
      navigate("/ProjectHistory");
    }
  }, []);

  return (
    <Paper
      elevation={0}
      sx={{
        display: "flex",
        justifyContent: "flex-start",
        flexDirection: "column",
        alignItems: "flex-start",
        p: 2,
        borderRadius: "14px",
        background: theme.palette.custom.greenMist,
        border: `1px solid ${theme.palette.custom.greenOverlay}`,
        boxShadow: "0px 10px 28px rgba(187, 0, 255, 0.06)",
      }}>
      <img src={crayola_logo} alt="Crayola Logo" style={{ width: "120px", marginBottom: "8px" }} />
      <Typography variant="h4" sx={{ mb: 2 }}>
        Login
      </Typography>

      <Typography variant="body2" sx={{ color: theme.palette.custom.grayText, mb: 2 }}>
        Access your Designer workspace
      </Typography>

      <SSOLogin disabled={loading} />

    </Paper>
  )
}
export default LoginScreen;