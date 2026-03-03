import { useEffect, useRef, useState } from "react";
import MDSectionAccordion from "../../../components/common/MDSectionAccordion";
import { useTheme, Slider, CircularProgress } from "@mui/material";
import MDLabel from "../../../components/common/MDLabel";
import MDFeedbackPrompt from "../../../components/common/MDFeedbackPrompt";
import MDLikeDislike from "../../../components/common/MDLikeDislike";
import MDButton from "../../../components/common/MDButton";
import listIcon from "../../../assets/images/list_icon.png";
import moveIcon from "../../../assets/images/maximize_icon.png";
import resizeIcon from "../../../assets/images/resize_icon.png";
import colorLightingIcon from "../../../assets/images/color_lighting_icon.png";
import uploadIcon from "../../../assets/images/upload_icon.png";
import CloseIcon from "@mui/icons-material/Close";
import type { Image } from "../../../utils/constants";
import { useSelector } from "react-redux";
import type { RootState } from "../../../redux/store";
import { refinementDelete, refinementUpload } from "../../../api/upload";
import RestoreIcon from '@mui/icons-material/Restore';

interface Position {
  x: number;
  y: number;
}

interface Filters {
  brightness: number;
  contrast: number;
  saturate: number;
  hue: number;
  blur: number;
}

