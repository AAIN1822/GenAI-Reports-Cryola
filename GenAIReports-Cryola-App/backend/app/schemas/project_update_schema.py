from pydantic import BaseModel
from typing import List, Optional

class Dimension(BaseModel):
    name: str
    value: float

class ImageItem(BaseModel):
    image: str
    name: str
    dimensions: Optional[List[Dimension]] = None

class Fsdu(BaseModel):
    image: str
    name: str
    dimensions: List[Dimension]

class ProductPlacementItem(BaseModel):
    image: str
    name: str
    dimensions: List[Dimension]

class Products(BaseModel):
    images: List[ImageItem]
    placement: List[List[ProductPlacementItem]]

class ProjectUpdate(BaseModel):
    fsdu: Fsdu
    header: Optional[ImageItem] = None
    footer: Optional[ImageItem] = None
    sidepanel: Optional[ImageItem] = None
    shelf: Optional[ImageItem] = None
    color: str
    products: Optional[Products] = None