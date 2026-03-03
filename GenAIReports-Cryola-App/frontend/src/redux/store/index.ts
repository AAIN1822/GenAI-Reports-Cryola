import { configureStore } from "@reduxjs/toolkit";
import masterDataReducer from "../slices/masterDataSlice";
import projectDataReducer from "../slices/projectSlice";

export const store = configureStore({
  reducer: {
    masterData: masterDataReducer,
    projectData: projectDataReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ["uploads/updateField"],
        ignoredPaths: [
          "uploads.fsduImage",
          "uploads.brandCreatives.header",
          "uploads.brandCreatives.footer",
          "uploads.brandCreatives.sidePanel",
          "uploads.brandCreatives.shelfImage",
          "uploads.productImages",
          "uploads.productPlacement",
        ],
      },
    }),
});

// Infer types for TypeScript
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;