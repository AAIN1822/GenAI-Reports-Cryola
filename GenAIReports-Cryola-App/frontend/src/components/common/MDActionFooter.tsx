import type { FC, CSSProperties } from "react";
import KeyboardArrowLeftRoundedIcon from "@mui/icons-material/KeyboardArrowLeftRounded";
import KeyboardArrowRightRoundedIcon from "@mui/icons-material/KeyboardArrowRightRounded";
import MDButton from "./MDButton";
import { useTheme } from "@mui/material";
import arrow_right_circle from "../../assets/images/arrow_right_circle.png";

interface MDActionFooterProps {
  onBack?: () => void;
  onNext?: () => void;
  onGenerate?: () => void;
  nextLabel?: string; // Next / Finish
  showNext?: boolean;
  showGenerate?: boolean;
  style?: CSSProperties;
}

const MDActionFooter: FC<MDActionFooterProps> = ({
  onBack,
  onNext,
  onGenerate,
  nextLabel = "Next",
  showNext = true,
  showGenerate = true,
  style,
}) => {
  const theme = useTheme();
  const wrapperStyle: CSSProperties = {
    width: "100%",
    background: theme.palette.custom.inputScreenBackground,
    padding: "7px 20px",
    borderRadius: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  };
  return (
    <div style={{ ...wrapperStyle, ...style }}>
      <MDButton
        text="Back"
        leftIcon={<KeyboardArrowLeftRoundedIcon sx={{ fontSize: 25 }} />}
        onClick={onBack}
        width="90px"
        variant="white"
      />
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        {showGenerate && (
          <MDButton
            text="Generate"
            variant="green"
            rightIcon={
              <img
                src={arrow_right_circle}
                alt="Arrow Right"
                style={{ width: 20, height: 20 }}
              />
            }
            loaderSize={1}
            style={{
              backgroundColor: theme.palette.custom.seaGreen,
              width: "140px",
              height: "35px",
              fontSize: "14px",
            }}
            onClick={onGenerate}
          />
        )}

        {showNext && (
          <MDButton
            text={nextLabel}
            rightIcon={<KeyboardArrowRightRoundedIcon sx={{ fontSize: 25 }} />}
            onClick={onNext}
            width="90px"
            variant="white"
          />
        )}
      </div>
    </div>
  );
};

export default MDActionFooter;
