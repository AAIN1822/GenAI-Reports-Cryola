import { type FC, type CSSProperties, useMemo } from "react";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import SaveOutlinedIcon from "@mui/icons-material/SaveOutlined";
import ArrowCircleDownIcon from "@mui/icons-material/ArrowCircleDown";
import CloseIcon from "@mui/icons-material/Close";
import { useTheme } from "@mui/material";
import MDButton from "./MDButton";

interface MDActionHeaderProps {
  title: string;
  isModifyMode?: boolean;
  onModify?: () => void;
  onSaveAs?: () => void;
  onDownload?: () => void;
  onClose?: () => void;
  style?: CSSProperties;
}

const MDActionHeader: FC<MDActionHeaderProps> = ({
  title,
  isModifyMode = false,
  onModify,
  onSaveAs,
  onDownload,
  onClose,
  style = {},
}) => {
  const theme = useTheme();
  const wrapperStyle = useMemo(() => ({
    width: "100%",
    background: theme.palette.custom.inputScreenBackground,
    padding: "6px 16px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    ...style,
  }), [style]);

  return (
    <div style={wrapperStyle}>
      <div style={{ fontSize: "16px", fontWeight: 600 }}>{title}</div>

      <div style={{ display: "flex", gap: "10px" }}>

        {/* Modify → Update */}
        {isModifyMode && <MDButton 
          text={"Modify"} 
          width="100px"
          onClick={onModify}
          leftIcon={
              <EditOutlinedIcon style={{ fontSize: 20 }} />
          }
          />}
          <MDButton 
          text="Save as"
          width="110px"
          variant="white"
          onClick={onSaveAs}
          leftIcon={<SaveOutlinedIcon style={{ fontSize: 20 }} />}
          />

        <div onClick={onDownload} style={{marginTop: "3px"}}>
          <ArrowCircleDownIcon style={{ fontSize: 26 }} />
        </div>
        <MDButton 
          text="Close"
          width="100px"
          variant="red"
          onClick={onClose}
          leftIcon={<CloseIcon style={{ fontSize: 20 }} />}
          />
      </div>
    </div>
  );
};

export default MDActionHeader;
