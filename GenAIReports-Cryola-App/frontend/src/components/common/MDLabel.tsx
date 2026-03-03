import Typography from "@mui/material/Typography";
import type { FC } from "react";
import { useTheme } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

/**
 * A reusable label component for consistent typography styling.
 * Supports MUI `sx` overrides and customizable text content.
 */
interface MDLabelProps {
  /** The label text to display */
  text: string;
  /** Optional MUI style overrides */
  sx?: SxProps<Theme>;
}

const MDLabel: FC<MDLabelProps> = ({ text, sx }) => {
  const theme = useTheme();
  return (
    <Typography
      sx={{
        fontSize: 14,
        fontWeight: 400,
        color: theme.palette.custom.labelGrayText,
        lineHeight: 1.2,
        textAlign: "left",
        ...sx, // ✅ allows flexible overrides
        mt: 1,
        mb: 0.5
      }}
    >
      {text}
    </Typography>
  );
};

export default MDLabel;
