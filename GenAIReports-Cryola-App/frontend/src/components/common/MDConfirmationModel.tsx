import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import MDLabel from "./MDLabel";
import MDButton from "./MDButton";

export type MDConfirmationModelProps = {
  open: boolean;
  onClose?: () => void;
  onConfirm?: () => void;
  title?: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  id?: string;
  loading?: boolean;
};

export default function MDConfirmationModel({
  open,
  onClose,
  onConfirm,
  title,
  description,
  loading = false,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
}: MDConfirmationModelProps) {
  return (
    <Dialog open={open} onClose={onClose}>
      {title && (
        <DialogTitle sx={{ textAlign: "center" }}>
          <MDLabel text={title} sx={{ fontSize: 20, fontWeight: 500 }}/>
        </DialogTitle>
      )}
      {description && (
        <DialogContent>
          <DialogContentText sx={{ textAlign: "center" }}>
            <MDLabel text={description} sx={{ fontSize: 15, fontWeight: 400 }}/>
          </DialogContentText>
        </DialogContent>
      )}

      <DialogActions sx={{ width: "auto", display: "flex", justifyContent: "center", gap: 2, mx: "auto", pb: 2, }}>
        <MDButton
          loading={loading}
          variant="green"
          text={confirmLabel}
          onClick={onConfirm}
          width="fit-content"
        ></MDButton>
        <MDButton
          variant="outline"
          text={cancelLabel}
          onClick={onClose}
          width="fit-content"
        ></MDButton>
      </DialogActions>
    </Dialog>
  );
}
