import axios, { type AxiosResponse } from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

apiClient.interceptors.request.use(
    (config) => {
        const { accessToken }  = useAuthStore.getState()

        if (accessToken && config.headers) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error)
    }
)

apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const { refreshToken, setTokens, logout } = useAuthStore.getState();

            if (refreshToken) {
                try {
                    const refreshResponse: AxiosResponse = await axios.post(`${API_URL}/auth/refresh`, {
                        refresh_token: refreshToken
                    });

                    const { access_token, refresh_token } = refreshResponse.data;

                    setTokens(access_token, refresh_token);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;

                    return apiClient(originalRequest)
                } catch (refreshError) {
                    logout();
                    return Promise.reject(refreshError);
                }
            } else {
                logout();
            }
        } 
        return Promise.reject(error);
    }
);
