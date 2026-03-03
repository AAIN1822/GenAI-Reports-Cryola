import { useState } from "react";
import { useTheme } from "@mui/material";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";

import LoginScreen from "./LoginScreen";
import SignupScreen from "./Signup";
import ForgotPassword from "./ForgotPassword";
import OtpScreen from "./OtpScreen";
import ResetPassword from "./ResetPassword";
// 👇 Type imports
import type { FC } from "react";
import shelf from "../../../assets/images/shelf2.png";
import color_slider from "../../../assets/images/color_slider.png";
import color_grid from "../../../assets/images/color_grid.png";
import designer from "../../../assets/images/designer.png";

import "./AuthScreen.scss"

const AuthScreen: FC = () => {
  const [screenState, setScreenState] = useState<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">("login");
  const [loginEmail, setLoginEmail] = useState<string>("");
  const theme = useTheme();

  const renderForm = (formType: "login" | "signup" | "forgotPassword" | "resetPassword" | "otp") => {
  switch (formType) {
    case "login": return <LoginScreen updateScreen={setScreenState} setLoginEmail={setLoginEmail} />;
    case "signup": return <SignupScreen updateScreen={setScreenState} />;
    case "forgotPassword": return <ForgotPassword updateScreen={setScreenState} setLoginEmail={setLoginEmail} />;
    case "resetPassword": return <ResetPassword updateScreen={setScreenState} />;
    case "otp": return <OtpScreen updateScreen={setScreenState} loginEmail={loginEmail} />;
    default: return <LoginScreen updateScreen={setScreenState} setLoginEmail={setLoginEmail} />;
  }
};

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: theme.palette.custom.applicationScreen,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100vw",
        p: "2rem 8rem",
      }}
    >
      <Grid container spacing={6} size={{xs: 12}} justifyContent="space-between" alignItems="center">
        {/* LEFT CARD */}
        <Grid size={{ xs: 6, md: 5}} sx={{minWidth: 350, maxWidth:350}} component="div">
          {renderForm(screenState)}
        </Grid>

        {/* RIGHT CARD */}
        <Grid size={{ xs: 6, md: 5}} sx={{ minWidth: 450 }} component="div">
          <Paper
            elevation={0}
            sx={{
              height: "100%",
              borderRadius: "16px",
              bgcolor: "#fff",
              border: "1px solid #E4E4E4",
              p: 2,
              display: "flex",
              flexDirection: "column",
              justifyContent: "flex-start",
              alignItems: "center",
              minHeight: 550,
            }}
          >
            <div className="image-stack">
            <img src={shelf} alt="Shelf" style={{ marginBottom: "15px", borderRadius: "8px", width: "180px" }} />
            <div style={{ display: "flex", flexDirection: "column", position: "relative", top: "50px" }}>
              <img src={designer} alt="Designer" style={{ marginBottom: "15px", borderRadius: "8px", width: "180px", position: "relative", top: "-50px", left: "20px" }} />
              <img src={color_slider} alt="Color Slider" style={{ marginBottom: "15px", borderRadius: "8px", top: "-70px", width: "120px" }} />
            </div>
            </div>
            <img  className="color_grid_front_page" src={color_grid} alt="Color Grid" style={{ borderRadius: "8px" }} />  
            <Typography sx={{ fontSize: "16px", mb: 0, fontWeight: 600, fontStyle: "bold" }}>
              Build Merchandising Display market ready creatives
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: theme.palette.custom.grayText,
                textAlign: "center",
                maxWidth: 300,
                lineHeight: 1.4,
              }}
            >
              Lets build Merchandising Display creatives that are market ready, collaborate with team and after market.
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AuthScreen;