export const TemplateGalleryCategoryEnum = {
  FSDU: "fsdu",
  HEADER: "header",
  FOOTER: "footer",
  SIDEPANEL: "sidepanel",
  SHELF: "shelf",
  PRODUCT: "product",
} as const;

export type TemplateGalleryCategoryEnum =
  (typeof TemplateGalleryCategoryEnum)[keyof typeof TemplateGalleryCategoryEnum];