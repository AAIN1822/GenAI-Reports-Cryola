import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
  getAccounts,
  getSeasons,
  getSubBrands,
  getStructures,
  getRegions,
  addAccounts,
  addSeasons,
  addSubBrands,
  addStructures,
  addRegions,
  deleteAccounts,
  deleteSeasons,
  deleteSubBrands,
  deleteStructures,
  deleteRegions,
  getDisplayDimension,
  addDisplayDimension,
  deleteDisplayDimension,
  getProductDimension,
  addProductDimension,
  deleteProductDimension
} from "../../api/masterData";
import type { MasterDataItem } from "../../api/model/MasterDataResponse";

export type MasterField =
  | "account"
  | "season"
  | "subBrand"
  | "structure"
  | "region"
  | "displayDimension"
  | "productDimension";

export interface MasterDataState {
  accounts: MasterDataItem[];
  seasons: MasterDataItem[];
  subBrands: MasterDataItem[];
  structures: MasterDataItem[];
  regions: MasterDataItem[];
  displayDimensions: MasterDataItem[];
  productDimensions: MasterDataItem[];
  loading: boolean;
}

const initialState: MasterDataState = {
  accounts: [],
  seasons: [],
  subBrands: [],
  structures: [],
  regions: [],
  displayDimensions: [],
  productDimensions: [],
  loading: false,
};

export const fetchMasterData = createAsyncThunk(
  "masterData/fetch",
  async () => {
    const [
      accountsRes,
      seasonsRes,
      subBrandsRes,
      structuresRes,
      regionsRes,
      displayDimensionsRes,
      productDimensionsRes,
    ] = await Promise.all([
      getAccounts(),
      getSeasons(),
      getSubBrands(),
      getStructures(),
      getRegions(),
      getDisplayDimension(),
      getProductDimension()
    ]);

    return {
      accounts: accountsRes.data.data.items || [],
      seasons: seasonsRes.data.data.items || [],
      subBrands: subBrandsRes.data.data.items || [],
      structures: structuresRes.data.data.items || [],
      regions: regionsRes.data.data.items || [],
      displayDimensions: displayDimensionsRes.data.data.items || [],
      productDimensions: productDimensionsRes.data.data.items || []
    };
  }
);

export const fetchDimensionsMasterData = createAsyncThunk(
  "masterData/fetchDimensions",
  async () => {
    const [
      displayDimensionsRes,
      productDimensionsRes,
    ] = await Promise.all([
      getDisplayDimension(),
      getProductDimension()
    ]);

    return {
      displayDimensions: displayDimensionsRes.data.data.items || [],
      productDimensions: productDimensionsRes.data.data.items || []
    };
  }
);

const apiMap: Record<MasterField, (value: string) => Promise<any>> = {
  account: addAccounts,
  season: addSeasons,
  subBrand: addSubBrands,
  structure: addStructures,
  region: addRegions,
  displayDimension: addDisplayDimension,
  productDimension: addProductDimension
};

export const addMasterItem = createAsyncThunk(
  "masterData/addItem",
  async ({ field, value }: { field: MasterField; value: string }) => {
    const apiFn = apiMap[field];
    const res = await apiFn(value);

    const item: MasterDataItem = {
      id: res.data?.data?.id ?? "",
      name: res.data?.data?.name ?? value,
      created_by: res.data?.data?.created_by ?? "",
    };

    return {
      field,
      item: item,
    };
  }
);

const deleteApiMap: Record<MasterField, (id: string) => Promise<any>> = {
  account: deleteAccounts,
  season: deleteSeasons,
  subBrand: deleteSubBrands,
  structure: deleteStructures,
  region: deleteRegions,
  displayDimension: deleteDisplayDimension,
  productDimension: deleteProductDimension
};

export const deleteMasterItem = createAsyncThunk(
  "masterData/deleteItem",
  async ({ field, id }: { field: MasterField; id: string }) => {
    const apiFn = deleteApiMap[field];
    await apiFn(id);

    return { field, id };
  }
);

const masterDataSlice = createSlice({
  name: "masterData",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMasterData.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMasterData.fulfilled, (state, { payload }) => {
        state.accounts = payload.accounts;
        state.seasons = payload.seasons;
        state.subBrands = payload.subBrands;
        state.structures = payload.structures;
        state.regions = payload.regions;
        state.displayDimensions = payload.displayDimensions;
        state.productDimensions = payload.productDimensions;
        state.loading = false;
      })
      .addCase(fetchMasterData.rejected, (state) => {
        state.loading = false;
      })
      .addCase(fetchDimensionsMasterData.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDimensionsMasterData.fulfilled, (state, { payload }) => {
        state.displayDimensions = payload.displayDimensions;
        state.productDimensions = payload.productDimensions;
        state.loading = false;
      })
      .addCase(fetchDimensionsMasterData.rejected, (state) => {
        state.loading = false;
      })
      .addCase(addMasterItem.fulfilled, (state, { payload }) => {
        const { field, item } = payload;
        type MasterArrayKeys =
          | "accounts"
          | "seasons"
          | "subBrands"
          | "structures"
          | "regions"
          | "displayDimensions"
          | "productDimensions";

        const stateMap: Record<MasterField, MasterArrayKeys> = {
          account: "accounts",
          season: "seasons",
          subBrand: "subBrands",
          structure: "structures",
          region: "regions",
          displayDimension: "displayDimensions",
          productDimension: "productDimensions"
        };

        state[stateMap[field]].push(item);
      })
      .addCase(deleteMasterItem.fulfilled, (state, { payload }) => {
        const { field, id } = payload;

        const stateMap = {
          account: "accounts",
          season: "seasons",
          subBrand: "subBrands",
          structure: "structures",
          region: "regions",
          displayDimension: "displayDimensions",
          productDimension: "productDimensions"
        } as const;

        const key = stateMap[field];

        state[key] = state[key].filter((item) => item.id !== id);
      });
  },
});

export default masterDataSlice.reducer;
