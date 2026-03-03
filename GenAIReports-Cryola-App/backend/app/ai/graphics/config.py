import os
from pathlib import Path
from pydantic_settings import BaseSettings

class GraphicsConfig(BaseSettings):

    # Azure Configuration
    AZURE_API_VERSION: str = "2025-04-01-preview"
    
    # Models
    IMAGE_MODEL: str = "gpt-image-1.5"
    REASONING_MODEL: str = "o3"

    # Local Output (Fallback)
    OUTPUT_DIR: Path = Path(__file__).parent / "output_graphics"

    class Config:
        env_file = ".env"
        extra = "ignore"

config = GraphicsConfig()

# Region Specs
REGION_SPECS = {
    "Header_Graphic": {
        "id": "Top_Header_Panel",
        "desc": "The top fascia/header panel.",
        "rule": "Center aligned. Do not crop. Maintain header structure."
    },
    "Front_Lip_Graphic": {
        "id": "Front_Lip_Rails",
        "desc": "The thin front facing strips/retainers on every shelf level.",
        "rule": "Repeat logic: Apply to ALL shelf lips. No cropping. Fit to height."
    },
    "Left_Side_Panel_Graphic": {
        "id": "Left_Side_Panel",
        "desc": "The vertical side panels/wings of the display.",
        "rule": "Full height placement. Watch for perspective skew."
    },
    "Right_Side_Panel_Graphic": {
        "id": "Right_Side_Panel",
        "desc": "The vertical side panels/wings of the display.",
        "rule": "Full height placement. Watch for perspective skew."
    },
    "Base_Plinth_Graphic": {
        "id": "Base_Plinth_Panel",
        "desc": "A flat quadrilateral base panel with straight perimeter edges and a slightly angled top surface, forming a shallow wedge-like rectangle..",
        "rule": "Locate absolute quadrilateral base panel with straight perimeter edges and a slightly angled top surface"
    }
}
