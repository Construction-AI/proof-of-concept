import { apiClient } from "./client";
import { useAuthStore } from "../store/authStore";

export const authService = {
    login: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const response = await apiClient.post("/auth/token", formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
        });

        const { access_token, refresh_token } = response.data;

        useAuthStore.getState().setTokens(access_token, refresh_token);

        await authService.fetchMe();
    },

    fetchMe: async () => {
        const response = await apiClient.get("/auth/me");
        useAuthStore.getState().setUser(response.data);
    }
};