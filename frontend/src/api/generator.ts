// src/api/generator.ts
import { apiClient } from './client';

export const generatorService = {
  generatePdf: async (projectId: number, templateId: number) => {
    // Wymuszamy na axiosie odbiór danych binarnych (blob)
    const response = await apiClient.post(
      `generator/generate`,
      {
        project_id: projectId,
        template_id: templateId
      },
      { responseType: 'blob' } 
    );
    
    // Tworzymy wirtualny link do pobrania pliku z pamięci RAM przeglądarki
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    // Próbujemy wyciągnąć polską nazwę pliku z nagłówka, a jak się nie uda, dajemy domyślną
    const disposition = response.headers['content-disposition'];
    let fileName = 'Raport.pdf';
    if (disposition && disposition.includes('filename*=')) {
      fileName = decodeURIComponent(disposition.split("filename*=utf-8''")[1]);
    }
    
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
};