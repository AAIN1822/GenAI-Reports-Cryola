import {
  Box,
  Dialog,
  DialogActions,
  Tooltip,
  Typography,
  useTheme,
} from "@mui/material";
import MDPasswordInput from "../../components/common/MDPasswordInput";
import MDErrorMessage from "../../components/common/MDErrorMessage";
import MDLabel from "../../components/common/MDLabel";
import MDButton from "../../components/common/MDButton";
import { useEffect, useState, type ChangeEvent } from "react";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { validatePassword } from "../../utils/helpers";
import { changePassword } from "../../api/User";

interface ChangePasswordModalProps {
  open: boolean;
  onClose: () => void;
}

const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
  open,
  onClose,
}) => {
  const theme = useTheme();
  const [oldPass, setOldPass] = useState("");
  const [newPass, setNewPass] = useState("");
  const [confirmPass, setConfirmPass] = useState("");

  const [oldError, setOldError] = useState("");
  const [newError, setNewError] = useState("");
  const [confirmError, setConfirmError] = useState("");

  const [apiErrorMsg, setApiErrorMsg] = useState("");

  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (open) {
      setOldPass("");
      setNewPass("");
      setConfirmPass("");
      setOldError("");
      setNewError("");
      setConfirmError("");
      setApiErrorMsg("");
    }
  }, [open]);

  const handleOldChange = (e: ChangeEvent<HTMLInputElement>) => {
    setOldPass(e.target.value);
    setOldError(e.target.value ? "" : "Old password is required");
  };
  const handleNewChange = (e: ChangeEvent<HTMLInputElement>) => {
    setNewPass(e.target.value);
    setNewError(e.target.value ? "" : "New password is required");
  };
  const handleConfirmChange = (e: ChangeEvent<HTMLInputElement>) => {
    setConfirmPass(e.target.value);
    setConfirmError(e.target.value ? "" : "Please confirm your password");
  };

  // SUBMIT
  const handleSubmitChangePassword = async () => {
    setOldError("");
    setNewError("");
    setConfirmError("");
    setApiErrorMsg("");
    let hasError = false;

    if (!oldPass) {
      setOldError("Old password is required");
      hasError = true;
    }
    if (!newPass) {
      setNewError("New password is required");
      hasError = true;
    } else if (!validatePassword(newPass)) {
      setNewError(
        "Password must be at least 8 characters and include a number, a letter, and a special character."
      );
      hasError = true;
    }
    if (!confirmPass) {
      setConfirmError("Please confirm your password");
      hasError = true;
    } else if (confirmPass !== newPass) {
      setConfirmError("Passwords do not match");
      hasError = true;
    }

    if (hasError) return;

    try {
      setLoading(true);
      const response = await changePassword(oldPass, newPass);
      console.log("Change Password Response:", response.data);
      onClose()
      alert(response.data.message);

    } catch (error: any) {
      console.error("Change Password error:", error.response?.data || error);
      if (error.response?.data?.message) {
        setApiErrorMsg(error.response.data.message);
      } else {
        setApiErrorMsg("Something went wrong, please try again");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Box sx={{ p: 3, width: 400 }}>
        <Typography variant="h6" sx={{ textAlign: "center", mb: 2 }}>
          Change Password
        </Typography>
        {/* OLD PASSWORD */}
        <MDLabel text="Old Password" sx={{ pb: 0.5 }} />
        <MDPasswordInput
          password={oldPass}
          handlePasswordChange={handleOldChange}
        />
        {oldError && <MDErrorMessage message={oldError} />}
        {/* NEW PASSWORD */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 1 }}>
          <MDLabel text="New Password" sx={{ pb: 0.5 }} />
          <Tooltip
            title="Password should be at least 8 characters including one special character, one number, one alphabet."
            placement="right"
          >
            <InfoOutlinedIcon
              sx={{
                fontSize: 18,
                color: theme.palette.custom.emeraldGreen,
                cursor: "pointer",
              }}
            />
          </Tooltip>
        </Box>

        <MDPasswordInput
          password={newPass}
          handlePasswordChange={handleNewChange}
        />
        {newError && <MDErrorMessage message={newError} />}
        {/* CONFIRM PASSWORD */}
        <MDLabel text="Confirm Password" sx={{ pb: 0.5, pt: 1 }} />
        <MDPasswordInput
          password={confirmPass}
          handlePasswordChange={handleConfirmChange}
        />
        {confirmError && <MDErrorMessage message={confirmError} />}

        {apiErrorMsg && <MDErrorMessage message={apiErrorMsg} />}

        <DialogActions sx={{ justifyContent: "center", gap: 2, mt: 1 }}>
          <MDButton
            loading={loading}
            text="Submit"
            variant="green"
            onClick={handleSubmitChangePassword}
          />

          <MDButton text="Cancel" variant="outline" onClick={onClose} />
        </DialogActions>
      </Box>
    </Dialog>
  );
};

export default ChangePasswordModal;
