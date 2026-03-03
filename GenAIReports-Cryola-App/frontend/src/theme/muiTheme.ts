import { createTheme, type ThemeOptions } from "@mui/material/styles";

/**
 * Custom MUI theme configuration for FSDU Creative Studio.
 * Defines primary palette, background, and typography defaults.
 */

// ✅ Extend the Palette type definitions
declare module "@mui/material/styles" {
  interface Palette {
    custom: {
      grayText: string;
      errorText: string;
      greenMist: string;
      emeraldGreen: string;
      greenOverlay: string;
      labelGrayText: string;
      labelBorderColor: string;
      numberInputBackground: string;
      seaGreen: string;
      applicationScreen: string;
      azureBlue: string;
      labelBoxColor: string;
      tableCellLabelColor: string;
      inputScreenBackground: string;
    };
  }
  interface PaletteOptions {
    custom?: {
      grayText?: string;
      errorText?: string;
      greenMist?: string;
      emeraldGreen?: string;
      greenOverlay?: string;
      labelGrayText?: string;
      labelBorderColor?: string;
      numberInputBackground?: string;
      seaGreen?: string;
      applicationScreen?: string;
      azureBlue?: string;
      labelBoxColor?: string;
      tableCellLabelColor?: string;
      inputScreenBackground?: string;
    };
  }
}

const themeOptions: ThemeOptions = {
  palette: {
    primary: {
      main: "#18a34a", // ✅ Brand green
      contrastText: "#ffffff",
    },
    background: {
      default: "#FAFAFC", // ✅ Soft light green background
    },
    custom: {
      grayText: "#8C8C8C",
      errorText: "#d32f2f",
      greenMist: "rgba(0, 137, 45, 0.02)",
      emeraldGreen: "#00892D",
      seaGreen: "#14AE5C",
      greenOverlay: "rgba(0, 137, 45, 0.2)",
      labelGrayText: "#1E1E1E",
      labelBorderColor: "#D9D9D9",
      numberInputBackground: "rgba(120, 120, 120, 0.2)",
      applicationScreen: "#FAFAFC",
      azureBlue: "#007AFF",
      labelBoxColor:"#78787833",
      tableCellLabelColor:"#667085",
      inputScreenBackground: "#E1F0E5"
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    fontSize: 14,
    h6: {
      fontWeight: 700,
    },
    body1: {
      color: "#333",
    },
  },
};

const muiTheme = createTheme(themeOptions);

export default muiTheme;
