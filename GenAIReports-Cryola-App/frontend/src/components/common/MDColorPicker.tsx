import React, { useState, useEffect } from "react";
import { HexColorPicker } from "react-colorful";
import MDLabel from "./MDLabel";
import { useTheme } from "@mui/material";
import { useSelector, useDispatch } from "react-redux";
import type { RootState } from "../../redux/store"; // make sure this points to your root reducer
import { updateProductColor } from "../../redux/slices/projectSlice";
import MDNumberInput from "./MDNumberInput";

// HEX to CMYK
const hexToCMYK = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const k = 1 - Math.max(r, g, b);
  const c = (1 - r - k) / (1 - k) || 0;
  const m = (1 - g - k) / (1 - k) || 0;
  const y = (1 - b - k) / (1 - k) || 0;

  return {
    c: Math.round(c * 100),
    m: Math.round(m * 100),
    y: Math.round(y * 100),
    k: Math.round(k * 100),
  };
};

// CMYK to HEX
const cmykToHex = (c: number, m: number, y: number, k: number) => {
  const r = Math.min(255, Math.max(0, 255 * (1 - c / 100) * (1 - k / 100)));
  const g = Math.min(255, Math.max(0, 255 * (1 - m / 100) * (1 - k / 100)));
  const b = Math.min(255, Math.max(0, 255 * (1 - y / 100) * (1 - k / 100)));

  return `#${Math.round(r)
    .toString(16)
    .padStart(2, "0")}${Math.round(g)
    .toString(16)
    .padStart(2, "0")}${Math.round(b).toString(16).padStart(2, "0")}`;
};

const channelNames: Record<"c" | "m" | "y" | "k", string> = {
  c: "Cyan",
  m: "Magenta",
  y: "Yellow",
  k: "Black",
};

const debounce = (func: Function, delay: number) => {
  let timer: any;
  return (...args: any[]) => {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};

interface MDColorPickerProps {
  defaultColor?: string;
  onColorChange?: (hex: string) => void;
}

const MDColorPicker: React.FC<MDColorPickerProps> = ({
  defaultColor = "#ffffff",
  onColorChange,
}) => {
    const theme = useTheme();
    const dispatch = useDispatch();
  const [color, setColor] = useState<string>(defaultColor);
  const [cmyk, setCMYK] = useState<{
    c: number;
    m: number;
    y: number;
    k: number;
  }>(hexToCMYK(defaultColor));

  const { currentProjectId } = useSelector(
    (state: RootState) => state.projectData
  );

  const debouncedUpdateColor = React.useMemo(
  () =>
    debounce((hex: string) => {
      if (currentProjectId) {
        dispatch(
          updateProductColor({
            projectId: currentProjectId,
            color: hex,
          })
        );
      }
    }, 300), // 300ms debounce
  [currentProjectId, dispatch]
);

  useEffect(() => {
  if (defaultColor !== color) {
    setColor(defaultColor);
  }
}, [defaultColor]);



  useEffect(() => {
    if (defaultColor !== color) {
      debouncedUpdateColor(color);
      onColorChange?.(color);
    }
  }, [color]);

  useEffect(() => {
    if (isInternalCMYKUpdate.current) {
      isInternalCMYKUpdate.current = false;
      return;
    }

    if (/^#[0-9A-Fa-f]{6}$/.test(color)) {
      setCMYK(hexToCMYK(color));
    }
  }, [color]);

  const isInternalCMYKUpdate = React.useRef(false);

  const handleCMYKChange = (channel: "c" | "m" | "y" | "k", value: number) => {
    const clamped = Math.max(0, Math.min(100, value));
    const newCMYK = { ...cmyk, [channel]: clamped };
    isInternalCMYKUpdate.current = true;

    setCMYK(newCMYK);
    setColor(cmykToHex(newCMYK.c, newCMYK.m, newCMYK.y, newCMYK.k));
  };

  const getSliderBackground = (channel: "c" | "m" | "y" | "k") => {
    const base = { ...cmyk };
    const startCMYK = { ...base, [channel]: 0 };
    const endCMYK = { ...base, [channel]: 100 };
    return `linear-gradient(to right, ${cmykToHex(
      startCMYK.c,
      startCMYK.m,
      startCMYK.y,
      startCMYK.k
    )} 0%, ${cmykToHex(endCMYK.c, endCMYK.m, endCMYK.y, endCMYK.k)} 100%)`;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2px", width: "100%"}}>
      {/* Inject slider styles */}
      <style>{`
        .cmyk-slider {
          -webkit-appearance: none;
          appearance: none;
          width: 60%;
          height: 20px; /* Track height */
          border-radius: 12px;
          background: transparent;
          position: relative;
        }

        /* WebKit browsers: Chrome, Edge, Safari */
        .cmyk-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid #ffffffff;
          background: #3A87FD;
          cursor: pointer;
          position: relative;
          top: 50%;
          transform: translateY(0%); /* Perfect vertical centering */
        }

        /* Firefox */
        .cmyk-slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid #ffffffff;
          background: #3A87FD;
          cursor: pointer;
          transform: translateY(-0%);
        }
      `}</style>

      {/* HEX Color Picker */}
      <div style={{ width: "100%" }}>
        <HexColorPicker color={color} onChange={setColor} style={{ width: "100%", height: "120px" }} />
      </div>

      {/* CMYK Sliders */}
      {(["c", "m", "y", "k"] as const).map((channel) => (
        <div key={channel} style={{ display: "flex", flexDirection: "column", gap: "0.15rem" }}>
          <MDLabel text={channelNames[channel]} sx={{ fontWeight: 400, textAlign: "left" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="range"
              min={0}
              max={100}
              width={50}
              value={cmyk[channel]}
              onChange={(e) => handleCMYKChange(channel, Number(e.target.value))}
              style={{ flex: 1, background: getSliderBackground(channel) }}
              className="cmyk-slider"
            />
            <MDNumberInput
              value={`${cmyk[channel]}`}
              onChange={(val) => handleCMYKChange(channel, Number(val))}
              size="small"
              max = {100}
            />
          </div>
        </div>
      ))}

      {/* HEX Display */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          width: "100%",
        }}
      >
        <MDLabel text="Hex Code:" sx={{ fontWeight: 600 }} />
        <input
          type="text"
          value={color}
          onChange={(e) => {
            const val = e.target.value;
            if (/^#([0-9A-Fa-f]{0,6})$/.test(val)) setColor(val);
          }}
          style={{
            fontWeight: 500,
            backgroundColor: theme.palette.custom.labelBoxColor,
            borderRadius: "0.4rem",
            padding: "0.4rem 0.5rem",
            border: `1px solid ${theme.palette.custom.labelBoxColor}`,
            width: "80px",
          }}
        />
      </div>
    </div>
  );
};

export default MDColorPicker;
