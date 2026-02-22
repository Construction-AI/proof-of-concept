import { apiClient } from "./client";

export interface AnswerWithConfidence {
    answer: string;
    confidence_score: number;
    reasoning: string;
};

export interface FinalResponse {
    structured_answer: AnswerWithConfidence;
    sources: string[];
};

export const ragService = {
    askProject: async (projectId: number, question: string) => {
        const response = await apiClient.post<FinalResponse>("/rag/c/project", {
            project_id: projectId,
            question: question
        });
        return response.data;
    }
};