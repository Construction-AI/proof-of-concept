import { apiClient } from "./client";
import type { User } from "../store/authStore";
import type { Project } from "./projects";

export interface Document {
    id: number;
    file_name: string;
    size: number;
    created_at: string;
    content_type: string;
    owner: User;
    project: Project;
};

export interface DocumentValidation {
    db: boolean;
    file_storage: boolean;
    vector_store: boolean;
}

export const documentsService = {
    getAll: async () => {
        const response = await apiClient.get<Document[]>("/documents");
        return response.data;
    },

    upload: async (projectId: number, file: File) => {
        const formData = new FormData();
        
        formData.append("project_id", projectId.toString());
        formData.append("file", file);

        const response = await apiClient.post<Document>("/documents/create", formData, {
            headers: {
                "Content-Type": "multipart/form-data"
            },
        });
        return response.data;
    },

    delete: async (documentId: number) => {
        await apiClient.delete(`/documents/${documentId}`);
    },

    getDownloadUrl: async (documentId: number) => {
        const response = await apiClient.get<string>(`/documents/download_url/${documentId}`);
        return response.data;
    },

    validate: async (documentId: number) => {
        const response = await apiClient.get<DocumentValidation>(`/documents/${documentId}/validate`);
        return response.data;
    },

    reupload: async (documentId: number, file: File) => {
        const formData = new FormData();
        
        formData.append("file", file);

        const response = await apiClient.post<Document>(`/documents/${documentId}/reupload`, formData, {
            headers: {
                "Content-Type": "multipart/form-data"
            },
        });
        return response.data;
    },
};