import { type FC, type CSSProperties, useState, useEffect} from "react";
import FlashOnIcon from "@mui/icons-material/FlashOn";
import MDLabel from "./MDLabel";
import MDButton from "./MDButton";
import { useTheme } from "@mui/material";

interface MDFeedbackPromptProps {
  onGenerate?: (value: string) => void;
  style?: CSSProperties;
  setFeedBackPrompt?: (value: string) => void;
  handleRegenerate?: () => void;
  prompt?: string;
}

const MDFeedbackPrompt: FC<MDFeedbackPromptProps> = ({
  style = {},
  setFeedBackPrompt,
  prompt = "",
  handleRegenerate
}) => {
  const [text, setText] = useState(prompt);
  const theme = useTheme();

  useEffect(() => {
   setFeedBackPrompt?.(text);
  }, [text]);

  useEffect(() => {
    if(prompt === "") return;
    setFeedBackPrompt?.(prompt);
    setText(prompt);
  }, [prompt]);

  return (
    <div
      style={{
        width: "100%",
        background: theme.palette.custom.inputScreenBackground,
        padding: "4px 8px",
        borderRadius: "4px",
        display: "flex",
        flexDirection: "column",
        gap: "2px",
        ...style,
      }}
    >
      {/* label */}
      <MDLabel text="Feedback prompt" />
      {/* textarea */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        style={{
          width: "100%",
          minHeight: "100px",
          borderRadius: "10px",
          border: "1px solid #dcdcdc",
          outline: "none",
          padding: "8px",
          fontSize: "14px",
          lineHeight: "18px",
          resize: "none",
        }}
      />

      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "4px" }}>
        <MDButton 
          text="Generate"
          leftIcon={
            <FlashOnIcon />
          }
          width="120px"
          onClick={() => handleRegenerate?.()}
        />
      </div>
    </div>
  );
};

export default MDFeedbackPrompt;
