import React, { useRef, useState, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Divider,
  Link,
  useTheme
} from "@mui/material";
import MDButton from "../../../components/common/MDButton";

import crayola_logo from '../../../assets/images/crayola_logo.png';

import { verifyOtp, resendOtp } from "../../../api/auth";
import SSOLogin from "./SSOLogin";
import MDErrorMessage from "../../../components/common/MDErrorMessage";
import MDLabel from "../../../components/common/MDLabel";

interface OtpScreenProps {
  updateScreen: React.Dispatch<React.SetStateAction<"login" | "signup" | "forgotPassword" | "resetPassword" | "otp">>;
  loginEmail?: string;
}

const OTPScreen: React.FC<OtpScreenProps> = ({ updateScreen, loginEmail }) => {
  const theme = useTheme();
  const [otp, setOtp] = useState<string[]>(Array(6).fill(""));
  const inputsRef = useRef<Array<HTMLInputElement | null>>([]);
  const [loading, setLoading] = useState(false);
  const [, setSuccess] = useState("");
  // Timer state
  const [timer, setTimer] = useState<number>(60);
  const [canResend, setCanResend] = useState<boolean>(false);

  // Field-specific errors
  const [otpError, setOtpError] = useState<string>("");

  useEffect(() => {
    if (!canResend) {
      const countdown = setInterval(() => {
        setTimer((prev) => {
          if (prev <= 1) {
            clearInterval(countdown);
            setCanResend(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(countdown);
    }
  }, [canResend]);

  const handleChange = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;

    // Allow only numeric input and move to next box
    if (/^[0-9]?$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);

      // Move to next input if not last and value entered
      if (value && index < otp.length - 1) {
        inputsRef.current[index + 1]?.focus();
      }
    }
  };

  const handleKeyDown =
    (index: number) => (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Backspace" && !otp[index] && index > 0) {
        inputsRef.current[index - 1]?.focus();
      }
    };

  const handleVerify = async () => {
    const code = otp.join("");
    if (code.length < 6) {
      setOtpError("Please enter a 6-digit OTP");
      return;
    }
    if (!loginEmail) {
      updateScreen("forgotPassword");
      return;
    }
    setLoading(true);
    try {
      const otpString = otp.join("");
      const res = await verifyOtp(loginEmail, otpString);
      console.log("OTP Verification Response:", res.data);
      localStorage.setItem("passwordResetToken", res.data.data.password_reset_token);
      setSuccess("OTP verification successful!");
      updateScreen("resetPassword");
    } catch (error: any) {
      console.error("OTP verification error:", error.response?.data || error);
      if (error.response?.data?.message) {
        setOtpError(error.response.data.message);
      } else {
        setOtpError("OTP verification failed, please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend) return;
    setCanResend(false);
    setTimer(30);
    setOtp(Array(6).fill(""));
    inputsRef.current[0]?.focus();
    try {
      const res = await resendOtp(localStorage.getItem("email") || "");
      console.log("OTP Resent Response:", res.data);
      setSuccess("OTP resent successfully!");
    } catch (error: any) {
      console.error("Failed to resend otp", error.response?.data || error);
      if (error.response?.data?.message) {
        setOtpError(error.response.data.message);
      } else {
        setOtpError("Failed to resend otp, please try again.");
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
        sx={{ mb: 2 }}
      >
        Reset Password
      </Typography>

      <Typography variant="body2" sx={{ color: theme.palette.custom.grayText, mb: 3 }}>
        We got your back! Not to worry.
      </Typography>
      <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
        <MDLabel text="OTP" />
        <Link
          component="button"
          variant="body2"
          data-testid="resend-otp"
          underline="none"
          sx={{
            color: canResend ? theme.palette.custom.emeraldGreen : theme.palette.custom.grayText,
            mb: 2,
            cursor: canResend && !loading ? "pointer" : "default",
          }}
          onClick={handleResend}
          disabled={loading || !canResend}
        >
          {canResend ? "Resend OTP" : `Resend OTP in ${timer}s`}
        </Link>
      </div>
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          gap: 1.5,
          mb: 1,
        }}
      >
        {otp.map((digit, index) => (
          <TextField
            key={index}
            value={digit}
            onChange={handleChange(index)}
            onKeyDown={handleKeyDown(index)}
            inputRef={(el) => (inputsRef.current[index] = el)}
            inputProps={{
              maxLength: 1,
              style: { textAlign: "center", fontSize: "20px", width: "12px", height: "10px" },
            }}
          />
        ))}
      </Box>
      {otpError && <MDErrorMessage id="otp-error" message={otpError} />}

      <MDButton text="Submit" onClick={handleVerify} style={{ width: "100%" }} disabled={loading} loading={loading} />

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
          disabled={loading}
        >
          Sign Up
        </Link>
      </Typography>
    </Paper>
  );
};

export default OTPScreen;
