// src/pages/Register.tsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../api/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export const Register = () => {
  const [formData, setFormData] = useState({
    email: '', firstName: '', lastName: '', password: '', confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Hasła nie są identyczne.');
      return;
    }

    setIsLoading(true);
    try {
      await authService.register(formData.email, formData.password, formData.firstName, formData.lastName);
      navigate('/login');
    } catch (err) {
      setError('Nie udało się utworzyć konta. Użytkownik może już istnieć.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Utwórz konto</CardTitle>
          <CardDescription className="text-center">
            Dołącz do systemu generatora dokumentów RAG
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">Imię</Label>
                <Input id="firstName" required value={formData.firstName} onChange={handleChange} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Nazwisko</Label>
                <Input id="lastName" required value={formData.lastName} onChange={handleChange} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Adres email</Label>
              <Input id="email" type="email" required value={formData.email} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Hasło</Label>
              <Input id="password" type="password" required value={formData.password} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Potwierdź hasło</Label>
              <Input id="confirmPassword" type="password" required value={formData.confirmPassword} onChange={handleChange} />
            </div>

            {error && <p className="text-sm text-destructive text-center">{error}</p>}

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Tworzenie konta...' : 'Zarejestruj się'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center">
          <p className="text-sm text-muted-foreground">
            Masz już konto?{' '}
            <Link to="/login" className="text-primary hover:underline">
              Zaloguj się
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};