import React, { useState } from "react";
import { Box, Typography, Button, Avatar, Menu } from "@mui/material";
import FolderOpenOutlinedIcon from "@mui/icons-material/FolderOpenOutlined";
import AddCircleOutlineOutlinedIcon from "@mui/icons-material/AddCircleOutlineOutlined";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import crayola_logo from "../../assets/images/crayola_logo.png";
import { useNavigate } from "react-router-dom";
import MDConfirmationModel from "../common/MDConfirmationModel";
import { logout } from "../../api/auth";
import { isSSO, logoutUser } from "../../utils/helpers";
import ChangePasswordModal from "../../features/profile/ChangePassordModel";

interface HeaderProps {
  onNewProjectClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onNewProjectClick }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [logoutPopup, setLogoutPopup] = useState(false);
  const [changePasswordPopup, setChangePasswordPopup] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    try {
      setLoading(true);
      const response = await logout();
      console.log("Logout Response:", response.data);
      logoutUser();
      navigate("/");
      setLogoutPopup(false);
    } catch (error: any) {
      alert(error?.response?.data?.message || "Something went wrong!");
      console.error("Login error:", error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ---------------- HEADER ---------------- */}
      <Box
        sx={{
          width: "100%",
          backgroundColor: "#006400",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          px: 2,
          py: 1,
          position: "sticky",
          top: 0,
          left: 0,
          zIndex: 1000,
        }}
      >
        {/* ✅ Left: Logo + Titles */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <img
            src={crayola_logo}
            alt="Crayola Logo"
            style={{ width: "80px", height: "auto" }}
          />
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-start",
              color: "white",
              lineHeight: 1.1,
            }}
          >
            <Typography
              variant="subtitle1"
              sx={{
                fontWeight: 700,
                fontSize: "17px",
              }}
            >
              Merchandising Display
            </Typography>
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 700,
                fontSize: "15px",

                mt: 0.2,
              }}
            >
              Creative Studio
            </Typography>
          </Box>
        </Box>

        {/* right: buttons + avatar */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, pr: 2 }}>
          <Button
            startIcon={<FolderOpenOutlinedIcon sx={{ color: "#000" }} />}
            sx={{
              backgroundColor: "whitesmoke",
              color: "#000",
              textTransform: "none",
              fontWeight: 500,
              px: 2.5,
            }}
            onClick={() => navigate("/ProjectHistory")}
          >
            Project History
          </Button>

          <Button
            startIcon={
              <AddCircleOutlineOutlinedIcon sx={{ color: "#006400" }} />
            }
            onClick={onNewProjectClick}
            sx={{
              backgroundColor: "#FFD700",
              color: "#006400",
              textTransform: "none",
              fontWeight: 500,
              borderRadius: 2,
              px: 2.5,
            }}
          >
            New Project
          </Button>

          {/* avatar */}
          <Avatar
            sx={{
              bgcolor: "#2E2E2E",
              width: 36,
              height: 36,
              cursor: "pointer",
            }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <PersonOutlineOutlinedIcon sx={{ color: "#fff", fontSize: 22 }} />
          </Avatar>
        </Box>
      </Box>
      {/* MENU */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        {!isSSO() && (
          <Typography
            sx={{ cursor: "pointer", p: 1 }}
            onClick={() => {
              setAnchorEl(null);
              setChangePasswordPopup(true);
            }}
          >
            ChangePassword
          </Typography>
        )}

        <Typography
          sx={{ cursor: "pointer", p: 1 }}
          onClick={() => {
            setAnchorEl(null);
            setLogoutPopup(true);
          }}
        >
          Logout
        </Typography>
      </Menu>
      <MDConfirmationModel
        title="Logout"
        loading={loading}
        open={logoutPopup}
        description="Are you sure that you want to logout?"
        confirmLabel="Yes"
        cancelLabel="No"
        onClose={() => {
          setLogoutPopup(false);
        }}
        onConfirm={handleLogout}
      ></MDConfirmationModel>

      <ChangePasswordModal
        open={changePasswordPopup}
        onClose={() => {
          setChangePasswordPopup(false);
        }}
      ></ChangePasswordModal>
    </>
  );
};
export default Header;
