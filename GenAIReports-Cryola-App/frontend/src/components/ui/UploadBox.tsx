import React, { useRef, useState, useEffect } from "react";
import { Box, Typography, Button, Stack, IconButton } from "@mui/material";
import FolderOpenOutlinedIcon from "@mui/icons-material/FolderOpenOutlined";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";
import file_upload from "../../assets/images/file_upload.png";
import image_icon from "../../assets/images/image_icon.png";
import { useDispatch } from "react-redux";

import { deleteFromBlob } from "../../api/upload";
import { imageExistApi, imageUploadCustom } from "../../api/image";
import {
  updateProjectField,
  setProductImages,
  removeProductImage,
  removeCategoryImage,
} from "../../redux/slices/projectSlice";
import ImageWithLoader from "../common/MDImageWithLoader";
import LoadingOverlay from "../common/LoadingOverlay";
import TemplateGalleryModel from "../../features/creative_studio/components/TemplateGalleryModel";
import CrayolaGallery from "../../features/creative_studio/components/CrayolaGallery";
import type { TemplateGalleryCategoryEnum } from "../../features/creative_studio/components/TemplateGalleryCategoryEnum";
import type { ImageInfo } from "../../api/model/ImageResponse";
import MDConfirmationModel from "../common/MDConfirmationModel";

interface FileUploadBoxProps {
  multiple?: boolean;
  value?: any;
  category?: TemplateGalleryCategoryEnum;
  path: string;
  height?: string | number;
  project_id?: string;
  isLoading?: boolean;
}

type UploadItem = {
  file: File | null;
  previewUrl: string | undefined;
  uploadedUrl?: string | undefined;
  loading?: boolean;
  name?: string | undefined;
  local?: boolean
};

type valueItem = {
  image: string | undefined;
  name: string | undefined;
  dimensions: [];
};

