import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

// --------------------------------------------------
// TYPES
// --------------------------------------------------

interface Dimension {
  name: string;
  value: number | string;
}

interface ImageItem {
  image: string | undefined;   // URL or File URL
  name: string | undefined;   // when edited locally
}

interface ProductPlacementItem extends ImageItem {
  dimensions?: Dimension[];
}

export interface ProjectDetails {
  fsdu: {
    image: string | null;
    name: string | null;
    dimensions: Dimension[];
  };

  header: ImageItem;
  footer: ImageItem;
  sidepanel: ImageItem;
  shelf: ImageItem;

  color: string | null;

  products: {
    images: ImageItem[];
    placement: ProductPlacementItem[][];
  };
}

export interface ProjectModel {
  id: string;
  account: string;
  structure: string;
  sub_brand: string;
  season: string;
  region: string;
  project_description: string;
  user_id: string;
  created_at: number;

  details: ProjectDetails;
}

// --------------------------------------------------
// REDUX STATE
// --------------------------------------------------

interface ProjectState {
  currentProjectId: string;
  entities: Record<string, ProjectModel>;
  history: string[];
}

const initialState: ProjectState = {
  currentProjectId: "1",
  entities: {},
  history: [],
};

// --------------------------------------------------
// SLICE
// --------------------------------------------------

