export interface MasterAddResponse {
  status: string;
  message: string;
  data: MasterAdd;
}

export interface MasterAdd {
  name: string;
  active: boolean;
  id: string;
  created_by?:string
  created_at: string;
}