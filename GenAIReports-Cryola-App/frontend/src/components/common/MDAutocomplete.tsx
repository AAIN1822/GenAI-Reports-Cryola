import React, { useEffect, useRef, useState } from "react";
import { Autocomplete, TextField, useTheme } from "@mui/material";
import MDErrorMessage from "./MDErrorMessage";
import MDConfirmationModel from "./MDConfirmationModel";
import type { MasterDataItem } from "../../api/model/MasterDataResponse";
import DeleteIcon from "@mui/icons-material/Delete";

interface MDAutocompleteProps {
  data: MasterDataItem[];
  placeholder?: string;
  label?: string;
  value?: string;
  onChange?: (value: string | null, isAddNew?: boolean) => void;
  onDeleteOption?: (id: string) => void;
  showAddOption?: boolean;
  showDeleteOption?: boolean;
  error?: string | null;
  background?: string;
}

const MDAutocomplete: React.FC<MDAutocompleteProps> = ({
  data,
  placeholder,
  label,
  value = "",
  onChange,
  onDeleteOption,
  showAddOption = false,
  showDeleteOption = false,
  error = null,
  background = "#ffffff",
}) => {
  const theme = useTheme();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [inputValue, setInputValue] = useState(value);
  const [open, setOpen] = useState(false);

  //const [confimationModel, setConfimationModel] = useState(false);
  const [confirm, setConfirm] = useState<{
    open: boolean;
    type: "add" | "delete" | null;
    payload?: string | null;
    id?:string |null
  }>({
    open: false,
    type: null,
    payload: null,
    id: null
  });

  const currentUserId = localStorage.getItem("id");

  const addNewText = "+ Add New";

  useEffect(() => {
    setInputValue(value || "");
  }, [value]);

  const removeErrorMessage = () => {
    // No manual DOM removal now; let MUI handle error
  };

  const itemMap = React.useMemo(() => {
    const map: Record<string, MasterDataItem> = {};
    data?.forEach((item) => {
      map[item.name] = item;
    });
    return map;
  }, [data]);

  const handleChange = (_: any, value: string | null) => {
    removeErrorMessage();
    if (value === null) {
      console.log("Cleared!");
      setInputValue("");
      onChange?.("", false);
      return;
    }

    if (value.startsWith(addNewText)) {
      const typedValue = inputRef.current?.value || "";
      setConfirm({
        open: true,
        type: "add",
        payload: inputRef.current?.value || "",
        id: null
      });
      setInputValue(typedValue); // keep what user typed
      setOpen(false);
      return;
    }

    if (onChange) onChange(value, false);
    setInputValue(value);
    setOpen(false);
  };

  const handleOnClose = () => {
    setConfirm({ open: false, type: null, payload: null, id: null });
  };
  const handleOnConfirm = () => {
    if (confirm.type === "add") {
      if (onChange) onChange(confirm.payload || "", true);
    }

    if (confirm.type === "delete" && confirm.id && onDeleteOption) {
      onDeleteOption(confirm.id);
    }

    setConfirm({ open: false, type: null, payload: null, id: null });
  };

  const handleInputChange = (_: any, newInputValue: string, _reason: string) => {
    removeErrorMessage();

    // Prevent "+ Add New ..." from being set in the input
    if (newInputValue.startsWith(addNewText)) return;

    setInputValue(newInputValue);
    if (onChange) {
      onChange(newInputValue, false);
    }
  };

  const filterOptions = (options: string[], params: { inputValue: string }) => {
    const filtered = options.filter((option) =>
      option.toLowerCase().includes(params.inputValue.toLowerCase())
    );

    if (showAddOption && params.inputValue.trim() !== "") {
      const addNewOption = `${addNewText} ${label || ""}`;
      return [addNewOption, ...filtered.filter((opt) => opt !== addNewOption)];
    }

    return filtered;
  };

  return (
    <div>
      <Autocomplete
        freeSolo
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => setOpen(false)}
        options={(data ?? []).map((item) => item.name)}
        onChange={handleChange}
        inputValue={inputValue}
        onInputChange={handleInputChange}
        filterOptions={filterOptions}
        popupIcon={inputValue ? null : undefined}
        clearIcon={inputValue ? undefined : null}
        forcePopupIcon={!inputValue}
        disableClearable={!inputValue}
        renderOption={(props, option) => {
          const isAdd = option.startsWith(addNewText);
          const item = itemMap[option];
          const canDelete =
            showDeleteOption &&
            !isAdd &&
            item &&
            currentUserId &&
            item.created_by === currentUserId;

          return (
            <li
              {...props}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                fontWeight: isAdd ? 700 : 400,
              }}
            >
              <span>{option}</span>
              {canDelete && (
                <DeleteIcon
                  className="delete-btn"
                  style={{
                    cursor: "pointer",
                    marginLeft: "10px",
                    color: "#c2bfbf",
                  }}
                  onClick={(e) => {
                    e.stopPropagation(); // prevent selection
                    setConfirm({
                      open: true,
                      type: "delete",
                      payload: option,
                      id: item.id
                    });
                  }}
                />
              )}
            </li>
          );
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            fullWidth
            size="small"
            placeholder={placeholder}
            inputRef={inputRef}
            InputProps={{
              ...params.InputProps,
              sx: {
                backgroundColor: `${background} !important`,
                borderRadius: "10px",
                minWidth: "150px",
                color: theme.palette.custom.labelGrayText,
                "&.MuiOutlinedInput-root, & .MuiOutlinedInput-root, & .MuiInputBase-root, & .MuiAutocomplete-inputRoot":
                  {
                    backgroundColor: `${background} !important`,
                    borderRadius: "10px",
                  },

                "& input": {
                  backgroundColor: "transparent !important",
                  color: theme.palette.custom.labelGrayText,
                },

                "& fieldset": {
                  borderColor: "#D9D9D9",
                  backgroundColor: "transparent !important",
                },
                "&:hover fieldset": {
                  borderColor: "#D9D9D9",
                  backgroundColor: "transparent !important",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#D9D9D9",
                  backgroundColor: "transparent !important",
                },
              },
            }}
            onInput={removeErrorMessage}
          />
        )}
      />
      {error && <MDErrorMessage message={error} />}
      <MDConfirmationModel
        open={confirm.open}
        title={confirm.type === "delete" ? "Delete Item" : "Add Item"}
        description={
          confirm.type === "delete"
            ? `Are you sure you want to delete "${confirm.payload}"?`
            : `Are you sure you want to add this "${confirm.payload}"?`
        }
        onClose={handleOnClose}
        onConfirm={handleOnConfirm}
      />
    </div>
  );
};

export default MDAutocomplete;