const projectSlice = createSlice({
  name: "projects",
  initialState,
  reducers: {
    // ---------------------------------------------
    // Create a new project (empty or loaded JSON)
    // ---------------------------------------------
    addProject: (state, action: PayloadAction<ProjectModel>) => {
      const project = action.payload;

      state.entities[project.id] = project;
      state.currentProjectId = project.id;

      // add to history (latest first)
      state.history = [project.id, ...state.history.filter(id => id !== project.id)];
    },

    // ---------------------------------------------
    // Switch active project
    // ---------------------------------------------
    setCurrentProject: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      state.currentProjectId = id;

      // update history
      state.history = [id, ...state.history.filter(p => p !== id)];

      if (!state.entities[id]) {
      state.entities[id] = {
        id: id,
        account: "",
        structure: "",
        sub_brand: "",
        season: "",
        region: "",
        project_description: "",
        user_id: "",
        created_at: Date.now(),
        details: {
          fsdu: { image: "", name: "", dimensions: [] },
          header: { image: "", name: "" },
          footer: { image: "", name: "" },
          sidepanel: { image: "", name: "" },
          shelf: { image: "", name: "" },
          color: "",
          products: { images: [], placement: [] },
        },
      };
    }
    },

    // ---------------------------------------------
    // Deep update any field with dot-path
    // Example path:
    //   "details.fsdu.image"
    //   "details.products.images.0.name"
    // ---------------------------------------------
   updateProjectField: (
    state,
    action: PayloadAction<{
      projectId: string;
      path: string;
      value: any;
      name: string | undefined;
    }>
  ) => {
    const { projectId, path, value, name } = action.payload;
    console.log("PP", action.payload)

    // If project doesn't exist, create a full empty one
    if (!state.entities[projectId]) {
      state.entities[projectId] = {
        id: projectId,
        account: "",
        structure: "",
        sub_brand: "",
        season: "",
        region: "",
        project_description: "",
        user_id: "",
        created_at: Date.now(),
        details: {
          fsdu: { image: "", name: "", dimensions: [] },
          header: { image: "", name: "" },
          footer: { image: "", name: "" },
          sidepanel: { image: "", name: "" },
          shelf: { image: "", name: "" },
          color: "",
          products: { images: [], placement: [] },
        },
      };
    }

    const project = state.entities[projectId];

    const keys = path.split(".");
    let temp: any = project;

    keys.forEach((key, index) => {
      if (index === keys.length - 1) {
        if(key == "fsdu") {
          temp[key] = {image: value, name: name, dimensions: temp[key].dimensions};
        } else {
          temp[key] = {image: value, name: name}; 
        }
        
      } else {
        if (temp[key] === undefined || temp[key] === null) {
          temp[key] = {};
        }
        temp = temp[key];
      }
    });
  },


    // ---------------------------------------------
    // Replace multiple product images
    // ---------------------------------------------
     setProductImages: (state, action: PayloadAction<{ projectId: string; images: ImageItem[] }>) => {
        const { projectId, images } = action.payload;
         if (!state.entities[projectId]) {
          state.entities[projectId] = {
            id: projectId,
            account: "",
            structure: "",
            sub_brand: "",
            season: "",
            region: "",
            project_description: "",
            user_id: "",
            created_at: Date.now(),
            details: {
              fsdu: { image: "", name: "", dimensions: [] },
              header: { image: "", name: "" },
              footer: { image: "", name: "" },
              sidepanel: { image: "", name: "" },
              shelf: { image: "", name: "" },
              color: "",
              products: { images: [], placement: [] },
            },
          };
        }

        const project = state.entities[projectId];
        if (project) {
          images.map((imageItem, _i) => {
            project.details.products.images.push(imageItem)
          })
        }

        // ---------------------------------------------
        // Add an empty project (if needed)
        // ---------------------------------------------
      },

    removeProductImage: (
        state,
        action: PayloadAction<{
          projectId: string;
          index?: number;
          imageUrl?: string;
        }>
      ) => {
        const { projectId, index, imageUrl } = action.payload;

        const project = state.entities[projectId];
        if (!project) return;

        const images = project.details.products.images;

        // Remove by index if provided
        if (typeof index === "number") {
          images.splice(index, 1);
          return;
        }

        // Remove by image URL
        if (imageUrl) {
          const position = images.findIndex(img => img.image === imageUrl);
          if (position !== -1) {
            images.splice(position, 1);
          }
        }
      },

      removeCategoryImage: (
        state,
        action: PayloadAction<{
          projectId: string;
          path: string; // example: "details.header"
        }>
      ) => {
        const { projectId, path } = action.payload;

        const project = state.entities[projectId];
        if (!project) return;

        const keys = path.split(".");
        let temp: any = project.details;

        keys.forEach((key, index) => {
          if (index === keys.length - 1) {
            // 👉 fsdu special case: keep dimensions
            if (key === "fsdu") {
              temp[key] = {
                image: "",
                name: "",
                dimensions: Array.isArray(temp[key]?.dimensions)
                  ? temp[key].dimensions
                  : [],
              };
            } else {
              // 👉 all other categories
              temp[key] = {
                image: "",
                name: "",
              };
            }
          } 
        });
      },


      updateFsduDimensions: (
        state,
        action: PayloadAction<{
          projectId: string;
          dimensions: Dimension[];
        }>
      ) => {
        const { projectId, dimensions } = action.payload;
        const project = state.entities[projectId];
        if (!project) return;

        project.details.fsdu.dimensions = dimensions;
      },

      setProductPlacement: (
        state,
        action: PayloadAction<{
          projectId: string;
          placement: ProductPlacementItem[][];
        }>
      ) => {
        const { projectId, placement } = action.payload;

        // Ensure project exists
        if (!state.entities[projectId]) {
          return;
        }

        // Full replacement (overwrite existing placement)
        if(state.entities[projectId]?.details?.products?.placement) {
        state.entities[projectId].details.products.placement = placement;
        }
      },

      updateProductColor: (
        state,
        action: PayloadAction<{
          projectId: string;
          color: string | null;
        }>
      ) => {
        const { projectId, color } = action.payload;

        const project = state.entities[projectId];
        if (!project) return;

        project.details.color = color;
      },

      updateProjectData: (
        state,
        action: PayloadAction<{
          projectId: string;
          project_data: ProjectModel
        }>
      ) => {
           const { projectId, project_data } = action.payload;

          if (!state.entities[projectId]) {
            state.entities[projectId] = {
              id: projectId,
              account: "",
              structure: "",
              sub_brand: "",
              season: "",
              region: "",
              project_description: "",
              user_id: "",
              created_at: Date.now(),
              details: {
                fsdu: { image: "", name: "", dimensions: [] },
                header: { image: "", name: "" },
                footer: { image: "", name: "" },
                sidepanel: { image: "", name: "" },
                shelf: { image: "", name: "" },
                color: "",
                products: { images: [], placement: [] },
              },
            };
          }

          const project = state.entities[projectId];
          project.account = project_data.account;
          project.structure = project_data.structure;
          project.sub_brand = project_data.sub_brand;
          project.season = project_data.season;
          project.region = project_data.region;
          project.project_description = project_data.project_description;
          project.user_id = project_data.user_id;
          project.created_at = project_data.created_at;
          if(project_data.details) {
          project.details = project_data.details;
          } else {
            project.details = {
                fsdu: { image: "", name: "", dimensions: [] },
                header: { image: "", name: "" },
                footer: { image: "", name: "" },
                sidepanel: { image: "", name: "" },
                shelf: { image: "", name: "" },
                color: "",
                products: { images: [], placement: [] },
              }
          }
        }


}});

// --------------------------------------------------
// EXPORTS
// --------------------------------------------------

export const {
  addProject,
  setCurrentProject,
  updateProjectField,
  setProductImages,
  removeProductImage,
  updateFsduDimensions,
  setProductPlacement,
  updateProductColor,
  updateProjectData,
  removeCategoryImage
} = projectSlice.actions;

export default projectSlice.reducer;
