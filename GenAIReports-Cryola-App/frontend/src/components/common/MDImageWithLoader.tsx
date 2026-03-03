import { CircularProgress } from "@mui/material";

type Props = {
  img: string | undefined;
  loading: boolean;
  idx: number;
};

export default function ImageWithLoader({ img, loading, idx }: Props) {
  return (
    <div
      style={{
        position: "relative",
        width: "fit-content",
        display: "inline-block",
      }}
    >
      <img
        src={img}
        alt={`Preview ${idx}`}
        style={{
          minWidth: 70,
          maxWidth: 150,
          borderRadius: 4,
          border: "1px solid #ccc",
          opacity: loading ? 0.5 : 1, // fade effect
        }}
      />

      {loading && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "rgba(255, 255, 255, 0.6)",
            borderRadius: "50%",
            padding: 8,
          }}
        >
          <CircularProgress size={24} sx={{color: "#555"}} />
        </div>
      )}
    </div>
  );
}
