import React, { useEffect, useState } from "react";
import { Box, Link } from "@mui/material";
import MDLabel from "../../../components/common/MDLabel";
import MDNumberInput from "../../../components/common/MDNumberInput";
import { useTheme } from "@mui/material/styles";
import AddDimension from "./AddDimension";
import DeleteIcon from "@mui/icons-material/Delete";

import { useSelector, useDispatch } from "react-redux";
import type { RootState } from "../../../redux/store"; // make sure this points to your root reducer
import { updateFsduDimensions } from "../../../redux/slices/projectSlice";

interface Dimension {
  name: string;
  value: number | string;
}

type DimensionsState = Dimension[];

interface DimensionsListProps {
  dimensionss: DimensionsState;
}

const DimensionsList: React.FC<DimensionsListProps> = ({ dimensionss }) => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const [dimensions, setDimensions] = useState<DimensionsState>(dimensionss);
  // console.log("dim", dimensionss)
  const [addDimension, setAddDimension] = useState<boolean>(false);

  const { currentProjectId } = useSelector(
    (state: RootState) => state.projectData
  );

  useEffect(() => {
    if (JSON.stringify(dimensionss) !== JSON.stringify(dimensions)) {
      setDimensions(dimensionss);
    }
  }, [dimensionss]);
  const handleClose = () => {
    setAddDimension(false);
  };

  const addNewDimension = (name: string, value: number | string) => {
    const updatedDimensions = [
      ...dimensions,
      { name: name, value: Number(value) },
    ];

    // Update local state
    setDimensions(updatedDimensions);

    handleClose();
    dispatch(
      updateFsduDimensions({
        projectId: currentProjectId,
        dimensions: updatedDimensions,
      })
    );
  };

  const updateValue = (i: number, newValue: number | string | null) => {
    const updatedDimensions = dimensions.map((dim, idx) =>
      idx === i ? { ...dim, value: newValue ?? "" } : dim
    );
    console.log("ud", updatedDimensions);
    // Update local state
    setDimensions(updatedDimensions);

    // Dispatch to Redux with updated values
    dispatch(
      updateFsduDimensions({
        projectId: currentProjectId,
        dimensions: updatedDimensions,
      })
    );
  };

  const deleteDimension = (dimIndex: number) => {
    const updatedDimensions = dimensions.filter((__, i) => i !== dimIndex);
    setDimensions(updatedDimensions);
    dispatch(
      updateFsduDimensions({
        projectId: currentProjectId,
        dimensions: updatedDimensions,
      })
    );
  };

  return (
    <Box
      style={{
        width: "100%",
        padding: "8px",
        background: "white",
        borderRadius: "6px",
        maxHeight: "18vh",
        overflowY: "auto",
      }}
    >
      {dimensionss.map((dim, i) => (
        <div
          key={dim.name}
          style={{
            display: "flex",
            marginBottom: "8px",
            alignItems: "center",
            width: "100%",
          }}
        >
          <MDLabel text={dim.name} />
          <div
            style={{
              display: "flex",
              alignItems: "center",
              marginLeft: "auto",
            }}
          >
            <MDNumberInput
              size="small"
              value={dim.value}
              onChange={(val) => updateValue(i, val)}
            />
            <DeleteIcon
              className="delete-btn"
              style={{
                cursor: "pointer",
                marginLeft: "10px",
                color: "#c2bfbf",
              }}
              onClick={(e) => {
                e.stopPropagation();
                // prevent selection
                deleteDimension(i);
              }}
            />
          </div>
        </div>
      ))}
      <Box
        style={{
          display: "flex",
          justifyContent: "flex-start",
          cursor: "pointer",
          marginTop: 8,
        }}
      >
        <Link
          component="button"
          variant="body2"
          underline="none"
          sx={{ color: theme.palette.custom.azureBlue, fontSize: 12 }}
          onClick={() => setAddDimension(true)}
        >
          Add Dimension
        </Link>
      </Box>
      <AddDimension
        isProductDimension={false}
        open={addDimension}
        handleClose={handleClose}
        addDimension={addNewDimension}
      />
    </Box>
  );
};

export default DimensionsList;
