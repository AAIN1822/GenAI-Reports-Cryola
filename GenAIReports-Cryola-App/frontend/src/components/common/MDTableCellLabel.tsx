import Typography from "@mui/material/Typography";
import type { FC } from "react";
import { useTheme } from "@mui/material";
import type { SxProps, Theme } from "@mui/material/styles";

/**
 * A reusable label component for consistent typography styling.
 * Supports MUI `sx` overrides and customizable text content.
 */
interface MDTableCellLabellProps {
  /** The label text to display */
  text: string;
  /** Optional MUI style overrides */
  sx?: SxProps<Theme>;
}

const MDTableCellLabel: FC<MDTableCellLabellProps> = ({ text, sx }) => {
  const theme = useTheme();
  return (
    <Typography
      sx={{
        fontSize: 13,
        fontWeight: 500,
        color: theme.palette.custom.tableCellLabelColor,
        lineHeight: 1.2,
        ...sx, // ✅ allows flexible overrides
      }}
    >
      {text}
    </Typography>
  );
};

export default MDTableCellLabel;