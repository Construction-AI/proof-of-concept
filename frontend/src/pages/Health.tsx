// src/pages/Health.tsx
import { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';

export const Health = () => {
    const [status, setStatus] = useState<'loading' | 'healthy' | 'unhealthy'>('loading');
    const [message, setMessage] = useState('');

    const checkHealth = async () => {
        try {
            setStatus('loading');
            const response = await apiClient.get('/health');

            if (!response.data) {
                throw new Error('Błąd odpowiedzi serwera');
            }

            const data = await response.data;
            setStatus('healthy');
            setMessage(data.message || 'Serwer działa poprawnie');
        } catch (error) {
            setStatus('unhealthy');
            setMessage('Brak połączenia z serwerem');
        }
    };

    useEffect(() => {
        checkHealth();
    }, []);

    const getStatusColor = () => {
        switch (status) {
            case 'healthy':
                return 'text-green-600';
            case 'unhealthy':
                return 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'healthy':
                return 'Zdrowy';
            case 'unhealthy':
                return 'Niezdrowy';
            default:
                return 'Sprawdzanie...';
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50">
            <div className="w-full max-w-md space-y-6 rounded-xl bg-white p-10 shadow-lg text-center">
                <h2 className="text-2xl font-bold text-gray-900">
                    Status systemu
                </h2>

                <div className={`text-lg font-semibold ${getStatusColor()}`}>
                    {getStatusText()}
                </div>

                {message && (
                    <p className="text-sm text-gray-600">
                        {message}
                    </p>
                )}

                <button
                    onClick={checkHealth}
                    className="w-full rounded-md bg-blue-600 py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Sprawdź ponownie
                </button>
                <div className="text-center text-sm">
                    <p className="text-gray-600">
                        <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                            Przejdź do logowania
                        </Link>
                    </p>
                </div>
            </div>

        </div>
    );
};