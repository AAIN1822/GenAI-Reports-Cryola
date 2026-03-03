import React, { useState } from "react";
import { Paper, Typography, Link, Divider, useTheme } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Tooltip from "@mui/material/Tooltip";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import MDButton from "../../../components/common/MDButton";
import MDLabel from "../../../components/common/MDLabel";
import MDInput from "../../../components/common/MDInput";

import crayola_logo from "../../../assets/images/crayola_logo.png";

import { registerUser } from "../../../api/auth";
import SSOLogin from "./SSOLogin";
import MDErrorMessage from "../../../components/common/MDErrorMessage";
import MDPasswordInput from "../../../components/common/MDPasswordInput";
import { storeToken, storeUser } from "../../../utils/helpers";
import { getMe } from "../../../api/User";

interface SignupScreenProps {
  updateScreen: React.Dispatch<
    React.SetStateAction<
      "login" | "signup" | "forgotPassword" | "resetPassword" | "otp"
    >
  >;
}

const Signup: React.FC<SignupScreenProps> = ({ updateScreen }) => {
  const navigate = useNavigate();
  const theme = useTheme();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  // Field-specific errors
  const [nameError, setNameError] = useState<string>("");
  const [emailError, setEmailError] = useState<string>("");
  const [passwordError, setPasswordError] = useState<string>("");
  const [confirmPasswordError, setConfirmPasswordError] = useState<string>("");
  const [generalError, setGeneralError] = useState<string>("");

  const validatePassword = (password: string) => {
    const regex =
      /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    return regex.test(password);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);

    if (!value) {
      setPasswordError("Password is required");
    } else {
      setPasswordError("");
    }
  };

  const handleConfirmPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    setConfirmPassword(value);

    if (!value) {
      setConfirmPasswordError("Please confirm your password.");
    } else {
      setConfirmPasswordError("");
    }
  };

  const handleSignup = async () => {
    // Reset all errors and success
    setNameError("");
    setEmailError("");
    setPasswordError("");
    setConfirmPasswordError("");
    setGeneralError("");
    setSuccess("");

    let hasError = false;

    // Name validation
    if (!name.trim()) {
      setNameError("Please enter your full name.");
      hasError = true;
    }

    // Email validation
    if (!email.trim()) {
      setEmailError("Please enter your email.");
      hasError = true;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailError("Please enter a valid email address.");
      hasError = true;
    }

    // Password validation
    if (!password) {
      setPasswordError("Please enter a password.");
      hasError = true;
    } else if (!validatePassword(password)) {
      setPasswordError(
        "Password must be at least 8 characters and include a number, a letter, and a special character."
      );
      hasError = true;
    }

    // Confirm password validation
    if (!confirmPassword) {
      setConfirmPasswordError("Please confirm your password.");
      hasError = true;
    } else if (password !== confirmPassword) {
      setConfirmPasswordError("Passwords do not match.");
      hasError = true;
    }

    if (hasError) return; // stop submission if any validation fails

    setLoading(true);
    try {
      const registerRes = await registerUser(name, email, password, "designer");
      console.log("Signup Response:", registerRes.data);
      storeToken(
        registerRes.data.data.access_token,
        registerRes.data.data.refresh_token
      );
      const meResponse = await getMe();
      console.log("Me Response:", meResponse.data);
      storeUser(meResponse.data.data);
      setSuccess("Signup successful!");
      navigate("/ProjectHistory");
    } catch (error: any) {
      console.error("Signup error:", error.response?.data || error);
      if (error.response?.data?.message) {
        setGeneralError(error.response.data.message);
      } else {
        setGeneralError("Signup failed, please try again.");
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
        width: "400px",
        borderRadius: "14px",
        background: theme.palette.custom.greenMist,
        border: `1px solid ${theme.palette.custom.greenOverlay}`,
        boxShadow: "0px 10px 28px rgba(187, 0, 255, 0.06)",
      }}
    >
      <img
        src={crayola_logo}
        alt="Crayola Logo"
        style={{ width: "120px", marginBottom: "8px" }}
      />
      <Typography variant="h4" sx={{ mb: 1 }}>
        Create your Account
      </Typography>

      <Typography
        variant="body2"
        sx={{ color: theme.palette.custom.grayText, mb: 1 }}
      >
        Please fill in the below details
      </Typography>

      {/* Full Name */}
      <MDLabel text="Full Name" />
      <MDInput
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Full Name"
        sx={{
          mb: 0.5
        }}
      />
      {nameError && <MDErrorMessage message={nameError} />}

      {/* Email */}
      <MDLabel text="Email" />
      <MDInput
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email address"
        sx={{ mb: 0.5 }}
      />
      {emailError && <MDErrorMessage message={emailError} />}

      {/* Password */}
      <div style={{ display: "flex", alignItems: "center", gap: "6px", }}>
        <MDLabel text="Password" />
        <Tooltip
          title="Password should be at least 8 characters including one special character, one number, one alphabet."
          arrow
          placement="right"
          componentsProps={{
            tooltip: {
              sx: {
                bgcolor: "#333",
                color: "#fff",
                fontSize: "12px",
                padding: "6px 10px",
                borderRadius: "6px",
              },
            },
          }}
        >
          <InfoOutlinedIcon
            sx={{
              fontSize: 18,
              color: theme.palette.custom.emeraldGreen,
              cursor: "pointer",

            }}
          />
        </Tooltip>
      </div>
      <MDPasswordInput
        password={password}
        handlePasswordChange={handlePasswordChange}
      />
      {passwordError && <MDErrorMessage message={passwordError} />}

      {/* Confirm Password */}
      <MDLabel text="Confirm Password" />
      <MDPasswordInput
        password={confirmPassword}
        handlePasswordChange={handleConfirmPasswordChange}
      />
      {confirmPasswordError && (
        <MDErrorMessage message={confirmPasswordError} />
      )}

      {
        !success && (<Typography sx={{ mb: 1 }} ></Typography>)
      }

      {/* Success Message */}
      {success && (
        <Typography
          variant="body2"
          sx={{ color: theme.palette.custom.emeraldGreen, mb: 1 }}
        >
          {success}
        </Typography>
      )}

      {generalError && <MDErrorMessage message={generalError} />}

      <MDButton
        text="Sign Up"
        onClick={handleSignup}
        variant="primary"
        style={{ height: 42, marginBottom: 10 }}
        disabled={loading}
        loading={loading}
      />
      <Divider sx={{ width: "100%", mb: 2 }}>
        <Typography
          variant="body2"
          sx={{
            textAlign: "center",
            color: theme.palette.custom.grayText,
            width: "100%",
            fontSize: 14,
          }}
        >
          or
        </Typography>
      </Divider>

      <SSOLogin disabled={loading} />

      <Typography
        variant="body2"
        sx={{
          mt: 1,
          textAlign: "center",
          color: theme.palette.custom.grayText,
        }}
      >
        Already have an account?{" "}
        <Link
          component="button"
          underline="always"
          sx={{ color: theme.palette.custom.emeraldGreen, cursor: "pointer" }}
          onClick={() => updateScreen("login")}
          disabled={loading}
        >
          Sign In
        </Link>
      </Typography>
    </Paper>
  );
};

export default Signup;
