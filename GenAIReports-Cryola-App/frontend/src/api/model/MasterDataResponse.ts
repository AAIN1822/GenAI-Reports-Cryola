export interface MasterDataResponse {
  status: string;
  message: string;
  data: MasterData;
}

export interface MasterData {
  total: number;
  items: MasterDataItem[];
}
export interface MasterDataItem {
  id: string;
  name: string;
  created_by?: string;
}