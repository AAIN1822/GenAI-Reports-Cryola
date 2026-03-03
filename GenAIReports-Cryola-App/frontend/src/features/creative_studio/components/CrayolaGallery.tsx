import React, { useState, useEffect } from "react";
import {
  Box,
  Modal,
  Typography,
  Checkbox,
  InputAdornment,
  TextField,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";

import type { ImageInfo } from "../../../api/model/ImageResponse";
import type { TemplateGalleryCategoryEnum } from "./TemplateGalleryCategoryEnum";
import { getCrayolaGallery } from "../../../api/image";
import MDLabel from "../../../components/common/MDLabel";
import MDButton from "../../../components/common/MDButton";
import GridViewIcon from '@mui/icons-material/GridView';
import ListIcon from '@mui/icons-material/List';

interface CrayolaGalleryProps {
  open: boolean;
  category: TemplateGalleryCategoryEnum;
  singleSelect?: boolean;
  onClose: () => void;
  onConfirm?: (selected: ImageInfo[]) => void;
}

const CrayolaGallery: React.FC<CrayolaGalleryProps> = ({
  open,
  category,
  singleSelect = false,
  onClose,
  onConfirm,
}) => {
  const [images, setImages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [selectedImages, setSelectedImages] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [queryKey, setQueryKey] = useState(0);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const scrollRef = React.useRef<HTMLDivElement>(null);

  const loadImages = async (pageToLoad = 1) => {
      if (loadingMore || !hasMore) return;
      if(pageToLoad > 1) {
        setLoading(false);
        setLoadingMore(true);
      }
      setErrorMsg("");

    try {
      const res = await getCrayolaGallery(searchTerm, pageToLoad);
      const result = res.data.data.items ?? [];
      setImages((prev) => 
      (pageToLoad === 1
        ? result 
        : [...prev, ...result])
      );
      setTotalCount(res.data.data.total_count || 0);
    setHasMore(images.length + result.length < (res.data.data?.total_count || 0))
    } catch (error: any) {
      setErrorMsg(error?.response?.data?.message || "Failed to load images.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const toggleSelect = (img: any) => {
    setSelectedImages((prev) => {
      const exists = prev.some((x) => x.thumbnails["2048px"].url === img.thumbnails["2048px"].url);

      if (singleSelect) {
        return exists ? [] : [img];
      }

      if (exists) {
        return prev.filter((x) => x.thumbnails["2048px"].url !== img.thumbnails["2048px"].url);
      } else {
        return [...prev, img];
      }
    });
  };

  const handleScroll = () => {
  if (!scrollRef.current || loadingMore || !hasMore) return;

  const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;

  if (scrollTop + clientHeight >= scrollHeight - 100) {
    setPage((prevPage) => prevPage + 1);
  }
};

  useEffect(() => {
    if (!open || !category) return;
    loadImages(page);
  }, [page, queryKey, open, category]);

  const resetAndReload = () => {
    setImages([]);
    setHasMore(true);
    setSelectedImages([]);
    setLoading(true);

    setPage(1);          // page might already be 1
    setQueryKey((k) => k + 1); // 🔥 forces reload
  };

  useEffect(() => {
    if (!open || !category) return;

    const handler = setTimeout(() => {
      resetAndReload();
    }, 500);

    return () => clearTimeout(handler);
  }, [searchTerm]);

  useEffect(() => {
    if (open && category) {
      resetAndReload();
      setSearchTerm("");
    }
  }, [open, category]);

  return (
    <Box textAlign="center">
      <Modal open={open} onClose={onClose}>
        <Box sx={modalStyle}>
          {/* Header */}
          <Box sx={{ flex: "0 0 auto" }}>
            <MDLabel
              text="Crayola Gallery"
              sx={{ fontSize: 20, textAlign: "center", fontWeight: 500 }}
            />
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                width: "100%",
                mt: 1,
              }}
            >
              {/* Category Label */}
              {/* <MDLabel
                text={CategoryDisplayName[category] || category}
                sx={{ fontSize: 19, fontWeight: 500 }}
              /> */}

              {/* Search Field */}
              <TextField
                variant="outlined"
                size="small"
                placeholder="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{
                  width: "100%",
                  backgroundColor: "#ffffff",
                  borderRadius: "25px",
                  "& .MuiOutlinedInput-root": {
                    borderRadius: "25px",
                    overflow: "hidden",
                    "& fieldset": {
                      borderRadius: "25px",
                      borderColor: "#D9D9D9",
                    },
                  },
                  input: { color: "#000000" },
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <SearchIcon sx={{ color: "#000000" }} />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
            <Box  
            sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                width: "100%",
                mt: 1,
                mb: 1
              }}
              >
                1 - {images.length} of {totalCount} images
                <Box sx={{ display: "flex", gap: 1 }}>
                  <MDButton 
                    leftIcon={<GridViewIcon />}
                    text="Grid"
                    variant={viewMode === "grid" ? "green" : "outline"}
                    onClick={() => setViewMode("grid")}
                  />
                  <MDButton 
                    leftIcon={<ListIcon />}
                    text="List"
                    variant={viewMode === "list" ? "green" : "outline"}
                    onClick={() => setViewMode("list")}
                  />
                </Box>
              </Box>
          </Box>

          {/* Content Area */}
          <Box sx={contentArea}>
            {loading && (
              <Box sx={centerBox}>
                <Typography>Loading...</Typography>
              </Box>
            )}

            {!loading && errorMsg && (
              <Box sx={centerBox}>
                <Typography sx={{ color: "red" }}>{errorMsg}</Typography>
              </Box>
            )}

            {!loading && !errorMsg && (images?.length ?? 0) <= 0 && (
              <Box sx={centerBox}>
                <Typography>No results found</Typography>
              </Box>
            )}

            {!loading && !errorMsg && category && (
              <Box
                component="section"
                ref={scrollRef}
                onScroll={handleScroll}
                sx={{
                  overflowY: "auto",
                  overflowX: "hidden",
                  px: 1,
                  py: 1,
                  height: "100%"
                }}
              >
                <Box
                  justifyItems="center"
                  alignContent="start"
                  sx={{
                    display: viewMode === "grid" ? "grid" : "flex",
                    gridTemplateColumns:
                    viewMode === "grid"
                        ? "repeat(auto-fill, minmax(200px, 1fr))"
                        : "none",
                    flexDirection: viewMode === "list" ? "column" : "unset",
                    gap: 2,
                    transition: "all 0.15s ease-in-out",
                  }}
                >
                  {images?.map((img, index) => {
                    const isSelected = selectedImages.some(
                      (x) => x.thumbnails["2048px"].url === img.thumbnails["2048px"].url
                    );

                    return (
                      <Box
                        key={index}
                        sx={{
                          ...imgCard,
                           display: viewMode === "list" ? "flex" : "flex",
                            flexDirection: viewMode === "list" ? "row" : "column",
                            alignItems: viewMode === "list" ? "center" : "stretch",
                            gap: viewMode === "list" ? 1 : 0,
                          border: isSelected
                            ? "2px solid #14AE5C"
                            : "1px solid #ddd",
                          position: "relative",
                          justifyContent: viewMode === "list" ? "flex-start" : "center",
                        }}
                      >
                        {/* Checkbox Top-Right */}
                        <Box
                          sx={{
                            position: "absolute",
                            top: 0,
                            right: 1,
                            zIndex: 1,
                          }}
                        >
                          <Checkbox
                            checked={isSelected}
                            onChange={() => toggleSelect(img)}
                            size="small"
                          />
                        </Box>

                        <Box sx={imgWrapper} 
                            width={viewMode === "list" ? 80 : "100%"}
                            height={viewMode === "list" ? 60 : 150}
                            >
                          <img
                            src={viewMode === "list" ? img.thumbnails["2048px"].url : img.thumbnails["2048px"].url}
                            alt={img.filename || "template"}
                            style={{
                              width: "100%",
                              height: "100%",
                              objectFit: "contain",
                            }}
                          />
                        </Box>

                        {img.filename && (
                          <MDLabel
                            text={img.filename}
                            sx={{
                              fontSize: 14,
                              fontWeight: 500,
                              mt: 1,
                              textAlign: "center",
                              px: 1,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                              width: "auto",
                            }}
                          />
                        )}
                      </Box>
                    );
                  })}
                </Box>
              </Box>
            )}
            {loadingMore && (
              <Box sx={{ textAlign: "center", py: 2 }}>
                <Typography>Loading more...</Typography>
              </Box>
            )}
          </Box>

          {/* Bottom Buttons */}
          <Box
            sx={{
              flex: "0 0 auto",
              display: "flex",
              justifyContent: "flex-end",
              gap: 2,
              mt: 2,
              borderTop: "1px solid #eee",
              pt: 2,
            }}
          >
            <Box sx={{ width: "120px" }}>
              <MDButton text={"Cancel"} variant="outline" onClick={onClose} />
            </Box>
            <Box sx={{ width: "120px" }}>
              <MDButton
                text={"Confirm"}
                disabled={selectedImages.length === 0}
                variant="green"
                onClick={() => {
                  if (onConfirm) onConfirm(selectedImages);
                  onClose();
                }}
              />
            </Box>
          </Box>
        </Box>
      </Modal>
    </Box>
  );
};

/* Styles */

const modalStyle = {
  position: "absolute" as const,
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "60%",
  maxWidth: 1200,
  minHeight: "70vh",
  maxHeight: "90vh",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  bgcolor: "white",
  p: 3,
  pt: 2,
  borderRadius: "10px",
};

const contentArea = {
  flex: "1 1 auto",
  display: "flex",
  flexDirection: "column",
  minHeight: 0,
};

const centerBox = {
  flex: 1,
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const imgCard = {
  background: "#fff",
  height: "auto",
  padding: "8px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  borderRadius: "6px",
  border: "1px solid #ddd",
  boxSizing: "border-box",
  width: "100%",
};

const imgWrapper = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  overflow: "hidden",
};

export default CrayolaGallery;
