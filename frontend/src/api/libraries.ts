import { apiClient } from './client';

export interface TemplateLibrary {
  id: number;
  name: string;
  industry: string;
  description: string;
  is_global: boolean;
}

export const librariesService = {
  getAll: async (query: string = '', industry: string = '') => {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (industry) params.append('industry', industry);
    const response = await apiClient.get(`/libraries/?${params.toString()}`);
    return response.data;
  },
  // NOWE: Tworzenie biblioteki
  create: async (name: string, industry: string, description: string = '') => {
    const response = await apiClient.post(`/libraries`, {
      name,
      industry,
      description
    });
    return response.data;
  },
  // NOWE: Pobieranie szablonów wewnątrz biblioteki
  getTemplates: async (libraryId: number) => {
    const response = await apiClient.get(`/libraries/${libraryId}/templates`);
    return response.data;
  },

  addTemplate: async (libraryId: number, templateId: number) => {
    const response = await apiClient.post(`/libraries/${libraryId}/add/${templateId}`);
    return response.data;
  }

};