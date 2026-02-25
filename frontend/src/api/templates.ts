import { apiClient } from "./client";
import type { SchemaNode, TemplateResponse } from "../store/schemaStore";

export const templatesService = {
    saveNodes: async (templateId: number, nodes: SchemaNode[]) => {
        const response = await apiClient.put<SchemaNode[]>(`/templates/${templateId}/nodes`, nodes);
        return response.data;
    },

    getNodes: async (templateId: number) => {
        const response = await apiClient.get<SchemaNode[]>(`/templates/${templateId}/nodes`);
        return response.data;
    },

    getAll: async () => {
        const response = await apiClient.get<TemplateResponse[]>(`/templates`);
        return response.data;
    },

    create: async (name: string, description: string = "") => {
        const response = await apiClient.post(`/templates`, {
            name,
            description
        });
        return response.data;
    },
    
    delete: async (templateId: number) => {
        await apiClient.delete(`/templates/${templateId}`);
    }
};