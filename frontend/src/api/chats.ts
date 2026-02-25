import { apiClient } from './client';

export interface Chat {
  id: number;
  title: string;
  project_id: number;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

export const chatsService = {
  getProjectChats: async (projectId: number): Promise<Chat[]> => {
    const res = await apiClient.get(`/projects/${projectId}/chats`);
    return res.data;
  },
  getChatMessages: async (chatId: number): Promise<Message[]> => {
    const res = await apiClient.get(`/chats/${chatId}`);
    return res.data;
  },
  // Zakładam, że masz endpoint do tworzenia nowego czatu (zwraca obiekt Chat)
  createChat: async (projectId: number, title: string = 'Nowa konwersacja'): Promise<Chat> => {
    const res = await apiClient.post(`/projects/${projectId}/chats`, { title });
    return res.data;
  },
  sendMessage: async (chatId: number, message: string): Promise<string> => {
    const res = await apiClient.post(`/chats/${chatId}/messages`, { chat_id: chatId, content: message });
    return res.data; // Zakładam, że backend zwraca samego stringa (odpowiedź AI)
  }
};