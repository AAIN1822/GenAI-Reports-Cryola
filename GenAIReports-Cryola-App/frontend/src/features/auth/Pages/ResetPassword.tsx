import React, { useEffect, useState } from "react";
import type { ChangeEvent } from "react";
import {
  Paper,
  Typography,
  Divider,
  useTheme,
  Tooltip,
  Link
} from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { useNavigate } from "react-router-dom";
import MDLabel from "../../../components/common/MDLabel";
import MDButton from "../../../components/common/MDButton";

import crayola_logo from '../../../assets/images/crayola_logo.png';

import { resetPassword } from "../../../api/auth";
import SSOLogin from "./SSOLogin";
import MDPasswordInput from "../../../components/common/MDPasswordInput";
import { validatePassword } from "../../../utils/helpers";
import MDErrorMessage from "../../../components/common/MDErrorMessage";

interface ResetPasswordProps {
  updateScreen: React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;
}

const ResetPassword: React.FC<ResetPasswordProps> = ({ updateScreen }) => {
  const navigate = useNavigate();
  const theme = useTheme();

  // Form fields
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [newPasswordError, setNewPasswordError] = useState<string>("");
  const [confirmPasswordError, setConfirmPasswordError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  // UI states
  const [error, setError] = useState<string>("");

  useEffect(() => {

  }, [])

  const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    setNewPassword(e.target.value);
    setNewPasswordError("");


  };

  const handleConfirmPasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    setConfirmPassword(e.target.value);
    setConfirmPasswordError("");


  }
  // ✅ Step 2: Validate Password Reset
  const handlePasswordReset = async () => {
    let hasError = false
    if (!newPassword) {
      setNewPasswordError("Please enter a password.");
      hasError = true;
    } else if (!validatePassword(newPassword)) {
      setNewPasswordError(
        "Password must be at least 8 characters and include a number, a letter, and a special character."
      );
      hasError = true;

    }
    if (!confirmPassword) {
      setConfirmPasswordError("Please enter a confirm password.");
      hasError = true;

    } else if (newPassword !== confirmPassword) {
      setConfirmPasswordError("Passwords do not match.");
      hasError = true;
    }

    if (hasError) return; // stop submission if any validation fails


    setError("");
    setLoading(true);
    try {
      const res = await resetPassword(newPassword, localStorage.getItem("passwordResetToken") || "");
      console.log("Password Reset Response:", res.data);
      setLoading(false);
    } catch (error: any) {
      console.error("Failed to reset password", error.response?.data || error);
      setLoading(false);
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError("Failed to reset password, please try again.");
      }
    }

    alert("Password reset successfully!");
    updateScreen("login");
    navigate("/");
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
        sx={{ mb: 2 }}
      >
        Reset Password
      </Typography>

      <Typography variant="body2" sx={{ color: theme.palette.custom.grayText, mb: 3 }}>
        We got your back! not to worry.
      </Typography>
      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
        <MDLabel text="New Password" />
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
      <MDPasswordInput password={newPassword} handlePasswordChange={handlePasswordChange} />
      {newPasswordError && (<MDErrorMessage message={newPasswordError} />)}

      <MDLabel text="Confirm Password" />
      <MDPasswordInput password={confirmPassword} handlePasswordChange={handleConfirmPasswordChange} />
      {confirmPasswordError && (<MDErrorMessage message={confirmPasswordError} />)}

      {
        !error && (<Typography sx={{ mb: 1 }} ></Typography>)
      }

      {/* ✅ Inline error message */}
      {error && (
        <MDErrorMessage id="reset-password-error" message={error} />
      )}

      <MDButton
        text="Submit"
        onClick={handlePasswordReset}
        variant="primary"
        style={{ height: 42, marginBottom: 10 }}
        loading={loading}
        disabled={loading}
      />

      <Divider sx={{ width: "100%", mb: 2 }}>
        <Typography variant="body2" sx={{ textAlign: "center", color: theme.palette.custom.grayText, width: "100%", fontSize: 14 }}>
          or
        </Typography>
      </Divider>

      <SSOLogin disabled={loading} />

      <Typography variant="body2" sx={{ mt: 2, textAlign: "center", color: theme.palette.custom.grayText, width: "100%" }}>
        Don’t have an account?{" "}
        <Link
          component="button"
          underline="always"
          sx={{ color: theme.palette.custom.emeraldGreen }}
          onClick={() => updateScreen("signup")}
          disabled={loading}>
          Sign Up
        </Link>
      </Typography>
    </Paper>
  );
};

export default ResetPassword;
