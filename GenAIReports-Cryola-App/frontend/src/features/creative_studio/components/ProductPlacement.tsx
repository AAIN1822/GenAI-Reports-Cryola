import React, { useEffect, useState } from "react";
import MDLabel from "../../../components/common/MDLabel";
import MDNumberInput from "../../../components/common/MDNumberInput";
import { Box, Card, CardContent, Link, useTheme } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import ImageDropdown from "./ImageDropdown";
import AddDimension from "./AddDimension";

import { useSelector, useDispatch } from "react-redux";
import type { RootState } from "../../../redux/store"; // make sure this points to your root reducer
import { setProductPlacement } from "../../../redux/slices/projectSlice";

// -------------------- Types --------------------
interface Dimension {
  name: string;
  value: number | string;
}

interface ProductPlacementItem {
  image: string | undefined;
  name: string | undefined;
  dimensions: Dimension[];
}

interface ProductPlacementProps {
  value: any
}

// -------------------- Component --------------------
const ProductPlacement: React.FC<ProductPlacementProps> = ({ value }) => {
  const theme = useTheme();
  const dispatch = useDispatch();

   const { currentProjectId, entities } = useSelector(
      (state: RootState) => state.projectData
    );

  // ---------------- Initial Shape ----------------
  const [shelves, setShelves] = useState<ProductPlacementItem[][]>(value);

  const [addDimension, setAddDimension] = useState<boolean>(false);
  const [selectedShelf, setSelectedShelf] = useState<number | null>(null);
const [selectedColumn, setSelectedColumn] = useState<number | null>(null);

  const handleClose = () => setAddDimension(false);

  useEffect(() => {
    // console.log("sv", value)
    if(JSON.stringify(shelves) !== JSON.stringify(entities[currentProjectId]?.details?.products?.placement)) {
    dispatch(
      setProductPlacement({
        projectId: currentProjectId,
        placement: shelves
      })
    )
  }
  }, [shelves])

  useEffect(() => {
    if(JSON.stringify(value) !== JSON.stringify(shelves)) {
    setShelves(value)
    }
  }, [value])

  // -----------------------------------------
  // 🔹 Add New Dimension to a Specific Column
  // -----------------------------------------
  const addNewDimension = (name: string, value: number | string, shelfIndex: number, colIndex: number) => {
    console.log(name, value, shelfIndex, colIndex)
    setShelves(prev => {
    return prev.map((shelf, sIndex) =>
      sIndex === shelfIndex
        ? shelf.map((col, cIndex) =>
            cIndex === colIndex
              ? {
                  ...col,
                  dimensions: [
                    ...col.dimensions,
                    {
                      name: name,
                      value: value
                    }
                  ]
                }
              : col
          )
        : shelf
    );
  });

    handleClose();
  };

  // -----------------------------------------
  // 🔹 Update Dimension Value
  // -----------------------------------------
  const updateValue = (
    shelfIndex: number,
    colIndex: number,
    dimensionIndex: number,
    newValue: number | null | string
  ) => {
    setShelves(prev => {
    const updated = structuredClone(prev);
    updated[shelfIndex][colIndex].dimensions[dimensionIndex].value = newValue || "";
    return updated;
    });

  };

  // -----------------------------------------
  // 🔹 Add Column
  // -----------------------------------------
  const addColumn = (shelfIndex: number) => {
    const updatedShelves = shelves.map((shelf, idx) =>
    idx === shelfIndex
      ? [
          ...shelf, // copy existing columns
          {
            image: "",
            name: "",
            dimensions: [],
          },
        ]
      : shelf.map(col => ({ ...col })) // optional deep copy of other shelves
  );
      
    setShelves(updatedShelves)
  };

  // -----------------------------------------
  // 🔹 Add Shelf
  // -----------------------------------------
  const addShelf = () => {
    setShelves(prev => [
      ...prev,
      [
        {
          image: "",
          name: "",
          dimensions: []
        }
      ]
    ]);
  };

  const updateImage = (
  img: { image: string | undefined; name: string | undefined } | undefined,
  shelfIndex: number,
  colIndex: number
) => {
  // Deep clone shelves
  const updatedShelves = structuredClone(shelves);
  console.log("in update image", img)
  if(!img) {
    updatedShelves[shelfIndex][colIndex].image = "";
  updatedShelves[shelfIndex][colIndex].name = "";
  }
  if(img?.image && img?.name){
  updatedShelves[shelfIndex][colIndex].image = img.image;
  updatedShelves[shelfIndex][colIndex].name = img.name;

  setShelves(updatedShelves);
  }
};

const deleteShelf = (shelfIndex: number) => {
  setShelves((prev) => prev.filter((_, i) => i !== shelfIndex));
}

const deleteColumn = (shelfIndex: number, colIndex: number) => {
  const updatedShelves = structuredClone(shelves);
  updatedShelves[shelfIndex] = updatedShelves[shelfIndex].filter((__, i) => i !== colIndex);
  setShelves(updatedShelves)
}

const deleteDimension = (shelfIndex: number, colIndex: number, dimIndex: number) => {
  const updatedShelves = structuredClone(shelves);
  updatedShelves[shelfIndex][colIndex].dimensions = updatedShelves[shelfIndex][colIndex].dimensions.filter((__, i) => i !== dimIndex);
  setShelves(updatedShelves)
}

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {shelves.map((shelf, shelfIndex) => (
        <Card key={shelfIndex}>
          <CardContent>
            <div style={{ marginBottom: 20, display: "flex", flexDirection: "column" }}>
              <div style={{display: "flex", justifyContent: "space-between"}}>
              <h4 style={{margin: "2px"}}>Shelf {shelfIndex + 1}</h4>
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
                   deleteShelf(shelfIndex)
                }}
              />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 10, justifyContent: "flex-start" }}>
                {shelf.map((column, colIndex) => (
                  <div
                    key={colIndex}
                    style={{ display: "flex", position: "relative", borderRadius: 4, gap: 12, alignItems: "center", flexWrap: "wrap", border: "1px solid #DEDEDE", padding: "8px" }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <MDLabel text={`Column ${colIndex + 1}`} />
                      <ImageDropdown image={column.image} name={column.name} onChange={(img: {image: string | undefined, name: string | undefined} | undefined) => updateImage(img, shelfIndex, colIndex)} />
                    </div>

                    {/* 🔥 LOOP THROUGH DIMENSIONS */}
                    {column.dimensions.map((dim, dimIndex) => (
                      <div key={dimIndex} style={{ display: "flex", alignItems: "center", gap: 4, border: "1px solid #DEDEDE", padding: "4px" }}>
                        <MDLabel text={dim.name} />
                        <MDNumberInput
                          value={dim.value}
                          onChange={(val) => updateValue(shelfIndex, colIndex, dimIndex, val)}
                        />
                        <DeleteIcon
                          className="delete-btn"
                          style={{
                            cursor: "pointer",
                            color: "#c2bfbf",
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            // prevent selection
                            deleteDimension(shelfIndex, colIndex, dimIndex)
                          }}
                        />
                      </div>
                    ))}

                    <Link
                      component="button"
                      underline="none"
                      sx={{ color: theme.palette.custom.azureBlue, fontSize: 12 }}
                      onClick={() => {
                         setSelectedShelf(shelfIndex);
                          setSelectedColumn(colIndex);
                          setAddDimension(true);
                        
                      }}
                    >
                      Add Dimension
                    </Link>

                    {/* Popup */}
                    <AddDimension
                      isProductDimension={true}
                      open={addDimension}
                      handleClose={handleClose}
                       addDimension={(name, value) => {
                        if (selectedShelf !== null && selectedColumn !== null) {
                          addNewDimension(name, value, selectedShelf, selectedColumn);
                        }
                      }}
                    />
                    <DeleteIcon
                      className="delete-btn"
                      
                      style={{
                        cursor: "pointer",
                        marginLeft: "10px",
                        color: "#c2bfbf",
                        position: "absolute",
                        bottom: 2,
                        right: 0,
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        // prevent selection
                        deleteColumn(shelfIndex, colIndex)
                      }}
                    />
                  </div>
                ))}
                <div style={{display: "flex", justifyContent: "flex-start"}}>
                <Link
                  underline="none"
                  component="button"
                  sx={{ color: theme.palette.custom.azureBlue, fontSize: 12}}
                  onClick={() => addColumn(shelfIndex)}
                >
                  Add Column
                </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      <Box sx={{display: "flex", justifyContent: "flex-start"}}>
      <Link
        component="button"
        underline="none"
        sx={{ color: theme.palette.custom.azureBlue, fontSize: 12, ml: 2 }}
        onClick={addShelf}
      >
        Add Shelf
      </Link>
      </Box>
    </div>
  );
};

export default ProductPlacement;
