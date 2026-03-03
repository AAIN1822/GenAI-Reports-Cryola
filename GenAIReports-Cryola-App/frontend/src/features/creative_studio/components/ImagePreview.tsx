import * as React from "react";
import { Radio, useTheme } from "@mui/material";
import type { CSSProperties } from "react";
import MDActionHeader from "../../../components/common/MDActionHeader";
import MDActionFooter from "../../../components/common/MDActionFooter";
import type { Image } from "../../../utils/constants";
import { downloadImageFromUrl } from "../../../utils/helpers";

interface ImagePreviewProps {
  title: string;
  stage: string;
  isModify?: boolean;
  selectedImage?: { url: string; score?: number };
  handleModify?: () => void;
  handleClose: () => void;
  handleBack: () => void;
  handleNext: () => void;
  handleSelect?: (img: Image) => void;
  images?: Image[];
  setLoading?: (loading: boolean) => void;
  saveProject?: () => void;
  handlenGenerate?: () => void;
  showNext?: boolean;
  showGenerate?: boolean;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({
  title,
  stage,
  isModify,
  handleModify,
  handleClose,
  handleBack,
  handleNext,
  images,
  handleSelect,
  saveProject,
  selectedImage,
  handlenGenerate,
  showNext,
  showGenerate,
}) => {
  const theme = useTheme();
  const [selectedIndex, setSelectedIndex] = React.useState<number>(0);

  /* IMAGE BOX */
  const cardBox: CSSProperties = {
    width: "330px",
    background: "#fff",
    borderRadius: "12px",

    padding: "12px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    height: "50vh",
  };

  const imageStyle: CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "contain",
  };

  const textWrapper: CSSProperties = {
    width: "100%",
    display: "flex",
    justifyContent: "left",
    flexDirection: "column",
    textAlign: "left",
  };

  React.useEffect(() => {
    if (!images || images.length === 0) return;
    if (selectedImage) {
      const index = images.findIndex(
        (img) =>
          img.url === selectedImage.url && img.score === selectedImage.score,
      );
      setSelectedIndex(index);
      handleSelect?.(images[index]);
    } else {
      setSelectedIndex(0);
      handleSelect?.(images[0]);
    }
  }, [images, selectedImage]);

  const onSelect = (index: number) => {
    setSelectedIndex(index);

    if (images?.[index]) {
      handleSelect?.(images[index]);
    }
  };

  const downloadImage = async () => {
    downloadImageFromUrl(
      images && images.length > 0 && images[selectedIndex]?.url
        ? images[selectedIndex].url
        : "",
    );
  };

  return (
    <div style={{ background: theme.palette.custom.inputScreenBackground }}>
      <MDActionHeader
        title={title}
        isModifyMode={isModify || false}
        onModify={handleModify}
        onClose={handleClose}
        onDownload={downloadImage}
        onSaveAs={saveProject}
      />
      <div
        style={{
          display: "flex",
          gap: 32,
          justifyContent: "center",
          padding: "8px",
        }}
      >
        {[0, 1, 2].map((_, index) => (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
            onClick={() => images?.[index]?.url && onSelect(index)}
          >
            {/* IMAGE CARD */}
            <div
              style={{
                ...cardBox,
                border:
                  images &&
                  images.length > 0 &&
                  images?.[selectedIndex]?.url === images?.[index]?.url
                    ? "3px solid #0FA958"
                    : "3px solid transparent",
              }}
            >
              {images &&
                images?.length > 0 &&
                (images?.[index]?.url ? (
                  <img
                    src={images[index].url}
                    style={imageStyle}
                    alt="preview"
                  />
                ) : (
                  <span style={{ color: theme.palette.custom.grayText }}>
                    Image generation failed due to OpenAI content moderation.
                    Please try a different product image.
                  </span>
                ))}
            </div>

            {/* RADIO + SCORE */}
            {images &&
              images?.length > 0 &&
              images?.[index]?.url &&
              stage !== "Multi_Angle_View" && (
                <>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "9px",
                      marginRight: "25%",
                    }}
                  >
                    {/* ⭐ MUI RADIO COMPONENT */}
                    <Radio
                      checked={selectedIndex === index}
                      onChange={() => onSelect(index)}
                      sx={{
                        padding: 0,
                        color: "#0FA958",
                        "&.Mui-checked": {
                          color: "#0FA958",
                        },
                        transform: "translateY(6px)",
                      }}
                    />
                    <div style={textWrapper}>
                      <span
                        style={{
                          fontWeight: 700,
                          fontSize: "16px",
                          color: "#0FA958",
                        }}
                      >
                        {images[index]?.score}%
                      </span>

                      <span style={{ fontSize: "14px", color: "#545454" }}>
                        Confidence Score
                      </span>
                    </div>
                  </div>
                </>
              )}
          </div>
        ))}
      </div>
      <MDActionFooter
        showGenerate={showGenerate}
        showNext={showNext}
        onGenerate={handlenGenerate}
        onBack={handleBack}
        onNext={handleNext}
        nextLabel={stage === "Multi_Angle_View" ? "Finish" : "Next"}
      />
    </div>
  );
};

export default ImagePreview;