export default function ImageEditor(
  {image, stage, setFeedBackPrompt, handleRegenerate, selectUploadedImage, giveFeedback, cancelUploadedImage}: {
    image?: Image;
    stage: string;
    setFeedBackPrompt: React.Dispatch<React.SetStateAction<string>>;
    handleRegenerate: () => void;
    selectUploadedImage?: (url: string) => void;
    giveFeedback?: (like: boolean, stage: string) => void;
    cancelUploadedImage?: () => void;
  }) {
  const theme = useTheme();
  const { currentProjectId } = useSelector(
    (state: RootState) => state.projectData
    );
  const [pos, setPos] = useState<Position>({ x: 200, y: 20 });
  const [originalSize, setOriginalSize] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });
  const [scale, setScale] = useState(1);
  const [initialScale, setInitialScale] = useState(1);
  const [rotation, setRotation] = useState<number>(0);
  const [displayImage, setDisplayImage] = useState<Record<string, any> | undefined>(undefined);

  const [filters, setFilters] = useState<Filters>({
    brightness: 100,
    contrast: 100,
    saturate: 100,
    hue: 0,
    blur: 0,
  });

  const [dragging, setDragging] = useState<boolean>(false);
  const [offset, setOffset] = useState<Position>({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement | null>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const imageSizeLoadedRef = useRef(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [resizedWidth, setResizedWidth] = useState<number>(0);
  const [resizedHeight, setResizedHeight] = useState<number>(0);

  useEffect(() => { 
    if (!image?.url) return;
    if(displayImage?.uploadedUrl === image.url) return;
    const newRecord = {
        file: null,
        previewUrl: null,
        uploadedUrl: image?.url || null,
        name: null,
        loading: false,
        local: false,
      };
    setDisplayImage(newRecord);
    imageSizeLoadedRef.current = false;
  }, [image]);

  // Start Drag
  const startDrag = (e: React.MouseEvent<HTMLImageElement, MouseEvent>) => {
    setDragging(true);
    setOffset({
      x: e.clientX - pos.x,
      y: e.clientY - pos.y,
    });
  };

  // Dragging
  const onDrag = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (!dragging) return;
    setPos({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const stopDrag = () => setDragging(false);
  
  const handleFiles = async (fileList: FileList) => {
      const selectedFiles = Array.from(fileList).filter((f) =>
        f.type.startsWith("image/")
      );
  
      if (!selectedFiles.length) return;
      const newRecord = {
        file: selectedFiles[0],
        previewUrl: URL.createObjectURL(selectedFiles[0]),
        uploadedUrl: undefined,
        name: selectedFiles[0].name,
        loading: true,
        local: true,
      };
      imageSizeLoadedRef.current = false;
      setDisplayImage(newRecord);
      handleUpload(newRecord);
    };

  const handleUpload = async (record: Record<string, any>) => {  
      try {
        const res = await refinementUpload(currentProjectId, stage, record.name, record.file);
        const blobUrl = res?.data?.data?.url;
        resetFilters();
        const updatedRecord = {
          ...record,
          uploadedUrl: blobUrl,
          loading: false,
        };
        setDisplayImage(updatedRecord);
        selectUploadedImage && selectUploadedImage(blobUrl);
        return blobUrl;
      } catch (err) {
        console.error("Upload Failed", err);
      }
    };

  const handleDelete = async () => {
    if(displayImage?.uploadedUrl) {
      setDisplayImage((prev) => ({
        ...prev,
        file: null,
        loading: true,
        uploadedUrl: null,
      }));
      try {
       await refinementDelete(currentProjectId, displayImage?.uploadedUrl || "");
        setDisplayImage((prev) => ({
          ...prev,
          file: null,
          loading: false,
          uploadedUrl: null,
          local: false,
        }));
        cancelUploadedImage && cancelUploadedImage();
      } catch (err) {
        console.error("Upload Failed", err);
      }}
    }
  const resetImagePlacement = () => {   
    setScale(initialScale);
    const container = containerRef.current;

    const containerWidth = container?.clientWidth || 100;
    const containerHeight = container?.clientHeight || 100;

    const imageWidth = originalSize.width * initialScale;
    const imageHeight = originalSize.height * initialScale;

    setPos({
      x: (containerWidth - imageWidth) / 2,
      y: (containerHeight - imageHeight) / 2,
    });
    console.log("x", (containerWidth - imageWidth) / 2, "y:", (containerHeight - imageHeight) / 2);
    setResizedWidth(imageWidth);
    setResizedHeight(imageHeight);
    setRotation(0); 
  }

  const resetFilters = () => {
    setFilters({
      brightness: 100,
      contrast: 100,
      saturate: 100,
      hue: 0,
      blur: 0,
    });
  }

  useEffect(() => {
    const src = displayImage?.uploadedUrl || displayImage?.previewUrl;
    if (!src) return;
   

    const img = new Image();
    img.src = src;
    console.log("displayImage", displayImage)
    img.onload = () => {
      console.log("img.width:", img.width, "img.height:", img.height);
      setOriginalSize({
        width: img.width,
        height: img.height,
      }); 
    };
  }, [displayImage?.uploadedUrl, displayImage?.previewUrl]);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!originalSize.width || !originalSize.height) return;
    

    const containerWidth = containerRef.current.clientWidth;
    const containerHeight = containerRef.current.clientHeight;

    const scaleX = containerWidth / originalSize.width;
    console.log("containerWidth:", containerWidth, "originalSize.width:", originalSize.width, "scaleX:", scaleX);
    const scaleY = containerHeight / originalSize.height;
    console.log("containerHeight:", containerHeight, "originalSize.height:", originalSize.height, "scaleY:", scaleY);

    const fitScale = Math.min(scaleX, scaleY, 1); // 🔑 contain

    setScale(fitScale);
    setInitialScale(fitScale);
    
  }, [originalSize]);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!originalSize.width || !originalSize.height) return;
    if( imageSizeLoadedRef.current) return;

    const container = containerRef.current;

    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    const imageWidth = originalSize.width * scale;
    const imageHeight = originalSize.height * scale;

    setPos({
      x: (containerWidth - imageWidth) / 2,
      y: (containerHeight - imageHeight) / 2,
    });
    console.log("x", (containerWidth - imageWidth) / 2, "y:", (containerHeight - imageHeight) / 2, "imageWidth:", imageWidth, "imageHeight:", imageHeight);
    setResizedWidth(originalSize.width > imageWidth ? imageWidth : originalSize.width);
    setResizedHeight(originalSize.height > imageHeight ? imageHeight : originalSize.height);

    imageSizeLoadedRef.current = true;
  }, [scale]);

  const resizeImage = (value: number) => {
    setScale(value);
    const container = containerRef.current;

    const containerWidth = container?.clientWidth || 100;
    const containerHeight = container?.clientHeight || 100;

    const imageWidth = originalSize.width * value;
    const imageHeight = originalSize.height * value;

    setPos({
      x: (containerWidth - imageWidth) / 2,
      y: (containerHeight - imageHeight) / 2,
    });
    console.log("x", (containerWidth - imageWidth) / 2, "y:", (containerHeight - imageHeight) / 2);
    setResizedWidth(imageWidth);
    setResizedHeight(imageHeight);
  }

  return (
    <div
      style={{
        width: "100%",
        height: "60vh",
        padding: "0 8px",
        display: "flex",
        background: theme.palette.custom.inputScreenBackground,
      }}
      onMouseMove={onDrag}
      onMouseUp={stopDrag}
    >
      {/* LEFT: Controls */}
      <div style={{ width: "30vw", maxHeight: "60vh", overflowY: "auto"}}>
        <MDSectionAccordion
          title="Image Placement and sizing"
          defaultExpanded={false}
          detailsSx={{
            justifyContent: "center",
            alignItems: "center",
            padding: "8px 0 8px 16px",
            border: `2px solid ${theme.palette.custom.inputScreenBackground}`,
            borderRadius: 0
          }}
          headerIcon={
                <img
                  src={listIcon}
                  alt="Arrow Right"
                  style={{width: "15px"}}
                />
              }
          rightIcon={
                <RestoreIcon
                  style={{cursor: "pointer"}}
                  onClick={resetImagePlacement}
                />
              }
        >
          <div className="d-flex">
              <img
                  src={moveIcon}
                  alt="Arrow Right"
                  style={{width: "15px", marginRight: "8px", marginLeft: "6px"}}
                />
                <MDLabel text="Move" />
          </div>
          <MDSectionAccordion title="Resize"
            detailsSx={{
            justifyContent: "center",
            alignItems: "center",
            padding: "8px",
            border: `2px solid ${theme.palette.custom.inputScreenBackground}`,
            borderRadius: 0
          }}
          headerIcon={
                <img
                  src={resizeIcon}
                  alt="Arrow Right"
                  style={{width: "15px"}}
                />
              }
         
        >
            <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
            <div style={{width: "100px"}}>
              <MDLabel text="Resize" />
            </div>
            <Slider
                value={scale}
                min={0.1}
                max={3}
                step={0.01}
                onChange={(_, value) => resizeImage(value as number)}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
            </div>
            <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
              <div style={{width: "100px"}}>
              <MDLabel text="Rotate" />
              </div>
              <Slider
                value={rotation}
                min={50}
                max={500}
                onChange={(_event: Event, value: number | number[]) => {
                    if (typeof value === "number") {
                    setRotation(value);
                    }
                }}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
            </div>
          </MDSectionAccordion>
        </MDSectionAccordion>
        <MDSectionAccordion
          title="Color and lighting"
          defaultExpanded={false}
          detailsSx={{
            justifyContent: "center",
            alignItems: "center",
            padding: "8px",
            border: `2px solid ${theme.palette.custom.inputScreenBackground}`,
            borderRadius: 0
          }}
          headerIcon={
                <img
                  src={colorLightingIcon}
                  alt="Arrow Right"
                  style={{width: "12px"}}   
                />
              }
           rightIcon={
                <RestoreIcon
                  style={{cursor: "pointer"}}
                  onClick={resetFilters}
                />
              }
        >
          <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
            <div style={{width: "100px"}}>
          <MDLabel text="Brightness" />
          </div>
          <Slider
                value={filters.brightness}
                min={50}
                max={500}
                onChange={(_event: Event, value: number | number[]) => {
                    setFilters({ ...filters, brightness: Number(value) })
                }}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
            </div>
          <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
            <div style={{width: "100px"}}>
          <MDLabel text="Contrast"/>
          </div>
          <Slider
                value={filters.contrast}
                min={50}
                max={500}
                onChange={(_event: Event, value: number | number[]) => {
                    setFilters({ ...filters, contrast: Number(value) })
                }}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
            </div>
          <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
            <div style={{width: "100px"}}>
          <MDLabel text="Saturation" />
          </div>
          <Slider
                value={filters.saturate}
                min={50}
                max={500}
                onChange={(_event: Event, value: number | number[]) => {
                    setFilters({ ...filters, saturate: Number(value) })
                }}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
          </div>
          <div className="d-flex" style={{gap: 12, marginTop: "10px"}}>
            <div style={{width: "100px"}}>
          <MDLabel text="Hue" />
          </div>
          <Slider
                value={filters.hue}
                min={50}
                max={500}
                onChange={(_event: Event, value: number | number[]) => {
                    setFilters({ ...filters, hue: Number(value) })
                }}
                style={{
                  width: "280px",
                  position: "relative",
                  right: "12px"
                }}
            />
          </div>
        </MDSectionAccordion>
        <MDFeedbackPrompt 
          setFeedBackPrompt={setFeedBackPrompt}
           prompt={image?.feedback_prompt || ""}
          handleRegenerate={() => {
            resetImagePlacement();
            resetFilters();
            handleRegenerate();
            }}  
        />
        {/* <br />
        <br />
        <button
          onClick={downloadImage}
          style={{
            padding: "10px",
            background: "black",
            color: "white",
            width: "100%",
            borderRadius: "6px",
          }}
        >
          Download Edited Image
        </button> */}

        <canvas ref={canvasRef} style={{ display: "none" }}></canvas>
      </div>
      {/* LEFT: Image Editing Area */}
      <div
      ref={containerRef}
        style={{
          flex: 1,
          position: "relative",
          overflow: "hidden",
          backgroundColor: "#fff",
          contain: "layout paint", // 🔑 prevents layout shifts
        }}
      >
        {displayImage?.loading === false ? (
        <img
          ref={imgRef}
          src={displayImage?.uploadedUrl || displayImage?.previewUrl || ""}
          alt=""
          onMouseDown={startDrag}
          style={{
            width: resizedWidth,
            height: resizedHeight,
            position: "absolute",
            left: pos.x,
            top: pos.y,
            transform: `rotate(${rotation}deg)`,
            filter: `
              brightness(${filters.brightness}%)
              contrast(${filters.contrast}%)
              saturate(${filters.saturate}%)
              hue-rotate(${filters.hue}deg)
              blur(${filters.blur}px)
            `,
            cursor: "grab",
            userSelect: "none",
          }}
        /> ): <CircularProgress  
        style={{
            position: "absolute",
            left: containerRef.current ? (containerRef.current.clientWidth / 2) - 20 : '50%',
            top: containerRef.current ? (containerRef.current.clientHeight / 2) - 20 : '50%',
        }}
        />}
        <div style={{position: 'absolute', bottom: "12px", right: "12px"}}>
        <MDLikeDislike stage={stage} giveFeedback={giveFeedback} />
        </div>
        <div style={{display: "flex", position: 'absolute', bottom: "20px", left: "12px", gap: 8}}>
        <MDButton text="Upload"
        leftIcon={
                <img
                  src={uploadIcon}
                  alt="Arrow Right"
                  width={15}
                />
              }
              onClick={() => fileInputRef.current?.click()}
        />
        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept="image/png, image/jpeg, image/jpg"
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
         <MDButton text="Cancel" variant="red"
            leftIcon={<CloseIcon />}
            onClick={handleDelete}
            disabled={displayImage?.loading || !displayImage?.previewUrl}
         />
        </div>
      </div>
    </div>
  );
}
