import React, { useState, useEffect } from "react";
import {
  FormControl,
  MenuItem,
  Select,
  Box,
  Typography,
  Tooltip,
} from "@mui/material";
import type { SelectChangeEvent } from "@mui/material";

import { useSelector } from "react-redux";
import type { RootState } from "../../../redux/store"; 
import folder from "../../../assets/images/folder.png";

type ImageItem = {
  image: string | undefined;
  name: string | undefined;
};

interface ImageDropdownProps {
  image: string | undefined,
  name: string | undefined,
  onChange : (img: ImageItem | undefined) => void,
}

const ImageDropdown: React.FC<ImageDropdownProps> = ({onChange, image, name}) => {
  const [selected, setSelected] = useState<ImageItem | undefined>({ image: image, name: name});
  const [images, setImages] = useState<ImageItem[] | []>([]);

  const { currentProjectId, entities } = useSelector(
      (state: RootState) => state.projectData
    );
  
  useEffect(() => {
    const project = entities[currentProjectId] || null;
    if(project) {
    const product_images = [
        ...project?.details?.products?.images?.map((img) => ({ image: img.image, name: img.name })),
      ];
      setImages(product_images)
    }
  }, [currentProjectId, entities])

  useEffect(() => {
    if (!selected) return;
    if (images.length === 0) return;

    const stillExists = images.some(img => img.image === selected.image);

    if (!stillExists) {
      setSelected(undefined);
      onChange(undefined);
    }
  }, [images]);
  
  const handleChange = (event: SelectChangeEvent) => {
    const selectedImage: ImageItem | undefined = images.find(img => img.image == event.target.value);
    setSelected(selectedImage);
    console.log("image value", selectedImage, event.target.value)
    onChange(selectedImage)
  };


  return (
    <FormControl sx={{width: "110px", padding: "2px 4px"}} size="small">
      <Select
        value={selected?.image}
        onChange={handleChange}
        displayEmpty
        sx={{
        "& .MuiSelect-select": {
          padding: "6px 8px !important",   // ← your custom padding
          minHeight: "unset",
        }
      }}
        renderValue={(value) => {
          if (!value) return (<Box style={{display: "flex", alignItems: "center", fontSize: 12}}><img src={folder} alt="Product" style={{width: 15, marginRight: 8}} />Product</Box>);

          if (!selected?.image) return value;

          return (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Tooltip title={selected?.name || ""} arrow placement="top">
              <img
                src={selected.image}
                alt={selected.name}
                style={{ width: 30, height: 30, objectFit: "cover", borderRadius: 4 }}
              />
              </Tooltip>
            </Box>
          );
        }}
      >
        {images.map((img) => (
          <MenuItem key={img.name} value={img.image}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <img
                src={img.image}
                alt={img.name}
                style={{ width: 40, height: 40, objectFit: "cover", borderRadius: 4 }}
              />
              <Typography>{img.name}</Typography>
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default ImageDropdown;
