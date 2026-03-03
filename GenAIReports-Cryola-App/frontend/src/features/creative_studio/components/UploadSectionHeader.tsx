import Typography from "@mui/material/Typography";
import type { FC } from "react";
import { useTheme } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

/**
 * A reusable label component for consistent typography styling.
 * Supports MUI `sx` overrides and customizable text content.
 */
interface UploadSectionHeaderProps {
  /** The label text to display */
  text: string;
  /** Optional MUI style overrides */
  sx?: SxProps<Theme>;
}

const UploadSectionHeader: FC<UploadSectionHeaderProps> = ({ text, sx }) => {
  const theme = useTheme();
  return (
    <Typography
      sx={{
        fontSize: 14,
        fontWeight: 600,
        color: theme.palette.custom.labelGrayText,
        mb: "1px",
        lineHeight: 1.2,
        textAlign: "left",
        position: "sticky",
        top: 0,
        zIndex: 10,
        paddingBottom: 0.5,
        backgroundColor: "#E1F0E5",
        ...sx, // ✅ allows flexible overrides
      }}
    >
      {text}
    </Typography>
  );
};

export default UploadSectionHeader;
