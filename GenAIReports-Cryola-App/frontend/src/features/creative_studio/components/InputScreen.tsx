import React from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../../../redux/store"; // make sure this points to your root reducer
import { Box, Chip, useTheme } from "@mui/material";
import MDLabel from "../../../components/common/MDLabel";
import UploadBox from "../../../components/ui/UploadBox";
import ProductPlacement from "../components/ProductPlacement";
import MDSectionAccordion from "../../../components/common/MDSectionAccordion";

import "../Pages/CreativeStudio.scss";
import DimensionsList from "../components/Dimensions";
import MDButton from "../../../components/common/MDButton";

import arrow_right_circle from "../../../assets/images/arrow_right_circle.png";
import UploadSectionHeader from "../components/UploadSectionHeader";
import MDColorPicker from "../../../components/common/MDColorPicker";
import { TemplateGalleryCategoryEnum } from "../components/TemplateGalleryCategoryEnum";
import KeyboardArrowRightRoundedIcon from "@mui/icons-material/KeyboardArrowRightRounded";

interface inputScreenProps {
  loading: boolean;
  handleUpdateProject: () => void;
  showNext?: boolean;
  handleNext?: () => void;
}

const InputScreen: React.FC<inputScreenProps> = ({
  loading,
  handleUpdateProject,
  showNext,
  handleNext,
}) => {
  const theme = useTheme();

  const { currentProjectId, entities } = useSelector(
    (state: RootState) => state.projectData,
  );
  const [productDetailsOpen, setProductDetailsOpen] = React.useState(true);

  const getNestedValue = (obj: any, path: string) => {
    // console.log('spp', path.split('.').reduce((acc, key) => acc?.[key], obj))
    return path.split(".").reduce((acc, key) => acc?.[key], obj);
  };

  return (
    <Box
      sx={{
        display: "flex",
        gap: 1.5,
        p: 1,
        backgroundColor: theme.palette.custom.inputScreenBackground,
        borderRadius: 2,
        mt: 1,
        height: "75vh", // or any fixed outer height you want
        overflowY: "auto", // prevent outer scroll
      }}
    >
      {/* FSDU Image */}
      <Box
        sx={{
          width: "18%",
          display: "flex",
          flexDirection: "column",
          maxHeight: "73vh",
          padding: 1,
        }}
      >
        <UploadSectionHeader text="Merchandising Display Details" />
        <MDSectionAccordion
          title="Image Upload"
          detailsSx={{
            minHeight: "30vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <UploadBox
            multiple={false}
            isLoading={loading}
            category={TemplateGalleryCategoryEnum.FSDU}
            path="details.fsdu"
            height="35vh"
            project_id={currentProjectId}
            value={
              currentProjectId &&
              entities[currentProjectId]?.details?.fsdu?.image
                ? [entities[currentProjectId].details.fsdu]
                : []
            }
          />
        </MDSectionAccordion>
        <MDSectionAccordion
          title="Dimensions"
          detailsSx={{
            display: "flex",
            justifyContent: "center",
          }}
        >
          <DimensionsList
            dimensionss={
              currentProjectId &&
              entities[currentProjectId]?.details?.fsdu.dimensions
                ? entities[currentProjectId]?.details?.fsdu.dimensions
                : []
            }
          />
        </MDSectionAccordion>
      </Box>
      {/* Brand Image Section */}
      <Box
        sx={{
          width: "20%",
          display: "flex",
          flexDirection: "column",
          maxHeight: "75vh",
          overflow: "hidden",
        }}
      >
        <UploadSectionHeader text="Brand Creatives" />
        <MDSectionAccordion
          title="Image Upload"
          detailsSx={{
            backgroundColor: "#E1F1E5",
            maxHeight: "70vh",
            paddingBottom: "50px",
            overflowY: "auto",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column" }}>
            {[
              {
                label: "Header Image",
                category: TemplateGalleryCategoryEnum.HEADER,
                path: "details.header",
              },
              {
                label: "Footer Image",
                category: TemplateGalleryCategoryEnum.FOOTER,
                path: "details.footer",
              },
              {
                label: "Side Panel Image",
                category: TemplateGalleryCategoryEnum.SIDEPANEL,
                path: "details.sidepanel",
              },
              {
                label: "Shelf Image",
                category: TemplateGalleryCategoryEnum.SHELF,
                path: "details.shelf",
              },
            ].map(({ label, path, category }) => {
              const imageValue = currentProjectId
                ? getNestedValue(entities[currentProjectId], path)
                : null;
              return (
                <Box
                  key={label}
                  sx={{
                    mb: 2,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                  }}
                >
                  <Chip
                    label={label}
                    size="small"
                    sx={{
                      position: "relative",
                      top: 4,
                      fontSize: 12,
                      fontWeight: 600,
                      backgroundColor: "#CFF7D3",
                      borderRadius: 0,
                    }}
                  />
                  <UploadBox
                    multiple={false}
                    path={path}
                    category={category}
                    project_id={currentProjectId}
                    isLoading={loading}
                    value={
                      currentProjectId && imageValue?.image ? [imageValue] : []
                    }
                  />
                </Box>
              );
            })}
          </div>
        </MDSectionAccordion>
      </Box>

      {/* FSDU Color Picker */}

      {/* Product Image */}
      <Box
        sx={{
          width: "40%",
          display: "flex",
          flexDirection: "column",
          maxHeight: "80vh",
          padding: 1,
          overflowY: "hidden",
        }}
      >
        <UploadSectionHeader text="Product Details" />
        <MDSectionAccordion
          title="Product Images"
          detailsSx={{
            minHeight: "20vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
          onToggle={(expanded) => setProductDetailsOpen(expanded)}
        >
          <UploadBox
            multiple
            category={TemplateGalleryCategoryEnum.PRODUCT}
            path="details.products.images"
            height="35vh"
            project_id={currentProjectId}
            isLoading={loading}
            value={
              currentProjectId &&
              entities[currentProjectId]?.details?.products.images
                ? entities[currentProjectId]?.details?.products.images
                : []
            }
          />
        </MDSectionAccordion>

        <MDSectionAccordion
          title="Product Placement"
          detailsSx={{
            display: "flex",
            justifyContent: "flex-start",
            alignItems: "center",
          }}
        >
          <Box
            style={{
              width: "100%",
              maxHeight: productDetailsOpen ? "20vh" : "55vh",
              overflowY: "auto",
            }}
          >
            <ProductPlacement
              value={
                currentProjectId &&
                entities[currentProjectId]?.details?.products.placement
                  ? entities[currentProjectId]?.details?.products.placement
                  : [[]]
              }
            />
          </Box>
        </MDSectionAccordion>
      </Box>
      <Box sx={{ width: "18%", display: "flex", flexDirection: "column" }}>
        <UploadSectionHeader text="Merchandising Display - Color" />
        <MDLabel text="Color Picker" sx={{ fontSize: 14, mb: 1 }} />
        <Box
          sx={{
            backgroundColor: "white",
            borderRadius: 2,
            p: 1,
            flex: 1,
            overflowY: "auto",
            minHeight: 0,
          }}
        >
          <MDColorPicker
            defaultColor={
              currentProjectId && entities[currentProjectId]?.details?.color
                ? entities[currentProjectId]?.details?.color
                : "#ffffff"
            }
          />
        </Box>
        <Box
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginTop: "8px",
            gap: 8,
            alignItems: "center",
          }}
        >
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
            onClick={handleUpdateProject}
          />
          {showNext && (
            <MDButton
              text={"Next"}
              rightIcon={
                <KeyboardArrowRightRoundedIcon sx={{ fontSize: 25 }} />
              }
              onClick={handleNext}
              width="90px"
              variant="white"
            />
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default InputScreen;
