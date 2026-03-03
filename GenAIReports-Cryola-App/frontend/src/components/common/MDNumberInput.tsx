import React from "react";
import TextField from "@mui/material/TextField";
import { useTheme } from "@mui/material/styles";

export type SimpleNumberInputProps = {
  value?: number | string;
  onChange?: (value: number | string) => void;
  size?: "small" | "medium";
  max?: number;
};

/**
 * Tiny number input for 3-digit numbers
 */
const NumberInput: React.FC<SimpleNumberInputProps> = ({
  value = "",
  onChange = () => {},
  size = "small",
  max = 1000,
}) => {
  const theme = useTheme();
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    onChange(val)
  };

  return (
    <TextField
      type="number"
      value={value}
      onChange={handleChange}
      size={size}
      style={{minWidth: "30px"}}
      slotProps={{
        htmlInput: {
          min: 0,
          max: max || undefined,
          step: 1,
        },
      }}
      sx={{
         "& .MuiInputBase-root": {
         
        },
         /* Remove number input arrows */
        "& input::-webkit-outer-spin-button, & input::-webkit-inner-spin-button": {
          WebkitAppearance: "none",
          margin: 0,
        },
        "& input[type=number]": {
          MozAppearance: "textfield", // Firefox
        },
        "& .MuiInputBase-input": {
          padding: "4px 8px",      // ← actual input padding
          width: "3ch",
        background: `${theme.palette.custom.numberInputBackground} !important`,
          borderRadius: 1,
          borderWidth: 0, 
        },
        "& .MuiOutlinedInput-notchedOutline": {
          border: "none !important",
        },
      }}
    />
  );
};

export default NumberInput;
