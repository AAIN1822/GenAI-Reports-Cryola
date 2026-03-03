import React, { useState, useEffect, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import type { AppDispatch, RootState } from "../../../redux/store"; // make sure this points to your root reducer
import { setCurrentProject } from "../../../redux/slices/projectSlice";
import { Box, FormControl, useTheme } from "@mui/material";
import MDLabel from "../../../components/common/MDLabel";
import { useNavigate, useParams } from "react-router-dom";
import Header from "../../../components/ui/Header";
import NewProjectModal from "../../project/Pages/NewProjectModal";
import { updateProject, fetchProject } from "../../../api/projects";
import { updateProjectData } from "../../../redux/slices/projectSlice";
import LoadingOverlay from "../../../components/common/LoadingOverlay";
import { fetchDimensionsMasterData } from "../../../redux/slices/masterDataSlice";
import InputScreen from "../components/InputScreen";
import ImagePreview from "../components/ImagePreview";
import ModifyScreen from "../components/ModifyScreen";
import {
  applyAIColorTheme,
  applyAIGraphics,
  applyAIPlacement,
  fetchMultiAngleView,
  getJobStatus,
} from "../../../api/ai";
import type { Image } from "../../../utils/constants";
import MDConfirmationModel from "../../../components/common/MDConfirmationModel";
import type { ProjectDetails } from "../../../redux/slices/projectSlice";

import "./CreativeStudio.scss";

/**
 * Represents the Creative Studio page where users can upload FSDU and product images,
 * select colors, and configure campaign details.
 */

const modifyProps = {
  Inputs: {
    title: "Refinement of Input Parameters",
    prompt:
      "Please review and adjust the input parameters to ensure they align with the desired design specifications for optimal results.",
  },
  Colour_Theme_Refinement: {
    title: "Refinement of Colouring and Design Application",
    prompt:
      "Side panel color appears slightly uneven – kindly adjust the alignment and fill so the color fits cleanly within the MERCHANDISING DISPLAY panel.",
  },
  Graphics_Refinement: {
    title: "Refinement of Superimposed Images",
    prompt:
      "Noticed the side panel image is getting slightly cut off – please adjust the alignment so it fits cleanly within the MERCHANDISING DISPLAY panel without cropping.",
  },
  Product_Placement_Refinement: {
    title: "Refinement of Product Placement",
    prompt:
      "Ensure each product is placed seamlessly within the MERCHANDISING DISPLAY shelves, maintaining consistency in alignment, accurate dimensions, and overall balance.",
  },
};

type ModifyType =
  | "Inputs"
  | "Colour_Theme_Refinement"
  | "Graphics_Refinement"
  | "Product_Placement_Refinement";

const CreativeStudio: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { project_id } = useParams();
  const dispatch = useDispatch();
  const appDispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [projectState, setProjectState] = useState("Inputs");
  const [modifyState, setModifyState] = useState<ModifyType>("Inputs");
  const [colourThemeData, setColourThemeData] = useState<Image[]>([]);
  const [colourThemeError, setColourThemeError] = useState(false);
  const [colourThemeErrorMessage, setColourThemeErrorMessage] = useState("");
  const [graphicsData, setGraphicsData] = useState<Image[]>([]);
  const [aiGraphicsImage, setAIGraphicsImage] = useState<Image>({
    url: "",
    score: 0,
  });
  const [graphicsError, setGraphicsError] = useState(false);
  const [graphicsErrorMessage, setGraphicsErrorMessage] = useState("");
  const [placementData, setPlacementData] = useState<Image[]>([]);
  const [aiPlacementImage, setAIPlacementImage] = useState<Image>({
    url: "",
    score: 0,
  });
  const [multiAngleData, setMultiAngleData] = useState<any[]>([]);
  const [multiAngleImage, setMultiAngleImage] = useState<{ url: string }>({
    url: "",
  });
  const [multiAngleError, setMultiAngleError] = useState(false);
  const [multiAngleErrorMessage, setMultiAngleErrorMessage] = useState("");
  const [placementError, setPlacementError] = useState(false);
  const [placementErrorMessage, setPlacementErrorMessage] = useState("");
  const [chosenImage, setChosenImage] = useState<Image>({ url: "", score: 0 });
  const [createNew, setCreateNew] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState<string | undefined>(
    undefined,
  );
  const pollIntervalRef = useRef<number | null>(null);

  const originalDetailsRef = useRef<any>(null);
  const chosenImageRef = useRef<Image>({ url: "", score: 0 });
  const aiGraphicsImageRef = useRef<Image>({ url: "", score: 0 });

  const { currentProjectId, entities } = useSelector(
    (state: RootState) => state.projectData,
  );

  // --- State Management ---
  const [labels, setLabels] = useState<{ label: string; value: string }[]>([
    { label: "Account", value: "" },
    { label: "Season/Year", value: "" },
    { label: "Sub Brand", value: "" },
    { label: "Structure", value: "" },
    { label: "Region", value: "" },
    { label: "Project Description", value: "" },
  ]);
  const [openNewProject, setOpenNewProject] = useState(false);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setLoadingMessage("Fetching project data...");
      const response = await fetchProject(project_id || "");
      console.log("Project updated successfully:", response.data);
      const {
        account,
        season,
        sub_brand,
        structure,
        region,
        project_description,
        stage,
      } = response.data.data;
      const newLabels = [
        { label: "Account", value: account },
        { label: "Season/Year", value: season },
        { label: "Sub Brand", value: sub_brand },
        { label: "Structure", value: structure },
        { label: "Region", value: region },
        { label: "Project Description", value: project_description },
      ];
      setLabels(newLabels);
      originalDetailsRef.current = JSON.parse(
        JSON.stringify(response.data.data.details),
      );
      dispatch(
        updateProjectData({
          projectId: response.data.data.id,
          project_data: response.data.data,
        }),
      );
      setProjectState(stage);
      setModifyState(stage as ModifyType);
      const {
        ai_colour_theme_results,
        ai_graphics_results,
        ai_product_placement_results,
        ai_colour_theme_refinement,
        ai_graphics_refinement,
        ai_product_placement_refinement,
        ai_multi_angle_view_results,
      } = response.data.data;
      if (ai_colour_theme_results && ai_colour_theme_results.length > 0) {
        setColourThemeData(ai_colour_theme_results);
      }
      if (
        ai_multi_angle_view_results &&
        ai_multi_angle_view_results.length > 0
      ) {
        setMultiAngleData(ai_multi_angle_view_results);
      }
      if (ai_graphics_results && ai_graphics_results.length > 0) {
        setGraphicsData(ai_graphics_results);
      }
      if (
        ai_product_placement_results &&
        ai_product_placement_results.length > 0
      ) {
        setPlacementData(ai_product_placement_results);
      }
      if (ai_colour_theme_refinement && ai_colour_theme_refinement.length > 0) {
        setChosenImage(
          ai_colour_theme_refinement[ai_colour_theme_refinement.length - 1],
        );
      }
      if (ai_graphics_refinement && ai_graphics_refinement.length > 0) {
        setAIGraphicsImage(
          ai_graphics_refinement[ai_graphics_refinement.length - 1],
        );
      }
      if (
        ai_product_placement_refinement &&
        ai_product_placement_refinement.length > 0
      ) {
        setAIPlacementImage(
          ai_product_placement_refinement[
            ai_product_placement_refinement.length - 1
          ],
        );
      }
    } catch (err) {
      console.error("Failed to update project:", err);
    } finally {
      setLoading(false);
      setLoadingMessage("Fetching project data...");
    }
  };

  useEffect(() => {
    appDispatch(fetchDimensionsMasterData());
  }, [appDispatch]);

  useEffect(() => {
    const newLabels = [
      { label: "Account", value: "" },
      { label: "Season/Year", value: "" },
      { label: "Sub Brand", value: "" },
      { label: "Structure", value: "" },
      { label: "Region", value: "" },
      { label: "Project Description", value: "" },
    ];
    setLabels(newLabels);
    setColourThemeData([]);
    dispatch(setCurrentProject(project_id || ""));
    fetchProjectData();
  }, [project_id]);

  const areAllProductsPlaced = (project: ProjectDetails): boolean => {
    // All product images (source of truth)
    const productImages = project.products.images
      .map((p) => p.image)
      .filter((img): img is string => !!img);

    // All placed product images across shelves & columns
    const placedImages = new Set(
      project.products.placement
        .flat() // flatten shelves -> columns
        .map((column) => column?.image)
        .filter((img): img is string => !!img),
    );

    // Every product must appear in placement
    return productImages.every((img) => placedImages.has(img));
  };

  // helper to update any field in uploads

  const handleUpdateProject = async () => {
    if (currentProjectId) {
      try {
        if (
          entities[currentProjectId].details.fsdu.image &&
          entities[currentProjectId].details.color &&
          areAllProductsPlaced(entities[currentProjectId].details) === true
        ) {
          setLoading(true);
          setLoadingMessage("Updating project...");
          const response = await updateProject(
            currentProjectId,
            entities[currentProjectId].details,
          );
          setProjectState("Colour_Theme");
          applyColourTheme(colourThemeData);
          originalDetailsRef.current = JSON.parse(
            JSON.stringify(response.data.data.details),
          );
        } else {
          if (!entities[currentProjectId].details.fsdu.image) {
            console.log("fsdu", entities);
            alert("Merchandising display image required");
          } else if (
            areAllProductsPlaced(entities[currentProjectId].details) === false
          ) {
            alert("All products must be placed in the display");
          } else {
            if (!entities[currentProjectId].details.color) {
              alert("Color required");
            }
          }
        }
      } catch (err) {
        console.error("Failed to update project:", err);
        setLoading(false);
        setLoadingMessage("");
        alert("Failed to update project. Please try again.");
      }
    }
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      const response = await getJobStatus(jobId);
      const { status, message } = response.data.data;
      if (status === "COMPLETED") {
        stopJobPolling();
        const projectResponse = await fetchProject(project_id || "");
        if (projectResponse.data.data.stage === "Colour_Theme") {
          setColourThemeData(projectResponse.data.data.ai_colour_theme_results);
        } else if (projectResponse.data.data.stage === "Graphics") {
          setGraphicsData(projectResponse.data.data.ai_graphics_results);
        } else if (projectResponse.data.data.stage === "Product_Placement") {
          setPlacementData(
            projectResponse.data.data.ai_product_placement_results,
          );
        } else if (projectResponse.data.data.stage === "Multi_Angle_View") {
          setMultiAngleData(
            projectResponse.data.data.ai_multi_angle_view_results || [],
          );
        }
        setLoading(false);
        setLoadingMessage("");
      } else if (status === "FAILED") {
        stopJobPolling();
        setLoading(false);
        setLoadingMessage("");
        if (response.data.data.stage === "Colour_Theme") {
          setColourThemeError(true);
          setColourThemeErrorMessage(
            message || "Something went wrong while applying the color theme.",
          );
        } else if (response.data.data.stage === "Graphics") {
          setGraphicsError(true);
          setGraphicsErrorMessage(
            message || "Something went wrong while applying the graphics.",
          );
        } else if (response.data.data.stage === "Product_Placement") {
          setPlacementError(true);
          setPlacementErrorMessage(
            message || "Something went wrong while applying the placement",
          );
        } else if (response.data.data.stage === "Multi_Angle_View") {
          setMultiAngleError(true);
          setMultiAngleErrorMessage(
            message ||
              "Something went wrong while fetching the multi-angle view.",
          );
        }
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

  useEffect(() => {
    return () => stopJobPolling();
  }, []);

  const applyColourTheme = async (ai_colour_theme_results: Image[]) => {
    const hasFsduChanged =
      originalDetailsRef.current?.fsdu?.image !==
      entities[currentProjectId].details.fsdu.image;

    const hasColorChanged =
      JSON.stringify(originalDetailsRef.current?.color) !==
      JSON.stringify(entities[currentProjectId].details.color);

    const hasAnyChange = hasFsduChanged || hasColorChanged;

    if (ai_colour_theme_results.length > 0 && !hasAnyChange) {
      setLoading(false);
      setLoadingMessage("");
      return;
    }
    try {
      setLoading(true);
      setLoadingMessage("Applying colour theme...");
      const response = await applyAIColorTheme(project_id || "");
      startJobPolling(response.data.data.job_id);
      // You can dispatch an action to store the theme in Redux if needed
    } catch (error) {
      setLoading(false);
      setLoadingMessage("");
      setColourThemeError(true);
      setColourThemeErrorMessage(
        "Something went wrong while applying the color theme.",
      );
      console.error("Error applying colour theme:", error);
    }
  };

  const applyGraphics = async (
    graphics_data: Image[],
    selectedImage: Image,
    isModified: boolean = false,
  ) => {
    const chosenImageChanged =
      JSON.stringify(selectedImage) !== JSON.stringify(chosenImageRef.current);
    if (
      Array.isArray(graphics_data) &&
      graphics_data.length > 0 &&
      !chosenImageChanged &&
      !isModified
    ) {
      console.error("length", graphics_data.length);
      console.error("chosenImageChanged", chosenImageChanged);
      setLoading(false);
      setLoadingMessage("");
      return;
    }
    try {
      setLoading(true);
      setLoadingMessage("Applying Graphics...");
      const response = await applyAIGraphics(
        project_id || "",
        selectedImage?.url || "",
        selectedImage?.score || 0,
      );
      startJobPolling(response.data.data.job_id);
      chosenImageRef.current = selectedImage;
      // You can dispatch an action to store the theme in Redux if needed
    } catch (error) {
      setLoading(false);
      setLoadingMessage("");
      setGraphicsError(true);
      setGraphicsErrorMessage(
        "Something went wrong while applying the graphics.",
      );
      console.error("Error applying graphics:", error);
    }
  };

  const applyPlacement = async (
    placement_data: Image[],
    selectedImage: Image,
    isModified: boolean = false,
  ) => {
    const chosenImageChanged =
      JSON.stringify(selectedImage) !==
      JSON.stringify(aiGraphicsImageRef.current);
    if (
      Array.isArray(placement_data) &&
      placement_data.length > 0 &&
      !chosenImageChanged &&
      !isModified
    ) {
      console.error("length", placement_data.length);
      console.error("chosenImageChanged", chosenImageChanged);
      setLoading(false);
      setLoadingMessage("");
      return;
    }
    try {
      setLoading(true);
      setLoadingMessage("Applying placement...");
      const response = await applyAIPlacement(
        project_id || "",
        selectedImage?.url || "",
        selectedImage?.score || 0,
      );
      startJobPolling(response.data.data.job_id);
      aiGraphicsImageRef.current = selectedImage;
      // You can dispatch an action to store the theme in Redux if needed
    } catch (error) {
      setLoading(false);
      setLoadingMessage("");
      setPlacementError(true);
      setPlacementErrorMessage(
        "Something went wrong while applying the placement.",
      );
      console.error("Error applying placement:", error);
    }
  };

  const getMultiAngleView = async () => {
    try {
      setLoading(true);
      setLoadingMessage("Fetching multi-angle view...");
      const res = await fetchMultiAngleView(
        currentProjectId,
        aiPlacementImage?.url || "",
        aiPlacementImage?.score || 0,
      );
      startJobPolling(res?.data?.data?.job_id);
    } catch (err) {
      console.error("Fetch Multi Angle View Failed", err);
      setLoading(false);
      setLoadingMessage("");
      setMultiAngleError(true);
      setMultiAngleErrorMessage(
        "Something went wrong while fetching the multi-angle view.",
      );
    }
  };

  const renderScreen = () => {
    switch (projectState) {
      case "Inputs":
        return (
          <InputScreen
            loading={loading}
            handleUpdateProject={handleUpdateProject}
            handleNext={() => {
              setProjectState("Colour_Theme");
            }}
            showNext={colourThemeData.length > 0}
          />
        );
      case "Colour_Theme":
        return (
          <ImagePreview
            title="Colouring and Design Application"
            stage={projectState}
            isModify={true}
            handleModify={() => {
              setProjectState("Colour_Theme_Refinement");
              setModifyState("Colour_Theme_Refinement");
            }}
            images={colourThemeData}
            selectedImage={chosenImage}
            handleSelect={(img: Image) => {
              setChosenImage(img);
            }}
            handleClose={() => navigate("/ProjectHistory")}
            handleBack={() => setProjectState("Inputs")}
            handlenGenerate={() => {
              setProjectState("Graphics");
              applyGraphics(graphicsData, chosenImage);
            }}
            handleNext={() => {
              setProjectState("Graphics");
            }}
            showNext={graphicsData.length > 0}
            saveProject={saveProject}
          />
        );
      case "Graphics":
        return (
          <ImagePreview
            title="Brand Logo and Creative Superimposition"
            stage={projectState}
            isModify={true}
            handleModify={() => {
              setProjectState("Graphics_Refinement");
              setModifyState("Graphics_Refinement");
            }}
            handleSelect={(img: Image) => {
              setAIGraphicsImage(img);
            }}
            images={graphicsData}
            selectedImage={aiGraphicsImage}
            handleClose={() => navigate("/ProjectHistory")}
            handleBack={() => setProjectState("Colour_Theme")}
            handlenGenerate={() => {
              setProjectState("Product_Placement");
              applyPlacement(placementData, aiGraphicsImage);
            }}
            handleNext={() => {
              setProjectState("Product_Placement");
            }}
            showNext={placementData.length > 0}
            saveProject={saveProject}
          />
        );
      case "Product_Placement":
        return (
          <ImagePreview
            title="Product Placement"
            stage={projectState}
            isModify={true}
            handleModify={() => {
              setProjectState("Product_Placement_Refinement");
              setModifyState("Product_Placement_Refinement");
            }}
            handleSelect={(img: Image) => {
              setAIPlacementImage(img);
            }}
            images={placementData}
            selectedImage={aiPlacementImage}
            handleClose={() => navigate("/ProjectHistory")}
            handleBack={() => setProjectState("Graphics")}
            handlenGenerate={() => {
              setProjectState("Multi_Angle_View");
              getMultiAngleView();
            }}
            handleNext={() => {
              setProjectState("Multi_Angle_View");
            }}
            showNext={multiAngleData.length > 0}
            saveProject={saveProject}
          />
        );
      case "Multi_Angle_View":
        return (
          <ImagePreview
            title="Multi-Angle View"
            stage={projectState}
            isModify={false}
            handleSelect={(img: Image) => {
              setMultiAngleImage(img);
            }}
            images={multiAngleData}
            selectedImage={multiAngleImage}
            handleClose={() => navigate("/ProjectHistory")}
            handleBack={() => setProjectState("Product_Placement")}
            handleNext={() => navigate("/ProjectHistory")}
            saveProject={saveProject}
            showGenerate={false}
          />
        );
      case "Colour_Theme_Refinement":
      case "Graphics_Refinement":
      case "Product_Placement_Refinement":
        return (
          <ModifyScreen
            title={modifyProps[modifyState].title}
            stage={modifyState}
            setLoading={setLoading}
            setLoadingMessage={setLoadingMessage}
            image={
              modifyState == "Colour_Theme_Refinement"
                ? chosenImage
                : modifyState == "Graphics_Refinement"
                  ? aiGraphicsImage
                  : aiPlacementImage
            }
            handleUpdate={handleUpdateProject}
            handleClose={() => navigate("/ProjectHistory")}
            handleBack={() =>
              modifyState == "Colour_Theme_Refinement"
                ? setProjectState("Colour_Theme")
                : modifyState == "Graphics_Refinement"
                  ? setProjectState("Graphics")
                  : setProjectState("Product_Placement")
            }
            handlenGenerate={(image) => {
              if (modifyState === "Colour_Theme_Refinement") {
                setProjectState("Graphics");
                setChosenImage(image);
                applyGraphics(graphicsData, image, true);
              } else if (modifyState === "Graphics_Refinement") {
                setProjectState("Product_Placement");
                setAIGraphicsImage(image);
                applyPlacement(placementData, image, true);
              } else if (modifyState === "Product_Placement_Refinement") {
                setProjectState("Multi_Angle_View");
                setAIPlacementImage(image);
                getMultiAngleView();
              }
            }}
            handleNext={() => {
              if (modifyState === "Colour_Theme_Refinement") {
                setProjectState("Graphics");
              } else if (modifyState === "Graphics_Refinement") {
                setProjectState("Product_Placement");
              } else if (modifyState === "Product_Placement_Refinement") {
                setProjectState("Multi_Angle_View");
              }
            }}
            showNext={
              modifyState === "Colour_Theme_Refinement"
                ? graphicsData.length > 0
                : modifyState === "Graphics_Refinement"
                  ? placementData.length > 0
                  : modifyState === "Product_Placement_Refinement"
                    ? multiAngleData.length > 0
                    : false
            }
            saveProject={saveProject}
          />
        );
      default:
        return (
          <InputScreen
            loading={loading}
            handleUpdateProject={handleUpdateProject}
            handleNext={() => {
              setProjectState("Colour_Theme");
            }}
            showNext={colourThemeData.length > 0}
          />
        );
    }
  };

  const saveProject = async () => {
    setOpenNewProject(true);
    setCreateNew(false);
  };

  // --- Render ---
  return (
    <LoadingOverlay isLoading={loading} loadingMessage={loadingMessage}>
      <Box
        sx={{
          backgroundColor: theme.palette.custom.applicationScreen,
          width: "100%",
        }}
      >
        <Header
          onNewProjectClick={() => {
            setOpenNewProject(true);
            setCreateNew(true);
          }}
        />
        <NewProjectModal
          open={openNewProject}
          createNew={createNew}
          formData={{
            account: createNew ? undefined : labels[0].value,
            season: createNew ? undefined : labels[1].value,
            subBrand: createNew ? undefined : labels[2].value,
            structure: createNew ? undefined : labels[3].value,
            region: createNew ? undefined : labels[4].value,
            projectDescription: createNew ? undefined : labels[5].value,
          }}
          onSave={(id) => {
            setOpenNewProject(false);
            navigate(`/creative-studio/${id}`);
            if (createNew) {
              setColourThemeData([]);
              setProjectState("Inputs");
            }
            dispatch(setCurrentProject(id));
          }}
          onClose={() => {
            setOpenNewProject(false);
          }}
        />
        {/* Top Dropdown Section */}
        <Box
          sx={{
            marginLeft: "70px",
            marginRight: "70px",
          }}
        >
          <Box
            sx={{
              display: "flex",
              gap: 5,
              borderBottom: "1px solid #E1F0E5",
            }}
          >
            {labels.map(({ label, value }) => (
              <FormControl
                key={label}
                sx={{
                  flex: 1,
                  width: "100%",
                  mb: 1,
                  backgroundColor: "transparent !important",
                }}
              >
                <MDLabel text={label} sx={{ textAlign: "left" }} />
                <Box
                  sx={{
                    fontSize: "14px",
                    height: "35px",
                    borderRadius: "8px",
                    padding: "6px 16px",
                    backgroundColor: theme.palette.custom.inputScreenBackground,
                    display: "flex",
                    justifyContent: "flex-start",
                    mt: 0.5,
                  }}
                >
                  {value}
                </Box>
              </FormControl>
            ))}
          </Box>
          {renderScreen()}
        </Box>

        {/* Main Upload & Color Section */}
      </Box>
      {colourThemeError && (
        <MDConfirmationModel
          open={colourThemeError}
          title="Error"
          confirmLabel="Retry"
          description={colourThemeErrorMessage}
          onClose={() => {
            setColourThemeError(false);
            setProjectState("Inputs");
          }}
          onConfirm={() => {
            setColourThemeError(false);
            applyColourTheme([]);
          }}
        />
      )}
      {graphicsError && (
        <MDConfirmationModel
          open={graphicsError}
          title="Error"
          confirmLabel="Retry"
          description={graphicsErrorMessage}
          onClose={() => {
            setGraphicsError(false);
            setProjectState("Colour_Theme");
          }}
          onConfirm={() => {
            setGraphicsError(false);
            applyGraphics([], chosenImage);
          }}
        />
      )}
      {placementError && (
        <MDConfirmationModel
          open={placementError}
          title="Error"
          confirmLabel="Retry"
          description={placementErrorMessage}
          onClose={() => {
            setPlacementError(false);
            setProjectState("Graphics");
          }}
          onConfirm={() => {
            setPlacementError(false);
            applyPlacement([], chosenImage);
          }}
        />
      )}
      {multiAngleError && (
        <MDConfirmationModel
          open={multiAngleError}
          title="Error"
          confirmLabel="Retry"
          description={multiAngleErrorMessage}
          onClose={() => {
            setMultiAngleError(false);
            setProjectState("Product_Placement");
          }}
          onConfirm={() => {
            setMultiAngleError(false);
            getMultiAngleView();
          }}
        />
      )}
    </LoadingOverlay>
  );
};

export default CreativeStudio;
