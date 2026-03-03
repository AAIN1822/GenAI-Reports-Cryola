import { type FC, type CSSProperties, useState } from "react";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import ThumbDownAltOutlinedIcon from "@mui/icons-material/ThumbDownAltOutlined";

interface MDLikeDislikeProps {
  stage: string;
  question?: string;
  onChange?: (value: "like" | "dislike" | null) => void;
  style?: CSSProperties;
  giveFeedback?: (like: boolean, stage: string) => void;
}

const MDLikeDislike: FC<MDLikeDislikeProps> = ({
  stage,
  question = "Would you Like this?",
  style = {},
  giveFeedback
}) => {
  const [selected, setSelected] = useState<"like" | "dislike" | null>(null);

  const handleSelect = (value: "like" | "dislike") => {
    setSelected(value);
    giveFeedback?.(value === "like", stage);
  };

  const iconStyle = (type: "like" | "dislike"): CSSProperties => ({
    fontSize: "34px",
    cursor: "pointer",
    transition: "0.2s ease",
    color: selected === type ? (type === "like" ? "#4CAF50" : "#F44336") : "#B0B0B0",
    transform: selected === type ? "scale(1.15)" : "scale(1)",
  });

  return (
    <div
      style={{
        ...style,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "12px",
      }}
    >
      <span style={{ fontSize: "18px", fontWeight: 400, color: "#2D2D2D" }}>
        {question}
      </span>

      <div style={{ display: "flex", gap: "25px" }}>
        <ThumbUpAltOutlinedIcon
          style={iconStyle("like")}
          onClick={() => handleSelect("like")}
        />
        <ThumbDownAltOutlinedIcon
          style={iconStyle("dislike")}
          onClick={() => handleSelect("dislike")}
        />
      </div>
    </div>
  );
};

export default MDLikeDislike;
