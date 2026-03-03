import React, { useState } from "react";
import { IconButton, InputAdornment, TextField } from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import type { ChangeEvent, MouseEvent } from "react";

interface MDPasswordInputProps {
  password: string;
  handlePasswordChange: (event: ChangeEvent<HTMLInputElement>) => void;
}

const MDPasswordInput: React.FC<MDPasswordInputProps> = ({
  password,
  handlePasswordChange,
}) => {
  const [showPassword, setShowPassword] = useState(false);

  // Masked value: replace characters with • if not showing
  const maskedValue = showPassword ? password : "•".repeat(password.length);

  // Handle user typing
  const handleMaskedChange = (e: ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;

    if (showPassword) {
      // If visible, pass through normally
      handlePasswordChange(e);
    } else {
      // If masked, calculate difference and update password
      let updatedPassword = password;
      if (newValue.length > password.length) {
        // User added character(s)
        const added = newValue.slice(password.length);
        updatedPassword += added;
      } else if (newValue.length < password.length) {
        // User deleted character(s)
        updatedPassword = password.slice(0, newValue.length);
      }
      handlePasswordChange({
        ...e,
        target: { ...e.target, value: updatedPassword },
      } as ChangeEvent<HTMLInputElement>);
    }
  };

  const togglePasswordVisibility = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setShowPassword((prev) => !prev);
  };

  return (
     <TextField
        fullWidth
        variant="outlined"
        size="small"
        placeholder="Password"
        value={maskedValue}
        onChange={handleMaskedChange}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={togglePasswordVisibility}
                onMouseDown={(e) => e.preventDefault()}
                edge="end"
                aria-label="toggle password visibility"
              >
                {showPassword ? <Visibility /> : <VisibilityOff />}
              </IconButton>
            </InputAdornment>
          ),
          style: { backgroundColor: "transparent" }, // Safari-safe
        }}
        inputProps={{
          autoComplete: "current-password",
        }}
      />
  );
};

export default MDPasswordInput;
