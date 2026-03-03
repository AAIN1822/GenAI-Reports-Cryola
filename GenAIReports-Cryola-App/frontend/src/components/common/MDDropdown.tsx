import FormControl from "@mui/material/FormControl";
import Select, { type SelectChangeEvent } from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import type { SxProps, Theme } from "@mui/material/styles";

/**
 * Props for the Dropdown component.
 */
interface MDDropdownProps<T extends string | number> {
  /** Label displayed above the dropdown */
  label?: string;
  /** Current selected value */
  value: T;
  /** Callback when value changes */
  onChange: (event: SelectChangeEvent<T>, child?: React.ReactNode) => void;
  /** List of selectable options */
  options: T[];
  /** Whether the dropdown should take full width */
  fullWidth?: boolean;
  /** Custom MUI sx styling */
  sx?: SxProps<Theme>;
}

/**
 * Reusable Dropdown component using MUI.
 * Displays a label, select box, and gracefully handles empty options.
 */
const MDDropdown = <T extends string | number>({
  label,
  value,
  onChange,
  options = [],
  fullWidth = true,
  sx = {},
}: MDDropdownProps<T>) => {
  return (
    <FormControl fullWidth={fullWidth} sx={sx}>
      {/* ✅ Label (outside select) */}
      {label && (
        <Typography
          sx={{
            fontSize: "14px",
            fontWeight: 600,
            color: "black",
            mb: "6px",
          }}
        >
          {label}
        </Typography>
      )}

      {/* ✅ Select dropdown */}
      <Select<T>
        value={value}
        onChange={onChange}
        size="small"
        displayEmpty
        sx={{
          backgroundColor: "white",
          borderRadius: "8px",
          fontSize: "14px",
          height: "40px",
          "& .MuiSelect-select": {
            display: "flex",
            alignItems: "center",
          },
        }}
      >
        {options.length > 0 ? (
          options.map((item, index) => (
            <MenuItem key={index} value={item}>
              {item}
            </MenuItem>
          ))
        ) : (
          <MenuItem disabled>No Options Available</MenuItem>
        )}
      </Select>
    </FormControl>
  );
};

export default MDDropdown;
