import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

type ServiceStatus = 'up' | 'down';

interface HealthData {
  status: string;
  services: {
    api: ServiceStatus;
    qdrant: ServiceStatus;
    minio: ServiceStatus;
  };
}

export const Health = () => {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchHealth = async () => {
    setIsLoading(true);
    try {
      // Uderzamy bezpośrednio w nasz nowy, agregujący endpoint
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/health`);
      setHealthData(response.data);
    } catch (error) {
      // W razie całkowitego padu API
      setHealthData({
        status: 'degraded',
        services: { api: 'down', qdrant: 'down', minio: 'down' }
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const renderBadge = (status?: ServiceStatus) => {
    if (isLoading) return <Badge variant="secondary">Sprawdzanie...</Badge>;
    return status === 'up' 
      ? <Badge className="bg-green-500 hover:bg-green-600">Zdrowy</Badge> 
      : <Badge variant="destructive">Niezdrowy</Badge>;
  };

  const serviceNames: Record<keyof HealthData['services'], string> = {
    api: 'Backend API',
    qdrant: 'Baza wektorowa (Qdrant)',
    minio: 'Magazyn plików (MinIO)'
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Status systemu</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          
          {(['api', 'qdrant', 'minio'] as const).map((key) => (
            <div key={key} className="flex justify-between items-center rounded-lg border p-4 bg-card">
              <span className="font-medium">{serviceNames[key]}</span>
              {renderBadge(healthData?.services[key])}
            </div>
          ))}

          <Button onClick={fetchHealth} disabled={isLoading} className="w-full mt-4" variant="outline">
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