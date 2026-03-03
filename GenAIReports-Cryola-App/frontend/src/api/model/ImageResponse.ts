export type Category =
  | "footer"
  | "fsdu"
  | "header"
  | "product"
  | "shelf"
  | "sidepanel";

export interface ImageResponse {
  status: string;
  message: string;
  data: ImageData;
}

type pagination = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface ImageData {
  items: ImageInfo[] | null;
  pagination: pagination;
  total_count?: number;
}

export interface ImageInfo {
  category: Category;
  image_name?: string;
  url: string;
  thumbnail_url?: string;
}
