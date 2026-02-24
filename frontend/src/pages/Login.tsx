// src/pages/Login.tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../api/auth';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Zatrzymuje domyślne przeładowanie strony po wysłaniu formularza
    setError('');
    setIsLoading(true);

    try {
      // Wywołujemy nasz serwis, który robi request i zapisuje tokeny w Zustandzie
      await authService.login(username, password);

      // Jeśli się udało, przenosimy użytkownika na stronę główną projektów
      navigate('/');
    } catch (err) {
      setError('Nieprawidłowy login lub hasło.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-10 shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Zaloguj się
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            System generatora dokumentów RAG
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4 rounded-md shadow-sm">
            <div>
              <label className="sr-only" htmlFor="username">Nazwa użytkownika</label>
              <input
                id="username"
                type="text"
                required
                className="relative block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="Nazwa użytkownika (Email)"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label className="sr-only" htmlFor="password">Hasło</label>
              <input
                id="password"
                type="password"
                required
                className="relative block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="Hasło"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={isLoading}
            className="group relative flex w-full justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
          >
            {isLoading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
          <div className="text-center">
            <Link
              to="/register"
              className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline transition-colors duration-200"
            >
              Zarejestruj się
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};