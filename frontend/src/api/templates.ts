import { apiClient } from "./client";
import type { SchemaNode } from "../store/schemaStore";

export const templatesService = {
    saveNodes: async (templateId: number, nodes: SchemaNode[]) => {
        const response = await apiClient.put<SchemaNode[]>(`/templates/${templateId}/nodes`, nodes);
        return response.data;
    },
};