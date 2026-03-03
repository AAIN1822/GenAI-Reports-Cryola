import { useMemo } from "react";
import type { FC, CSSProperties, ReactNode } from "react";
import { CircularProgress, Box } from "@mui/material";

type ButtonVariant =
  | "primary"
  | "outline"
  | "green"
  | "nopad"
  | "gray"
  | "white"
  | "red";

interface MDButtonProps {
  text: string;
  onClick?: () => void;
  variant?: ButtonVariant;
  style?: CSSProperties;
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  loaderSize?: number;
  width?: string;
}

const MDButton: FC<MDButtonProps> = ({
  text,
  onClick,
  variant = "primary",
  style = {},
  disabled = false,
  loading = false,
  leftIcon,
  rightIcon,
  loaderSize = 20,
  width = "100%",
}) => {
  const baseStyle: CSSProperties = {
    width: width,
    height: "35px",
    borderRadius: "6px",
    fontSize: "14px",
    cursor: disabled ? "not-allowed" : "pointer",
    border: "none",
    transition: "all 0.3s ease",
    fontWeight: 600,
    display: "flex",
    alignItems: "center",
    textAlign: "center",
    justifyContent: "center",
    gap: "8px",
    textTransform: "none",
    opacity: disabled ? 0.6 : 1,
    pointerEvents: disabled ? "none" : "auto",
  };

  const variants: Record<ButtonVariant, CSSProperties> = {
    primary: {
      background: "#2C2C2C",
      color: "#FFFFFF",
    },
    outline: {
      background: "#FFFFFF",
      border: "1.5px solid #22A447",
      color: "#22A447",
    },
    green: {
      background: "#00843D",
      color: "#FFFFFF",
    },
    nopad: {
      background: "#DDEEE4",
      border: "1.5px solid #22A447",
      color: "#22A447",
    },
    gray: {
      background: "#E3E3E3",
      border: "1.0px solid #22A447",
      color: "#1E1E1E",
    },
    white: {
      color: "#344054",
      background: "#fff",
      borderColor: "#D0D5DD",
      fontSize: "12px",
      borderRadius: "8px",
    },
    red: {
      background: "#eb0800",
      color: "#fff",
    },
  };

  const combinedStyle = useMemo(
    () => ({
      ...baseStyle,
      ...variants[variant],
      ...style,
    }),
    [variant, style, disabled]
  );

  return (
    <button
      type="button"
      onClick={onClick}
      style={combinedStyle}
      disabled={disabled}
    >
      {/* Left Icon */}
      {leftIcon && (
        <span style={{ display: "flex", alignItems: "center" }}>
          {leftIcon}
        </span>
      )}

      {text}
      {rightIcon && (
        <span style={{ display: "flex", alignItems: "center" }}>
          {rightIcon}
        </span>
      )}

      {/* If loading, show loader on right */}
      {loading && (
        <Box sx={{ color: "white" }}>
          <CircularProgress color="inherit" size={loaderSize | 20} />
        </Box>
      )}
    </button>
  );
};

export default MDButton;
