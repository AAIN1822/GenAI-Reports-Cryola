import * as React from 'react';
import { styled } from '@mui/material/styles';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';
import { Box} from '@mui/material';
import MDLabel from '../../../components/common/MDLabel';
import MDButton from '../../../components/common/MDButton';
import NumberInput from '../../../components/common/MDNumberInput';
import MDAutocomplete from '../../../components/common/MDAutocomplete';
import type { AppDispatch, RootState } from "../../../redux/store/index";
import { useDispatch, useSelector } from "react-redux";
import {
  addMasterItem,
  deleteMasterItem,
  type MasterField,
} from "../../../redux/slices/masterDataSlice";
import { useEffect } from 'react';

const BootstrapDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-root': {
    borderRadius: 8,
  },
  '& .MuiDialogContent-root': {
    padding: theme.spacing(3),
  },
  '& .MuiDialogActions-root': {
    padding: theme.spacing(1),
  },
}));

interface AddDimensionProps {
  open: boolean;
  isProductDimension:boolean;
  handleClose: () => void;
  addDimension: (name: string, value: number | string) => void;
}

const AddDimension: React.FC<AddDimensionProps> = ({open, isProductDimension, handleClose, addDimension}) => {
  const dispatch = useDispatch<AppDispatch>();
  
  const { displayDimensions, productDimensions } = useSelector((state: RootState) => state.masterData);
  const [newDimensionLabel, setNewDimensionLabel] = React.useState("");
  const [value, setValue] = React.useState<number | string>(0);
  const [error, setError] = React.useState(false);

   useEffect(() => {
      if (open) {
        setNewDimensionLabel("")
        setValue(0)
        setError(false)
      }
    }, [open]);

  const handleAutocompleteChange = async (
      field: MasterField,
      value: string | null,
      isAddNew?: boolean
    ) => {
      if (!value) {
        setNewDimensionLabel("");
        return;
      }
      if (value && isAddNew) {
        await dispatch(addMasterItem({ field, value }));
      }
      setNewDimensionLabel(value);
      
      setError(false);
    };
  
    const handleDelete = async (field: MasterField, id: string | null) => {
      if (!id) return;
      await dispatch(deleteMasterItem({ field, id }));
    };

    const handleSave = async() => {
      addDimension(newDimensionLabel, value)
       handleClose();
    }
  
  return (
    <React.Fragment>
      <BootstrapDialog
        onClose={handleClose}
        aria-labelledby="customized-dialog-title"
        open={open}
        BackdropProps={{
          style: { backgroundColor: "rgba(0,0,0,0.2)" } // ← transparency here
        }}
        PaperProps={{
        sx: {
          boxShadow: "0px 4px 20px rgba(0,0,0,0.1)", // lighter shadow
          
        }
      }}
      >
        <DialogTitle sx={{ m: 0, p: 2 }} id="customized-dialog-title">
          Add Dimension(in)
        </DialogTitle>
        <IconButton
          aria-label="close"
          onClick={handleClose}
          sx={(theme) => ({
            position: 'absolute',
            right: 8,
            top: 8,
            color: theme.palette.grey[500],
          })}
        >
          <CloseIcon />
        </IconButton>
        <DialogContent dividers>
          <Box style={{display: "flex", gap: 32, alignItems: "center"}}>
            <Box style={{display: "flex", gap: 8, alignItems: "center"}}>
            <MDLabel text="Dimension Type" />
            <MDAutocomplete
              placeholder="Select"
              data={isProductDimension ? productDimensions : displayDimensions}
              label="Dimension"
              value={newDimensionLabel}
              showAddOption={true}
              error={error ? "Dimension is required" : null}
              onChange={(value, isAddNew) =>
                handleAutocompleteChange(isProductDimension ? "productDimension" : "displayDimension", value, isAddNew)
              }
              showDeleteOption={true}
              onDeleteOption={(id) => handleDelete(isProductDimension ? "productDimension" : "displayDimension", id)}
            />
            </Box>
            <NumberInput value={value}  onChange={(val) => setValue(val)}/>
          </Box>
        </DialogContent>
        <DialogActions>
          <Box
            sx={{
              display: "flex",
              justifyContent: "flex-end",
              marginRight: "10px"
            }}
          >
          <MDButton 
            variant="green" 
            text="Save" 
            onClick={handleSave} 
            disabled={!newDimensionLabel || !value} 
            style={{ height: "35px", width: "70px" }}
            />
            </Box>
        </DialogActions>
      </BootstrapDialog>
    </React.Fragment>
  );
}

export default AddDimension;