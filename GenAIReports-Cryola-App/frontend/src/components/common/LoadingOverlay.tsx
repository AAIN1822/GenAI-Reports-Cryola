import { CircularProgress, Box, Typography } from "@mui/material";

type LoadingOverlayProps = {
  isLoading: boolean;
  children?: React.ReactNode;
  loadingMessage?: string;
};

export default function LoadingOverlay({ isLoading, children, loadingMessage }: LoadingOverlayProps) {
  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        height: "100%",
        borderRadius: 3,
        textAlign: "center",
        cursor: "pointer",
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          transition: "0.3s ease",
          opacity: isLoading ? 0.6 : 1, // ✅ safe
        }}
      >
      {children}
      </Box>

      {/* Loader Overlay */}
      {isLoading && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(255,255,255,0.2)",
            borderRadius: 3,
          }}
        >
          <CircularProgress sx={{color: "#555"}} />
          <Typography color="black" >{loadingMessage ? loadingMessage : ""}</Typography>
        </Box>
      )}
    </Box>
  );
}
