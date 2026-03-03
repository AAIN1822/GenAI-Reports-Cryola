import React, { useState } from "react";
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import ExpandCircleDownIcon from '@mui/icons-material/ExpandCircleDown';
import MDLabel from "./MDLabel";

interface MDSectionAccordionProps {
  title: string;
  children: React.ReactNode;
  detailsSx?: object;   // allow style override
  summarySx?: object;   // allow summary override
  defaultExpanded?: boolean;
  headerIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onToggle?: (expanded: boolean) => void;
}

const MDSectionAccordion: React.FC<MDSectionAccordionProps> = ({
  title,
  children,
  detailsSx = {},
  summarySx = {},
  defaultExpanded = true,
  headerIcon,
  rightIcon,
  onToggle,
}) => {
  const [expanded, setExpanded] = useState<boolean>(defaultExpanded);
  return (
    <Accordion
      expanded={expanded}
      defaultExpanded={defaultExpanded}
      disableGutters
      sx={{
        width: "100%",
        backgroundColor: "transparent",
        boxShadow: "none",
        "&:before": { display: "none" },
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandCircleDownIcon sx={{ color: "black", cursor: "pointer" }}
         onClick={(e) => {
          e.stopPropagation();        // 👈 prevent summary click
          setExpanded((prev: boolean) => !prev);
          onToggle && onToggle(!expanded);
        }}
         />}
        sx={{
          backgroundColor: "#E1F1E5",
          minHeight: 20,
          padding: 0.5,
          alignItems: "center",
          position: "relative",
          cursor: "default",
          "&.Mui-expanded": { minHeight: 40 },
          "& .MuiAccordionSummary-content": {
            margin: 0,
            alignItems: "center",
          },
          ":focus": { outline: "none" },
          ...summarySx,
        }}
        onClick={(e) => e.stopPropagation()} 
      >
        {headerIcon && <span style={{marginRight: "8px"}}>{headerIcon}</span>}
        <MDLabel text={title} />
        <div style={{position: "absolute", top: "8px", right: "40px"}}>{rightIcon}</div>
      </AccordionSummary>

      <AccordionDetails
        sx={{
          borderRadius: 2,
          p: "0.5px 0.5px",
          overflowY: "auto",
          ...detailsSx,
        }}
      >
        {children}
      </AccordionDetails>
    </Accordion>
  );
};

export default MDSectionAccordion;
