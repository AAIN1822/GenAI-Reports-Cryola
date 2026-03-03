import React from "react";
import { Typography, Box, useTheme } from "@mui/material";

interface MDErrorMessageProps {
  id?: string;
  message: string;
  align?: "left" | "center" | "right";
  show?: boolean;
}

const MDErrorMessage: React.FC<MDErrorMessageProps> = ({
  id = "md-error-message",
  message,
  align = "left",
  show = true,
}) => {
  const theme = useTheme();
  if (!show || !message) return null;

  return (
    <Box sx={{ mb: 0.5 }}>
      <Typography
        data-testid={id}
        variant="body2"
        sx={{
          color: theme.palette.custom.errorText,
          fontSize: 12,
          textAlign: align,
          fontWeight: 400,
          overflowWrap: "break-word"
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default MDErrorMessage;