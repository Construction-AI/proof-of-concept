import { apiClient } from "./client";

export interface Project {
    id: number;
    title: string;
    description: string | null;
    created_at: string;
    last_modified: string;
};

export const projectsService = {
    getAll: async () => {
        const response = await apiClient.get<Project[]>('/projects');
        return response.data;
    },
    create: async (title: string, description: string = '') => {
        const response = await apiClient.post<Project>('/projects/create', {
            title,
            description: description,
        });
        return response.data;
    }
};