import TextField from "@mui/material/TextField";
import type { TextFieldProps } from "@mui/material/TextField";
import type { FC } from "react";

/**
 * A reusable Input component that wraps MUI's TextField
 * with consistent default styling and full type support.
 */

const MDInput: FC<TextFieldProps> = (props) => {
  return (
    <TextField
      fullWidth
      size="small"
      variant="outlined"
      sx={{
        mb: 1,
        backgroundColor: "white",
        "& .MuiOutlinedInput-input": {
          backgroundColor: "white !important", // ✅ visible background
          borderRadius: "4px",
        },
        "& .MuiOutlinedInput-notchedOutline": {
          borderColor: "#D9D9D9",
        },
        "&:hover .MuiOutlinedInput-notchedOutline": {
          borderColor: "#999",
        },
        "& input:-webkit-autofill": {
          backgroundColor: "white !important",
          WebkitBoxShadow: "0 0 0 1000px white inset !important",
          WebkitTextFillColor: "#000000",
          caretColor: "#000",
        },
        "& input:-internal-autofill-selected": {
          backgroundColor: "white !important",
          WebkitBoxShadow: "0 0 0 1000px white inset !important",
          WebkitTextFillColor: "#000000",
          caretColor: "#000",
        },
      }}
      {...props}
    />
  );
};

export default MDInput;