const FileUploadBox: React.FC<FileUploadBoxProps> = ({
  multiple = false,
  value = [],
  category = "fsdu",
  path = "details.fsdu.image",
  height = "100%",
  project_id = "",
  isLoading = false,
}) => {
  const dispatch = useDispatch();
  const fileInputRef = useRef<HTMLInputElement>(null);

  /** -------------------------
   **    SINGLE STATE
   ** ------------------------*/
  const [items, setItems] = useState<UploadItem[]>([]);
  const [openTemplateGallery, setOpenTemplateGallery] = useState<boolean>(false);
  const [openCrayolaGallery, setOpenCrayolaGallery] = useState<boolean>(false);
  const [overrideResolver, setOverrideResolver] =  useState<((value: "overwrite" | "use_existing") => void) | null>(null);
  const [showOverrideDialog, setShowOverrideDialog] = useState<boolean>(false);
  const [overrideFileName, setOverrideFileName] = useState<string | null>(null);

  const deepEqual = (valueArr: any, itemsArr: any) => {
    if (valueArr.length !== itemsArr.length) return false;

    for (let i = 0; i < valueArr.length; i++) {
      if (
        valueArr[i].image !== itemsArr[i].uploadedUrl ||
        valueArr[i].name !== itemsArr[i].name
      ) {
        return false;
      }
    }
    return true;
  };

  /** Load initial value */

  useEffect(() => {
  // Convert Redux → local format
    const normalizedValue = value.map((v: valueItem) => {
    // check if this item already exists locally
    const existingItem = items.find(
      i => i.uploadedUrl === v.image && i.name === v.name
    );

    return {
      file: null,
      previewUrl: null,
      uploadedUrl: v.image,
      name: v.name,
      loading: false,
      // 🔥 preserve local flag if it already exists
      local: existingItem?.local ?? true,
    };
  });


  // Compare only what matters (image + name)
  const normalizedItems = items.map(item => ({
    uploadedUrl: item.uploadedUrl,
    name: item.name,
  }));
  const normalizedValueComparable = normalizedValue.map((item: Record<string, any>) => ({
    uploadedUrl: item.uploadedUrl,
    name: item.name,
  }));

  // If identical → do NOT update state
  if (deepEqual(normalizedItems, normalizedValueComparable)) {
    return;
  }

  // Replace items from Redux
  setItems(normalizedValue);

}, [value]);


  // Open file picker
  const handleClick = () => fileInputRef.current?.click();

  const askUserOverride = (fileName: string): Promise<"overwrite" | "use_existing"> => {
  return new Promise((resolve) => {
    setOverrideFileName(fileName);
    setOverrideResolver(() => resolve);
    setShowOverrideDialog(true);
  });
};

  const handleUpload = async (file: File) => {
    setItems((prev) =>
      prev.map((p) => (p.file === file ? { ...p, loading: true } : p))
    );

    try {
      const res = await imageExistApi(category as any, file.name);
      console.log("resp", res)
      if(res.data.data.status) {
         // ⏸ waits here until user clicks
        const action = await askUserOverride(file.name);
        console.log("user action", action)
        if (action === "use_existing") {
          const existingUrl = res.data.data.url;

          setItems((prev) =>
            prev.map((p) => (p.file === file ? { ...p, uploadedUrl: existingUrl, loading: false } : p))
          );

           if (category !== "product") {
            // console.log("updating project")
            dispatch(
              updateProjectField({
                projectId: project_id,
                path: path,
                name: file.name,
                value: existingUrl,
              })
            );
          }
          return existingUrl;
        } else {

        const uploadRes = await imageUploadCustom(
          category as any,
          file.name,
          action,
          file
        );

        const blobUrl = uploadRes?.data?.data?.url;

        setItems((prev) =>
          prev.map((p) =>
            p.file === file ? { ...p, uploadedUrl: blobUrl, loading: false, local: true } : p
          )
        );
        if (category !== "product") {
          // console.log("updating project")
          dispatch(
            updateProjectField({
              projectId: project_id,
              path: path,
              name: file.name,
              value: blobUrl,
            })
          );
        }
        return blobUrl;
      }
      } else {
        const res = await imageUploadCustom(category as any, file.name, "overwrite", file)
          const blobUrl = res?.data?.data?.url;

        setItems((prev) =>
          prev.map((p) =>
            p.file === file ? { ...p, uploadedUrl: blobUrl, loading: false, local: true } : p
          )
        );
        if (category !== "product") {
          // console.log("updating project")
          dispatch(
            updateProjectField({
              projectId: project_id,
              path: path,
              name: file.name,
              value: blobUrl,
            })
          );
        }
        return blobUrl;
      } 
    } catch (err) {
      console.error("Upload Failed", err);
    }
  };

  /** Add Files */
  const handleFiles = async (fileList: FileList) => {
    const selectedFiles = Array.from(fileList).filter((f) =>
      f.type.startsWith("image/")
    );

    if (!selectedFiles.length) return;

    const newRecords = selectedFiles.map((file) => ({
      file,
      previewUrl: URL.createObjectURL(file),
      uploadedUrl: undefined,
      name: file.name,
      loading: false,
      local: true,
    }));

    // Update UI immediately
    setItems((prev) => (!multiple ? newRecords : [...prev, ...newRecords]));

    // Upload all files
    let uploadedUrls : string[] = [];
    for (const record of newRecords) {
      const url = await handleUpload(record.file); // ⏸ waits per file
      uploadedUrls.push(url as string);
    }

    // Update items after upload
    setItems((prev) =>
      prev.map((item) => {
        const index = newRecords.findIndex((r) => r.file === item.file);
        return index !== -1
          ? { ...item, uploadedUrl: uploadedUrls[index] }
          : item;
      })
    );

    // -----------------------------------------------------------
    // ✅ Build final array of OBJECTS: { image: url, name: fileName }
    // -----------------------------------------------------------
    const finalBlobObjects = [
      ...newRecords.map((r, idx) => ({
        image: uploadedUrls[idx] || "",
        name: r.name,
      })),
    ].filter((o) => o.image); // Remove empty ones

    // -----------------------------------------------------------
    // 🔥 Send final array of OBJECTS to Redux
    // -----------------------------------------------------------
    if (category === "product") {
      dispatch(
        setProductImages({
          projectId: project_id,
          images: finalBlobObjects, // ⬅️ NOW OBJECTS, NOT URLS
        })
      );
    }
  };

  const handleTemplateImagesSelection = async (images: ImageInfo[]) => {

    const newRecords = images.map((image) => ({
      file: null,
      previewUrl: image.url,
      uploadedUrl: image.url,
      name: image.image_name,
      loading: false,
      local: false
    }));

    // Update UI immediately
    setItems((prev) => (!multiple ? newRecords : [...prev, ...newRecords]));

    

    // -----------------------------------------------------------
    // ✅ Build final array of OBJECTS: { image: url, name: fileName }
    // -----------------------------------------------------------
    const finalBlobObjects = [
      ...newRecords.map((r) => ({
        image: r.uploadedUrl,
        name: r.name,
      })),
    ].filter((o) => o.image); // Remove empty ones

    // -----------------------------------------------------------
    // 🔥 Send final array of OBJECTS to Redux
    // -----------------------------------------------------------
    console.log("c", category, images)
    if (category === "product") {
      dispatch(
        setProductImages({
          projectId: project_id,
          images: finalBlobObjects, // ⬅️ NOW OBJECTS, NOT URLS
        })
      );
    } else {
      dispatch(
          updateProjectField({
            projectId: project_id,
            path: path,
            name: images[0].image_name,
            value: images[0].url,
          })
        );
    }
  };

  const handleCrayolaImagesSelection = async (images: any[]) => {

    const newRecords = images.map((image) => ({
      file: null,
      previewUrl: image.thumbnails["2048px"].url,
      uploadedUrl: image.thumbnails["2048px"].url,
      name: image.filename,
      loading: false,
      local: false
    }));

    // Update UI immediately
    setItems((prev) => (!multiple ? newRecords : [...prev, ...newRecords]));

    

    // -----------------------------------------------------------
    // ✅ Build final array of OBJECTS: { image: url, name: fileName }
    // -----------------------------------------------------------
    const finalBlobObjects = [
      ...newRecords.map((r) => ({
        image: r.uploadedUrl,
        name: r.name,
      })),
    ].filter((o) => o.image); // Remove empty ones

    // -----------------------------------------------------------
    // 🔥 Send final array of OBJECTS to Redux
    // -----------------------------------------------------------
    console.log("c", category, images)
    if (category === "product") {
      dispatch(
        setProductImages({
          projectId: project_id,
          images: finalBlobObjects, // ⬅️ NOW OBJECTS, NOT URLS
        })
      );
    } else {
      dispatch(
          updateProjectField({
            projectId: project_id,
            path: path,
            name: images[0].filename,
            value: images[0].thumbnails["2048px"].url,
          })
        );
    }
  };


  /** Delete File */
  const removeImage = async (index: number) => {
    const removed = items[index];
    console.log("rem", removed);
    if(removed.local) {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, loading: true } : item))
    );

    if (removed.uploadedUrl) {
      try {
        await deleteFromBlob(removed.uploadedUrl);
        setItems((prev) =>
          prev.map((item, i) =>
            i === index ? { ...item, loading: false } : item
          )
        );

        const updated = items.filter((_, i) => i !== index);
        setItems(updated);
        if (category === "product") {
          console.log("deleting from redux")
          dispatch(
            removeProductImage({
              projectId: project_id,
              index: index,
              imageUrl: removed.uploadedUrl,
            })
          );
        } else {
          dispatch(
            removeCategoryImage({
              projectId: project_id,
              path: path,
            })
          );
        }
      } catch (err) {
        console.error("Delete Failed:", err);
      } finally {
        setItems((prev) =>
          prev.map((item, i) =>
            i === index ? { ...item, loading: false } : item
          )
        );
      }
    }
  } else {
     const updated = items.filter((_, i) => i !== index);
        setItems(updated);
        if (category === "product") {
          console.log("deleting from redux")
          dispatch(
            removeProductImage({
              projectId: project_id,
              index: index,
              imageUrl: removed.uploadedUrl,
            })
          );
        } else {
          dispatch(
            removeCategoryImage({
              projectId: project_id,
              path: path,
            })
          );
        }
  }
  };

  return (
    <LoadingOverlay isLoading={isLoading}>
      <Box
        onDrop={(e) => {
          e.preventDefault();
          e.stopPropagation(); // prevent click after drop
          if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);

          // Close file dialog if somehow still open
          fileInputRef.current?.blur();
        }}
        onDragOver={(e) => e.preventDefault()}
        sx={{
          p: 3,
          textAlign: "center",
          backgroundColor: "#fff",
          width: "100%",
          height,
          minHeight: "200px",
          borderRadius: "8px",
          cursor: "pointer",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: items.length > 0 ? "flex-start" : "center",
          overflowY: "auto",
        }}
      >
        <Stack spacing={2} alignItems="center">
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
            {items.length > 0 &&
              items.map((img, idx) => (
                <Box key={idx} sx={{ position: "relative" }}>
                  <ImageWithLoader
                    img={img.uploadedUrl ? img.uploadedUrl : img.previewUrl}
                    idx={idx}
                    loading={img.loading || false}
                  />
                  {/* <img
                  src={img.previewUrl}
                  alt={`Preview ${idx}`}
                  style={{
                    minWidth: 70,
                    maxWidth: 150,
                    borderRadius: 4,
                    border: "1px solid #ccc",
                  }}
                /> */}

                  <Box
                    sx={{
                      backgroundColor: "#FFF",
                      padding: "6px",
                      fontSize: 14,
                      maxWidth: 150,
                      color: "#242424",
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      borderRadius: 1,
                      border: "1px solid #D1D1D1",
                      overflow: "hidden",
                    }}
                  >
                    <img
                      src={image_icon}
                      alt={img.name}
                      style={{ width: 20, height: 20 }}
                    />
                    <Box
                      sx={{
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                        textOverflow: "ellipsis",
                        flex: 1,
                      }}
                    >
                      {img.name}
                    </Box>
                  </Box>
                  <IconButton
                    size="small"
                    sx={{
                      position: "absolute",
                      top: -8,
                      right: 0,
                      backgroundColor: "#fff",
                      border: "1px solid #ccc",
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      removeImage(idx);
                    }}
                    disabled={img.loading}
                  >
                    <HighlightOffIcon fontSize="small" />
                  </IconButton>
                </Box>
              ))}

            {(items.length === 0 || multiple) && (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <img src={file_upload} />
                <Typography sx={{ fontSize: 14 }}>
                  Drag & Drop{" "}
                  <Typography
                    component="span"
                    sx={{ textDecoration: "underline", cursor: "pointer" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleClick();
                    }}
                  >
                    here
                  </Typography>{" "}
                  or{" "}
                  <Typography
                    component="span"
                    sx={{
                      textDecoration: "underline",
                      cursor: "pointer",
                      fontSize: 14,
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleClick();
                    }}
                  >
                    Browse files
                  </Typography>{" "}
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<FolderOpenOutlinedIcon />}
                  sx={{
                    color: "#2C2C2C",
                    border: "1px solid #2C2C2C",
                    fontSize: "12px",
                    textTransform: "none",
                  }}
                  onClick={() => setOpenTemplateGallery(true)}
                >
                  Template Gallery
                </Button>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<FolderOpenOutlinedIcon />}
                  sx={{
                    color: "#2C2C2C",
                    border: "1px solid #2C2C2C",
                    fontSize: "12px",
                    textTransform: "none",
                    marginTop: "8px",
                  }}
                  onClick={() => setOpenCrayolaGallery(true)}
                >
                  Crayola Gallery
                </Button>
              </Box>
            )}
          </Box>
        </Stack>
        {openTemplateGallery && <TemplateGalleryModel 
          open={openTemplateGallery} 
          category={category} 
          singleSelect={category === "product" ? false : true}
          onConfirm={handleTemplateImagesSelection}  
          onClose={() => setOpenTemplateGallery(false)}
          />}
        {openCrayolaGallery && <CrayolaGallery
          open={openCrayolaGallery} 
          category={category} 
          singleSelect={category === "product" ? false : true}
          onConfirm={handleCrayolaImagesSelection}  
          onClose={() => setOpenCrayolaGallery(false)}
          />}
        <input
          ref={fileInputRef}
          type="file"
          hidden
          multiple={multiple}
          accept="image/png, image/jpeg, image/jpg"
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </Box>
      <MDConfirmationModel
              open={showOverrideDialog}
              description={`Image ${overrideFileName} already exists. Do you want overwrite or keep both images?`}
              confirmLabel="Use Existing"
              cancelLabel="Overwrite"
              onClose={() => {
                overrideResolver?.("overwrite");
                setOverrideResolver(null);
                setShowOverrideDialog(false);
              }}
              onConfirm={() => {
                overrideResolver?.("use_existing");
                setOverrideResolver(null);
                setShowOverrideDialog(false);
              }}
            />
    </LoadingOverlay>
  );
};

export default FileUploadBox;
