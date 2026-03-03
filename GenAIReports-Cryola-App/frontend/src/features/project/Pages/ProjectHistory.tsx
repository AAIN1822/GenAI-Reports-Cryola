import React, { useEffect, useState } from "react";
import {
  Box,
  FormControl,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Pagination,
  TextField,
  InputAdornment,
  TableSortLabel,
  Select,
  MenuItem,
  CircularProgress
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import Header from "../../../components/ui/Header";
import MDButton from "../../../components/common/MDButton";
import NewProjectModal from "./NewProjectModal";
import MDLabel from "../../../components/common/MDLabel";
import MDAutocomplete from "../../../components/common/MDAutocomplete";
import type { AppDispatch, RootState } from "../../../redux/store/index";
import { useDispatch, useSelector } from "react-redux";
import { fetchMasterData } from "../../../redux/slices/masterDataSlice";
import { setCurrentProject } from "../../../redux/slices/projectSlice";
import { projectHistory, downloadProjectAssets } from "../../../api/projects";
import type { Project } from "../../../api/model/ProjectHistroyResponse";
import MDTableCellLabel from "../../../components/common/MDTableCellLabel";
import { useNavigate } from "react-router-dom";
import type { MasterDataItem } from "../../../api/model/MasterDataResponse";

type FilterKey = keyof Pick<
  Project,
  "account" | "season" | "sub_brand" | "structure" | "region"
>;

const ProjectHistory: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const { accounts, seasons, subBrands, structures, regions } = useSelector(
    (state: RootState) => state.masterData
  );

  const filterFields: {
    label: string;
    key: FilterKey;
    options: MasterDataItem[];
  }[] = [
    { label: "Account", key: "account", options: accounts },
    { label: "Season/Year", key: "season", options: seasons },
    { label: "Sub Brand", key: "sub_brand", options: subBrands },
    { label: "Structure", key: "structure", options: structures },
    { label: "Region", key: "region", options: regions },
  ];

  const [filters, setFilters] = useState<Record<FilterKey, string>>({
    account: "",
    season: "",
    sub_brand: "",
    structure: "",
    region: "",
  });

  const [projects, setProjects] = useState<Project[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Project;
    direction: "asc" | "desc";
  }>({
    key: "project_description",
    direction: "asc",
  });

  const [page, setPage] = useState(1);
  const [pageCount, setPageCount] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const [openNewProject, setOpenNewProject] = useState(false);

  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState<Record<string, boolean>>({});

  const fetchProjects = async () => {
    try {
      setLoading(true);

      const response = await projectHistory(
        searchTerm,
        filters.account,
        filters.structure,
        filters.sub_brand,
        filters.season,
        filters.region,
        page,
        rowsPerPage,
        sortConfig.key,
        sortConfig.direction
      );

      const projects = response.data.data.projects;
      const totalPages = response.data.data.pagination.total_pages;

      setProjects(projects);

      setPageCount(totalPages);
    } catch (error) {
      console.error("Failed to fetch project history:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    dispatch(fetchMasterData());
  }, [dispatch]);

  useEffect(() => {
    setPage(1);
    fetchProjects();
  }, [rowsPerPage, filters, sortConfig])

  useEffect(() => {
    const handler = setTimeout(() => {
    setPage(1);
    fetchProjects();
  }, 500);

  return () => clearTimeout(handler);
  }, [searchTerm])

  useEffect(() => {
    fetchProjects();
  }, [page])
  
  const downloadAssets = async (project_id: string) => {
    try {
      setDownloading((prev) => ({ ...prev, [project_id]: true }));
      const response = await downloadProjectAssets(project_id);
      const blob = new Blob([response.data], {
      type: "application/zip",
    });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "files.zip";
      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to fetch project assets:", error);
    } finally {
      setDownloading((prev) => ({ ...prev, [project_id]: false }));
    }
  };

  // Autocomplete filter change
  const handleAutocompleteChange = (field: FilterKey, value: string) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
  };

  // Sorting
  const handleSort = (key: keyof Project) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  };

  const columns = [
    { label: "Account", key: "account" },
    { label: "Season/Year", key: "season" },
    { label: "Sub Brand", key: "sub_brand" },
    { label: "Structure", key: "structure" },
    { label: "Region", key: "region" },
    { label: "Project Description", key: "project_description" },
  ];

  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100vw",
        overflowX: "hidden",
        backgroundColor: "#F9FBF9",
        fontWeight: 700,
      }}
    >
      <Header onNewProjectClick={() => setOpenNewProject(true)} />

      {/* FILTER BAR */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "flex-start",
          alignItems: "center",
          px: 8,
          py: 1.5,
          borderBottom: "2px solid #E8F3E8",
          width: "100%",
          backgroundColor: "#fff",
          gap: "20px",
        }}
      >
        {filterFields.map(({ label, key, options }) => (
          <FormControl key={key} sx={{ flex: 1, width: "100%" }}>
            <MDLabel text={label} sx={{ textAlign: "left" }} />
            <MDAutocomplete
              placeholder="Select"
              data={options}
              background="#00892D1A"
              value={filters[key]}
              onChange={(value) => handleAutocompleteChange(key, value || "")}
            />
          </FormControl>
        ))}
      </Box>

      {/* TABLE */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          mt: 2,
        }}
      >
        <Box
          sx={{
            width: "100%",
            maxWidth: "91.5%",
            backgroundColor: "#E1F0E5",
            borderRadius: 5,
            p: 3,
          }}
        >
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2.5,
            }}
          >
            <MDLabel
              text="My Projects"
              sx={{ fontWeight: 400, fontSize: "25px" }}
            />

            <TextField
              variant="outlined"
              size="small"
              placeholder="Search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                backgroundColor: "#000000",
                borderRadius: "25px",
                "& .MuiOutlinedInput-root": {
                  borderRadius: "25px",
                  overflow: "hidden",
                  "& fieldset": {
                    borderRadius: "25px",
                    borderColor: "#D9D9D9",
                  },
                },
                input: {
                  color: "#000000",
                },
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

          <TableContainer
            component={Paper}
            sx={{ borderRadius: 5, width: "100%" }}
          >
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: "whitesmoke" }}>
                  {columns.map((col) => (
                    <TableCell
                      key={col.key}
                      sx={{
                        fontWeight: 500,
                        color: "#667085",
                        fontSize: "13px",
                      }}
                    >
                      <TableSortLabel
                        active={sortConfig.key === col.key}
                        direction={
                          sortConfig.key === col.key
                            ? sortConfig.direction
                            : "asc"
                        }
                        onClick={() => handleSort(col.key as keyof Project)}
                        IconComponent={ArrowDownwardIcon}
                        sx={{ "& .MuiTableSortLabel-icon": { opacity: 1 } }}
                      >
                        {col.label}
                      </TableSortLabel>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>

              <TableBody>
                {loading && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <MDTableCellLabel text="Loading..." />
                    </TableCell>
                  </TableRow>
                )}

                {!loading && projects.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <MDTableCellLabel text="No results found" />
                    </TableCell>
                  </TableRow>
                )}
                {!loading && projects.length > 0 && (
                  projects.map((row, i) => (
                    <TableRow
                      key={i}
                      hover
                      onClick={() => {
                        navigate(`/creative-studio/${row.id}`);
                        setCurrentProject(row.id);
                      }}
                    >
                      <TableCell>
                        {" "}
                        <MDTableCellLabel text={row.account} />
                      </TableCell>
                      <TableCell>
                        {" "}
                        <MDTableCellLabel text={row.season} />
                      </TableCell>
                      <TableCell>
                        {" "}
                        <MDTableCellLabel text={row.sub_brand} />
                      </TableCell>

                      <TableCell>
                        {" "}
                        <MDTableCellLabel text={row.structure} />
                      </TableCell>
                      <TableCell>
                        {" "}
                        <MDTableCellLabel text={row.region} />
                      </TableCell>
                      <TableCell
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <MDTableCellLabel text={row.project_description} />
                        {downloading[row.id] ? (
                          <div className="d-flex"  style={{gap: "8px"}}>
                            <Typography
                            sx={{
                              fontWeight: 400,
                              fontSize: 12
                            }}
                            onClick={(e) => {
                              e.stopPropagation(); 
                            }}
                          >
                            Downloading...
                          </Typography>
                          <CircularProgress color="inherit" size={10} />
                          </div>) : (
                          <Typography
                            sx={{
                              color: "#14AE5C",
                              cursor: "pointer",
                              fontWeight: 400,
                              fontSize: 12,
                              "&:hover": { textDecoration: "underline" },
                            }}
                            onClick={(e) => {
                              e.stopPropagation(); 
                              downloadAssets(row.id);
                            }}
                          >
                            Download Assets
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>

            {/* PAGINATION */}
            {projects.length > 0 && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mt: 1.5,
                  mb: 2,
                }}
              >
                <MDButton
                  text="Previous"
                  leftIcon={<ArrowBackIcon sx={{ fontSize: 18 }} />}
                  onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                  variant="white"
                  style={{
                    height: "35px",
                    width: "100px",
                    marginLeft: 20,
                    border: "1px solid #D0D5DD",
                  }}
                />

                <Pagination
                  count={pageCount}
                  page={page}
                  onChange={(_, value) => setPage(value)}
                  shape="rounded"
                  hideNextButton
                  hidePrevButton
                  
                  sx={{
                    "& .MuiPaginationItem-root": {
                      minWidth: "32px",
                      height: "32px",
                      borderRadius: "7px",
                      color: "#00892D",
                      fontWeight: 400,
                      background: "#DEEEE2",
                    },
                  }}
                />
                <div style={{display: "flex", gap: "8px"}}>
                <MDLabel text="Rows per page:" />
                <Select
                  value={rowsPerPage}
                  onChange={(e) => {
                    setRowsPerPage(Number(e.target.value));
                    setPage(1); // reset page
                  }}
                  sx={{
                  "& .MuiSelect-select": {
                    padding: "6px 10px",
                    fontSize: "14px",
                    fontWeight: 600,
                    color: "#344054"
                  },
                }}
                >
                  <MenuItem value={5}>5</MenuItem>
                  <MenuItem value={10}>10</MenuItem>
                  <MenuItem value={20}>20</MenuItem>
                  <MenuItem value={30}>30</MenuItem>
                </Select>
                <MDButton
                  text="Next"
                  rightIcon={<ArrowForwardIcon sx={{ fontSize: 18 }} />}
                  onClick={() =>
                    setPage((prev) => Math.min(prev + 1, pageCount))
                  }
                  variant="white"
                  style={{
                    height: "35px",
                    width: "80px",
                    marginRight: 15,
                    border: "1px solid #D0D5DD",
                  }}
                />
                </div>
              </Box>
            )}
          </TableContainer>
        </Box>
      </Box>

      {/* Create New Project Modal */}
      <NewProjectModal
        open={openNewProject}
        onSave={(id) => {
          setOpenNewProject(false);
          fetchProjects();
          navigate(`/creative-studio/${id}`);
          dispatch(setCurrentProject(id));
        }}
        onClose={() => {
          setOpenNewProject(false);
        }}
      />
    </Box>
  );
};

export default ProjectHistory;
