// src/pages/Health.tsx
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

type ServiceStatus = 'loading' | 'healthy' | 'unhealthy';

interface ServiceHealth {
    name: string;
    url: string;
    status: ServiceStatus;
    message?: string;
}

export const Health = () => {
    const [services, setServices] = useState<ServiceHealth[]>([
        {
            name: 'Backend (API + DB)',
            url: 'http://localhost:8000/api/v1/health',
            status: 'loading',
        },
        {
            name: 'MinIO',
            url: 'http://localhost:9000/minio/health/live',
            status: 'loading',
        },
        {
            name: 'Qdrant',
            url: 'http://localhost:6333',
            status: 'loading',
        },
    ]);

    const checkService = async (service: ServiceHealth): Promise<ServiceHealth> => {
        try {
            const response = await axios.get(service.url, { timeout: 5000 });

            if (!response || response.status >= 400) {
                throw new Error('Niepoprawna odpowiedź');
            }

            return {
                ...service,
                status: 'healthy',
                message:
                    response.data?.message ||
                    response.data?.status ||
                    'Usługa działa poprawnie',
            };
        } catch (error) {
            return {
                ...service,
                status: 'unhealthy',
                message: 'Brak połączenia lub błąd usługi',
            };
        }
    };

    const checkAllServices = async () => {
        setServices((prev) =>
            prev.map((service) => ({ ...service, status: 'loading', message: '' }))
        );

        const results = await Promise.all(
            services.map((service) => checkService(service))
        );

        setServices(results);
    };

    useEffect(() => {
        checkAllServices();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const getStatusColor = (status: ServiceStatus) => {
        switch (status) {
            case 'healthy':
                return 'text-green-600';
            case 'unhealthy':
                return 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    const getStatusText = (status: ServiceStatus) => {
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
            <div className="w-full max-w-lg space-y-6 rounded-xl bg-white p-10 shadow-lg">
                <h2 className="text-2xl font-bold text-gray-900 text-center">
                    Status systemu
                </h2>

                <div className="space-y-4">
                    {services.map((service) => (
                        <div
                            key={service.name}
                            className="rounded-lg border p-4"
                        >
                            <div className="flex justify-between items-center">
                                <span className="font-medium text-gray-800">
                                    {service.name}
                                </span>
                                <span
                                    className={`font-semibold ${getStatusColor(
                                        service.status
                                    )}`}
                                >
                                    {getStatusText(service.status)}
                                </span>
                            </div>

                            {service.message && (
                                <p className="mt-2 text-sm text-gray-600">
                                    {service.message}
                                </p>
                            )}
                        </div>
                    ))}
                </div>

                <button
                    onClick={checkAllServices}
                    className="w-full rounded-md bg-blue-600 py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                    Sprawdź ponownie
                </button>

                <div className="text-center text-sm">
                    <Link
                        to="/login"
                        className="font-medium text-blue-600 hover:text-blue-500"
                    >
                        Przejdź do logowania
                    </Link>
                </div>
            </div>
        </div>
    );
};