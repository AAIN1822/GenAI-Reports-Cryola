import type { FC, CSSProperties } from "react";

interface MDCardPreview {
  image: string;
  score: number;
  selected?: boolean;
  onClick?: () => void;
  align?: "left" | "center" | "right";   // ⭐ NEW — control alignment
  style?: CSSProperties;
}

const MDCardPreview: FC<MDCardPreview> = ({
  image,
  score,
  selected = false,
  onClick,
  align = "center",       // ⭐ Default center
  style = {},
}) => {

  /* IMAGE BOX */
  const cardBox: CSSProperties = {
    width: "330px",
    height: "330px",
    background: "#fff",
    borderRadius: "12px",
    border: selected ? "3px solid #22A447" : "1px solid #CFCFCF",
    padding: "12px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",

  };

  const imageStyle: CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "contain",
  };

  /* RADIO BUTTON */
  const radioOuter: CSSProperties = {
    width: "22px",
    height: "22px",
    borderRadius: "50%",
    border: "2px solid #0FA958", // black when not selected
    background: "#fff",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    transform: "translateY(9px)",  // ⭐ move slightly DOWN

  };

  const radioInner: CSSProperties = {
    width: "12px",
    height: "12px",
    borderRadius: "50%",
    background: selected ? "#0FA958" : "transparent", // hide when not selected
  };


  /* ⭐ ALIGNMENT LOGIC */
  const justifyMap = {
    left: "flex-start",
    center: "center",
    right: "flex-end",
  };

  const scoreWrapper: CSSProperties = {
    marginTop: "6px",
    width: "100%",
    display: "flex",
    justifyContent: justifyMap[align],
  };

  const textWrapper: CSSProperties = {
    width: "100%",
    display: "flex",
    justifyContent: justifyMap[align],
    transform: "translateX(25px)"   // ← reset (no shift)
  };

  return (
    <div
      style={{
        ...style,
        display: "flex",
        flexDirection: "column",
      }}
      onClick={onClick}
    >
      {/* IMAGE CARD */}
      <div style={cardBox}>
        <img src={image} style={imageStyle} alt="preview" />
      </div>

      {/* RADIO + SCORE */}
      <div style={scoreWrapper}>
        <div style={{ display: "flex", alignItems: "center", gap: "9px", marginRight: "25%" }}>
          <div style={radioOuter}>
            {selected && <div style={radioInner} />}
          </div>

          <span style={{ fontWeight: 700, fontSize: "16px", color: "#0FA958", }}>
            {score}%
          </span>
        </div>
      </div>

      {/* CONFIDENCE LABEL */}
      <div style={textWrapper}>
        <span style={{ fontSize: "14px", color: "#545454", }}>
          Confidence Score
        </span>
      </div>
    </div>
  );
};

export default MDCardPreview;
