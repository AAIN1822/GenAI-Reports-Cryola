import type { FC, ChangeEvent } from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

// 💡 Define Props Interface for Type Safety
interface ColorPickerProps {
  /** Selected color value (hex string like "#FFFFFF") */
  value: string;
  /** Callback triggered when color changes */
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  /** Optional label above the color picker */
  label?: string;
  /** Optional custom styles for the container */
  backgroundColor?: string;
}

/**
 * A reusable color picker component using MUI and HTML input[type=color].
 */
const ColorPicker: FC<ColorPickerProps> = ({
  value,
  onChange,
  label = "Select Color",
  backgroundColor = "#fff",
}) => {
  return (
    <Box
      sx={{
        p: 2,
        backgroundColor,
        borderRadius: 2,
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      {label && (
        <Typography
          sx={{
            fontSize: 14,
            mb: 1,
            fontWeight: 500,
            color: "#333",
          }}
        >
          {label}
        </Typography>
      )}

      <input
        type="color"
        value={value}
        onChange={onChange}
        style={{
          width: "100%",
          height: "40px",
          border: "1px solid #ddd",
          borderRadius: "6px",
          cursor: "pointer",
          background: "transparent",
        }}
      />
    </Box>
  );
};

export default ColorPicker;
