export interface AIResponse {
  status: string;
  message: string;
  data: AIData;
}

export interface AIData {
  job_id: string;
  status: string;
}

type aiRefinementResponse = {
    url: string;
    score: number;
    feedback_prompt: string;
}

export interface aiRegenerationResponse {
  status: string;
  message: string;
  data: aiRefinementResponse
}

export interface AIJobStatusResponse {
  status: string;
  message: string;
  data: AIJobStatus
}

type AIJobStatus = {
    id: string;
    project_id: string;
    stage: string;
    status: string;
    error: string;
    message: string;
}