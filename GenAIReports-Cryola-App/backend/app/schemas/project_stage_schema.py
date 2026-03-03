from enum import Enum

class ProjectStage(str, Enum):
    STAGE_1 = "Project_Created"
    STAGE_2 = "Inputs"
    STAGE_3 = "Colour_Theme"
    STAGE_4 = "Colour_Theme_Refinement"
    STAGE_5 = "Graphics"
    STAGE_6 = "Graphics_Refinement"
    STAGE_7 = "Product_Placement"
    STAGE_8 = "Product_Placement_Refinement"
    STAGE_9 = "Multi_Angle_View"


class StageForJobStatus(str, Enum):
    Theme = "Colour_Theme"
    Graphics = "Graphics"
    Product = "Product_Placement"
    Theme_Refinement = "Colour_Theme_Refinement"
    Graphics_Refinement = "Graphics_Refinement"
    Product_Refinement = "Product_Placement_Refinement"
    Multi_Angle_View = "Multi_Angle_View"
    