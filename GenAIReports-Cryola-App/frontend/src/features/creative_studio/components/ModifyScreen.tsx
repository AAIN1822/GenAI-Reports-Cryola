import * as React from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../../../redux/store"; // make sure this points to your root reducer
import MDActionHeader from "../../../components/common/MDActionHeader";
import MDActionFooter from "../../../components/common/MDActionFooter";
import ImageEditor from "./ImageEditor";
import {
  applyAIColorThemeRegeneration,
  applyAIGraphicsRegeneration,
  applyAIPlacementRegeneration,
  feedback,
  getJobStatus,
} from "../../../api/ai";
import type { Image } from "../../../utils/constants";
import MDConfirmationModel from "../../../components/common/MDConfirmationModel";
import { fetchProject } from "../../../api/projects";
import { useRef } from "react";
import { downloadImageFromUrl } from "../../../utils/helpers";

interface ModifyScreenProps {
  title: string;
  stage: string;
  handleUpdate: () => void;
  handleClose: () => void;
  handleBack: () => void;
  handleNext: (image: Image) => void;
  image: Image;
  setLoading?: (loading: boolean) => void;
  saveProject?: () => void;
  setLoadingMessage?: (message: string) => void;
  handlenGenerate: (image: Image) => void;
  showNext?: boolean;
  showGenerate?: boolean;
}

const ModifyScreen: React.FC<ModifyScreenProps> = ({
  title,
  stage,
  handleUpdate,
  handleClose,
  handleBack,
  handleNext,
  image,
  setLoading,
  saveProject,
  setLoadingMessage,
  handlenGenerate,
  showNext,
  showGenerate,
}) => {
  const [feedBackPrompt, setFeedBackPrompt] = React.useState<string>("");
  const [imageObj, setImageObj] = React.useState<Image>(image);
  const [regenerateError, setRegenerateError] = React.useState<boolean>(false);
  const [regenerateErrorMessage, setRegenerateErrorMessage] =
    React.useState<string>("");
  const pollIntervalRef = useRef<number | null>(null);

  const { currentProjectId } = useSelector(
    (state: RootState) => state.projectData,
  );

  const pollJobStatus = async (jobId: string) => {
    try {
      const response = await getJobStatus(jobId);
      const { status, message } = response.data.data;
      if (status === "COMPLETED") {
        stopJobPolling();
        const projectResponse = await fetchProject(currentProjectId || "");
        if (projectResponse.data.data.stage === "Colour_Theme_Refinement") {
          const data = projectResponse.data.data.ai_colour_theme_refinement;
          const lastItem =
            Array.isArray(data) && data.length > 0
              ? data[data.length - 1]
              : null;
          if (lastItem) {
            const newImage = {
              url: lastItem.url,
              score: lastItem.score,
            };
            setImageObj(newImage);
          }
        } else if (projectResponse.data.data.stage === "Graphics_Refinement") {
          const data = projectResponse.data.data.ai_graphics_refinement;
          const lastItem =
            Array.isArray(data) && data.length > 0
              ? data[data.length - 1]
              : null;
          if (lastItem) {
            const newImage = {
              url: lastItem.url,
              score: lastItem.score,
            };
            setImageObj(newImage);
          }
        } else if (
          projectResponse.data.data.stage === "Product_Placement_Refinement"
        ) {
          const data =
            projectResponse.data.data.ai_product_placement_refinement;
          const lastItem =
            Array.isArray(data) && data.length > 0
              ? data[data.length - 1]
              : null;
          if (lastItem) {
            const newImage = {
              url: lastItem.url,
              score: lastItem.score,
            };
            setImageObj(newImage);
          }
        }
        setLoading?.(false);
      } else if (status === "FAILED") {
        stopJobPolling();
        setLoading?.(false);
        setRegenerateError(true);
        setRegenerateErrorMessage(
          message || "Something went wrong while regenerate image.",
        );
      }
    } catch (error) {
      console.error("Error polling theme status:", error);
    }
  };

  const startJobPolling = (jobId: string) => {
    if (pollIntervalRef.current !== null) return;
    pollIntervalRef.current = window.setInterval(() => {
      pollJobStatus(jobId);
    }, 6000);
  };
  const stopJobPolling = () => {
    if (pollIntervalRef.current !== null) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  React.useEffect(() => {
    return () => stopJobPolling();
  }, []);

  const handleRegenerate = async () => {
    try {
      console.error("stage", stage);
      setLoading?.(true);
      setLoadingMessage?.("Regenerating image...");
      if (stage === "Colour_Theme_Refinement") {
        const response = await applyAIColorThemeRegeneration(
          currentProjectId,
          imageObj.url,
          feedBackPrompt,
        );
        console.log("Regeneration response:", response.data);
        startJobPolling(response.data.data.job_id);
      } else if (stage === "Graphics_Refinement") {
        const response = await applyAIGraphicsRegeneration(
          currentProjectId,
          imageObj.url,
          feedBackPrompt,
        );
        console.log("Regeneration response:", response.data);
        startJobPolling(response.data.data.job_id);
      } else if (stage === "Product_Placement_Refinement") {
        const response = await applyAIPlacementRegeneration(
          currentProjectId,
          imageObj.url,
          feedBackPrompt,
        );
        console.log("Regeneration response:", response.data);
        startJobPolling(response.data.data.job_id);
      }
    } catch (error) {
      setLoading?.(false);
      setRegenerateError(true);
      setRegenerateErrorMessage("Something went wrong while regenerate image.");
      console.error("Regeneration error:", error);
    }
  };

  const selectUploadedImage = (url: string) => {
    setImageObj((prev) => ({
      ...prev,
      url: url,
    }));
  };

  const cancelUploadedImage = () => {
    setImageObj((prev) => ({
      ...prev,
      url: image.url,
    }));
  };

  const giveFeedback = async (like: boolean, stage: string) => {
    try {
      const response = await feedback(
        currentProjectId,
        imageObj.url,
        like,
        stage,
      );
      console.log("Feedback response:", response.data);
    } catch (error) {
      console.error("Feedback error:", error);
    }
  };

  const downloadImage = async () => {
    downloadImageFromUrl(imageObj.url);
  };

  return (
    <div>
      <MDConfirmationModel
        open={regenerateError}
        title="Error"
        confirmLabel="Retry"
        description={regenerateErrorMessage}
        onConfirm={() => {
          handleRegenerate();
          setRegenerateError(false);
          setRegenerateErrorMessage("");
        }}
        onClose={() => {
          setRegenerateError(false);
          setRegenerateErrorMessage("");
        }}
      />
      <MDActionHeader
        title={title}
        isModifyMode={false}
        onModify={handleUpdate}
        onClose={handleClose}
        onSaveAs={saveProject}
        onDownload={downloadImage}
      />
      <ImageEditor
        image={imageObj}
        stage={stage}
        setFeedBackPrompt={setFeedBackPrompt}
        handleRegenerate={handleRegenerate}
        selectUploadedImage={selectUploadedImage}
        giveFeedback={giveFeedback}
        cancelUploadedImage={cancelUploadedImage}
      />
      <MDActionFooter
        onGenerate={()=>{
          handlenGenerate(imageObj);
        }}
        showGenerate={showGenerate}
        showNext={showNext}
        onBack={handleBack}
        onNext={() => {
          handleNext(imageObj);
        }}
        nextLabel={stage === "Multi_Angle_View" ? "Finish" : "Next"}
      />
    </div>
  );
};

export default ModifyScreen;
