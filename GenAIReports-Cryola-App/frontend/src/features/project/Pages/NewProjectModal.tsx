import React, { useEffect, useState } from "react";
import { Dialog, DialogContent, Box, Grid } from "@mui/material";
import MDButton from "../../../components/common/MDButton";
import MDAutocomplete from "../../../components/common/MDAutocomplete";
import MDLabel from "../../../components/common/MDLabel";
import MDInput from "../../../components/common/MDInput";
import MDErrorMessage from "../../../components/common/MDErrorMessage";
import { createNewProject, saveAsProject } from "../../../api/projects";
import type { AppDispatch, RootState } from "../../../redux/store/index";
import { useDispatch, useSelector } from "react-redux";
import {
  addMasterItem,
  deleteMasterItem,
  fetchMasterData,
  type MasterField,
} from "../../../redux/slices/masterDataSlice";
import IconButton from "@mui/material/IconButton";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";

interface NewProjectModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (id: string) => void;
  createNew?: boolean;
  formData?: {
    account?: string | undefined;
    season?: string | undefined;
    subBrand?: string | undefined;
    structure?: string | undefined;
    projectDescription?: string | undefined;
    region?: string | undefined;
  };
}

const NewProjectModal: React.FC<NewProjectModalProps> = ({
  open,
  onClose,
  onSave,
  createNew = true,
  formData,
}) => {
  const dispatch = useDispatch<AppDispatch>();

  const { accounts, seasons, subBrands, structures, regions } = useSelector(
    (state: RootState) => state.masterData
  );

  const { currentProjectId } = useSelector(
    (state: RootState) => state.projectData
  );

  const [loading, setLoading] = useState<boolean>(false);

  const [formValues, setFormValues] = useState({
    account: formData?.account || "",
    season: formData?.season || "",
    subBrand: formData?.subBrand || "",
    structure: formData?.structure || "",
    projectDescription: formData?.projectDescription || "",
    region: formData?.region || "",
  });

  const [errors, setErrors] = useState({
    account: false,
    season: false,
    subBrand: false,
    structure: false,
    projectDescription: false,
    region: false,
  });

  useEffect(() => {
    if (open) {
      if (createNew) {
        handleClear();
      }
      if (!createNew && formData) {
        setFormValues({
          account: formData.account || "",
          season: formData.season || "",
          subBrand: formData.subBrand || "",
          structure: formData.structure || "",
          projectDescription: formData.projectDescription || "",
          region: formData.region || "",
        });

        setErrors({
          account: false,
          season: false,
          subBrand: false,
          structure: false,
          projectDescription: false,
          region: false,
        });
      }
      dispatch(fetchMasterData());
    }
  }, [open]);

  const handleInputChange = (field: string, value: string) => {
    setFormValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: false }));
  };

  const handleClear = () => {
    setFormValues({
      account: "",
      season: "",
      subBrand: "",
      structure: "",
      projectDescription: "",
      region: "",
    });
    setErrors({
      account: false,
      season: false,
      subBrand: false,
      structure: false,
      projectDescription: false,
      region: false,
    });
  };

  const handleCreate = async () => {
    const newErrors = {
      account: !formValues.account,
      season: !formValues.season,
      subBrand: !formValues.subBrand,
      structure: !formValues.structure,
      projectDescription: !formValues.projectDescription,
      region: !formValues.region,
    };
    setErrors(newErrors);

    const hasError = Object.values(newErrors).some((v) => v);
    if (hasError) return;

    setLoading(true);
    console.log("Form data:", formValues);

    try {
      setLoading(true);
      const response = await createNewProject(
        formValues.account,
        formValues.structure,
        formValues.subBrand,
        formValues.season,
        formValues.region,
        formValues.projectDescription
      );
      onSave(response.data.data.id);
      handleClear();
      alert(response.data.message);
    } catch (error: any) {
      console.error("Error creating project:", error);
      alert(error?.response?.data?.message || "Something went wrong!");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    const newErrors = {
      account: !formValues.account,
      season: !formValues.season,
      subBrand: !formValues.subBrand,
      structure: !formValues.structure,
      projectDescription: !formValues.projectDescription,
      region: !formValues.region,
    };
    setErrors(newErrors);

    const hasError = Object.values(newErrors).some((v) => v);
    if (hasError) return;

    setLoading(true);
    console.log("Form data:", formValues);

    try {
      setLoading(true);
      const response = await saveAsProject(
        currentProjectId,
        formValues.account,
        formValues.structure,
        formValues.subBrand,
        formValues.season,
        formValues.region,
        formValues.projectDescription
      );
      onSave(response.data.data.id);
      handleClear();
      alert(response.data.message);
    } catch (error: any) {
      console.error("Error creating project:", error);
      alert(error?.response?.data?.message || "Something went wrong!");
    } finally {
      setLoading(false);
    }
  };

  const handleAutocompleteChange = async (
    field: MasterField,
    value: string | null,
    isAddNew?: boolean
  ) => {
    if (!value) return;
    if (isAddNew) {
      await dispatch(addMasterItem({ field, value }));
    }

    setFormValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: false }));
  };

  const handleDelete = async (field: MasterField, id: string | null) => {
    if (!id) return;
    await dispatch(deleteMasterItem({ field, id }));
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogContent sx={{ backgroundColor: "#fff", position: "relative" }}>
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: "absolute",
            right: 4,
            top: 4,
            color: "#666",
          }}
        >
          <HighlightOffIcon fontSize="medium" />
        </IconButton>
        <MDLabel
          text={createNew ? "Create New Project" : "Save As Project"}
          sx={{ fontWeight: 700, fontSize: 20 }}
        />
        <MDLabel
          text={
            createNew
              ? "Launch a new project and define its key parameters"
              : "Save current project with new details"
          }
        />

        <Grid
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: 2.5,
            mb: 3,
            mt: 3,
          }}
        >
          <Box>
            <MDLabel text="Account" />
            <MDAutocomplete
              placeholder="Select"
              data={accounts}
              label="Account"
              value={formValues.account}
              showAddOption={true}
              error={errors.account ? "Account is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange("account", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete("account", id)}
            />
          </Box>
          <Box>
            <MDLabel text="Season/Year" />
            <MDAutocomplete
              placeholder="Select"
              data={seasons}
              label="Season"
              showAddOption={true}
              value={formValues.season}
              error={errors.season ? "Season is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange("season", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete("season", id)}
            />
          </Box>

          <Box>
            <MDLabel text="Sub Brand" />
            <MDAutocomplete
              placeholder="Select"
              data={subBrands}
              label="Sub Brand"
              showAddOption={true}
              value={formValues.subBrand}
              error={errors.subBrand ? "Sub Brand is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange("subBrand", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete("subBrand", id)}
            />
          </Box>
          <Box>
            <MDLabel text="Structure" />
            <MDAutocomplete
              placeholder="Select"
              data={structures}
              label="Structure"
              showAddOption={true}
              value={formValues.structure}
              error={errors.structure ? "Structure is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange("structure", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete("structure", id)}
            />
          </Box>
          <Box>
            <MDLabel text="Region" />
            <MDAutocomplete
              placeholder="Select"
              data={regions}
              label="Region"
              showAddOption={true}
              value={formValues.region}
              error={errors.region ? "Region is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange("region", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete("region", id)}
            />
          </Box>
          <Box>
            <MDLabel text="Project Description" />
            <MDInput
              value={formValues.projectDescription}
              onChange={(e) =>
                handleInputChange("projectDescription", e.target.value)
              }
              sx={{
                width: "100%",
                maxWidth: 300,
                "& .MuiOutlinedInput-root": {
                  borderRadius: "10px",
                },
              }}
            />
            {errors.projectDescription && (
              <MDErrorMessage message={"Project Description is required"} />
            )}
          </Box>
        </Grid>

        <Box sx={{ display: "flex", justifyContent: "center", gap: 4, mt: 4 }}>
          <MDButton
            text="Save"
            variant="green"
            style={{ height: "35px", width: "50%" }}
            onClick={createNew ? handleCreate : handleSave}
            disabled={loading}
            loading={loading}
          />
          <MDButton
            text="Clear"
            variant="gray"
            style={{ height: "35px", width: "50%" }}
            onClick={handleClear}
          />
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default NewProjectModal;
