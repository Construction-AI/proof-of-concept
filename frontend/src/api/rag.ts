import { apiClient } from "./client";

export interface Source {
    source: string;
    node_confidence: number;
    exact_sentence: string;
    context_window: string;
};

export interface DynamicRAGResponse {
    answer: string;
    llm_confidence: number;
    reasoning: string;
    sources: Source[];
};

export const ragService = {
    askProject: async (projectId: number, instruction: string) => {
        const response = await apiClient.post<DynamicRAGResponse>("/rag/q/dynamic", {
            instruction: instruction,
            output_format: "string",
            project_id: projectId,
        });
        return response.data;
    }
};