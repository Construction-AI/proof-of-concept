import { create } from 'zustand';

export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string
}

interface AuthState {
    accessToken: string | null;
    refreshToken: string | null;
    user: User | null;
    isAuthenticated: boolean;

    setTokens: (access: string, refresh: string) => void;
    setUser: (user: User) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    accessToken: localStorage.getItem("accessToken"),
    refreshToken: localStorage.getItem("refreshToken"),
    user: null,
    isAuthenticated: !!localStorage.getItem("accessToken"),
    
    setTokens: (access, refresh) => {
        localStorage.setItem("accessToken", access);
        localStorage.setItem("refreshToken", refresh);
        set({ accessToken: access, refreshToken: refresh, isAuthenticated: true })
    },

    setUser: (user) => set({ user }),

    logout: () => {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false })
    }
}));