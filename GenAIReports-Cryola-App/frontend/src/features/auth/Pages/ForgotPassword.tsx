import React, { useState } from "react";
import type { ChangeEvent } from "react";
import {
  Paper,
  Typography,
  Link,
  useTheme
} from "@mui/material";
import MDInput from "../../../components/common/MDInput";
import MDLabel from "../../../components/common/MDLabel";
import MDButton from "../../../components/common/MDButton";
import Divider from "@mui/material/Divider";

import crayola_logo from '../../../assets/images/crayola_logo.png';

import { forgotPassword } from "../../../api/auth";
import SSOLogin from "./SSOLogin";
import MDErrorMessage from "../../../components/common/MDErrorMessage";
import { isValidEmail } from "../../../utils/helpers";

interface ForgotPasswordProps {
  updateScreen: React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;
  setLoginEmail: React.Dispatch<React.SetStateAction<string>>;
}

const ForgotPassword: React.FC<ForgotPasswordProps> = ({ updateScreen, setLoginEmail }) => {
  const theme = useTheme();

  // Form fields
  const [email, setEmail] = useState<string>("");

  // UI states
  const [error, setError] = useState<string>("");
  const [, setSuccess] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const handleEmailChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);

    setLoginEmail(e.target.value);
    setError("");
  }
  // ✅ Forgot Password API call (no alert, inline feedback)
  const handleEmailSubmit = async (): Promise<void> => {
    setError("");
    setSuccess("");

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    if (!isValidEmail(email)) {
      setError("Enter a valid email address.");
      return;
    }

    // Functions Here Only 
    setLoading(true);
    try {
      const res = await forgotPassword(email);
      console.log("Forgot password response:", res.data);
      setSuccess("Reset link sent successfully!");
      updateScreen("otp")
    } catch (err: any) {
      console.error("Forgot password error:", err.response?.data || err);
      if (err.response?.data?.message) {
        setError(err.response.data.message || "An error occurred. Please try again.");
      } else {
        setError("Failed to send otp. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

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
      }}
    >
      <img src={crayola_logo} alt="Crayola Logo" style={{ width: "120px", marginBottom: "8px" }} />

      <Typography
        variant="h4"
        sx={{ mb: 1 }}
      >
        Reset Password
      </Typography>

      <Typography variant="body2" sx={{ color: theme.palette.custom.grayText, mb: 3 }}>
        We got your back! Not to worry.
      </Typography>

      <MDLabel text="Email" />
      <MDInput
        placeholder="Enter your email address"
        value={email}
        onChange={handleEmailChange}
        sx={{ mb: 0.5 }}
      />
      {
        !error && (<Typography sx={{ mb: 1 }} ></Typography>)
      }

      {/* Inline error or success message */}
      {error && (
        <MDErrorMessage id="email-error" message={error} />
      )}

      <MDButton
        text={"Send OTP"}
        onClick={handleEmailSubmit}
        variant="primary"
        style={{ height: 42, marginBottom: 10 }}
        disabled={loading}
        loading={loading}
      />

      <Divider sx={{ width: "100%", mb: 2 }}>
        <Typography variant="body2" sx={{ textAlign: "center", color: theme.palette.custom.grayText, width: "100%", fontSize: 14 }}>
          or
        </Typography>
      </Divider>

      <SSOLogin disabled={loading} />

      <Typography
        variant="body2"
        sx={{ mt: 2, textAlign: "center", color: theme.palette.custom.grayText, width: "100%" }}
      >
        Don’t have an account?{" "}
        <Link
          component="button"
          data-testid="signup-link"
          underline="always"
          sx={{ color: theme.palette.custom.emeraldGreen, cursor: "pointer" }}
          onClick={() => updateScreen("signup")}
          disabled={loading}
        >
          Sign Up
        </Link>
      </Typography>

    </Paper>
  );
};

export default ForgotPassword;
