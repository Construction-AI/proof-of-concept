// src/pages/Health.tsx
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

type ServiceStatus = 'loading' | 'healthy' | 'unhealthy';

interface ServiceHealth {
  name: string;
  url: string;
  status: ServiceStatus;
  message?: string;
}

export const Health = () => {
  const [services, setServices] = useState<ServiceHealth[]>([
    { name: 'Backend (API + DB)', url: 'http://localhost:8000/api/v1/health', status: 'loading' },
    { name: 'MinIO', url: 'http://localhost:9000/minio/health/live', status: 'loading' },
    { name: 'Qdrant', url: 'http://localhost:6333', status: 'loading' },
  ]);

  const checkService = async (service: ServiceHealth): Promise<ServiceHealth> => {
    try {
      const response = await axios.get(service.url, { timeout: 5000 });
      if (!response || response.status >= 400) throw new Error('Error');
      return {
        ...service,
        status: 'healthy',
        message: response.data?.message || response.data?.status || 'Usługa działa poprawnie',
      };
    } catch {
      return { ...service, status: 'unhealthy', message: 'Brak połączenia lub błąd usługi' };
    }
  };

  const checkAllServices = async () => {
    setServices((prev) => prev.map((s) => ({ ...s, status: 'loading', message: '' })));
    const results = await Promise.all(services.map(checkService));
    setServices(results);
  };

  useEffect(() => {
    checkAllServices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getBadgeVariant = (status: ServiceStatus) => {
    if (status === 'healthy') return 'default'; // lub np. customowy 'success' jeśli masz
    if (status === 'unhealthy') return 'destructive';
    return 'secondary';
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Status systemu</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {services.map((service) => (
            <div key={service.name} className="flex flex-col rounded-lg border p-4 space-y-2 bg-card">
              <div className="flex justify-between items-center">
                <span className="font-medium">{service.name}</span>
                <Badge variant={getBadgeVariant(service.status)}>
                  {service.status === 'loading' ? 'Sprawdzanie...' : service.status === 'healthy' ? 'Zdrowy' : 'Niezdrowy'}
                </Badge>
              </div>
              {service.message && (
                <p className="text-sm text-muted-foreground">{service.message}</p>
              )}
            </div>
          ))}
          <Button onClick={checkAllServices} className="w-full mt-4" variant="outline">
            Sprawdź ponownie
          </Button>
        </CardContent>
        <CardFooter className="flex justify-center">
          <Link to="/login" className="text-sm text-primary hover:underline">
            Przejdź do logowania
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
};