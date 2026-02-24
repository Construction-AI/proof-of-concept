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

    register: async (
        email: string,
        password: string,
        first_name: string,
        last_name: string
    ) => {
        const payload = { email, password, first_name, last_name };

        await apiClient.post("/auth/register", payload);

        // Automatically log the user in after successful registration
        await authService.login(email, password);
    },

    fetchMe: async () => {
        const response = await apiClient.get("/auth/me");
        useAuthStore.getState().setUser(response.data);
    }
};