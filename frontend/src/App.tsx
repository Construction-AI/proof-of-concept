// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { useAuthStore } from './store/authStore';

// Prosta zaślepka na stronę główną
const DashboardPlaceholder = () => {
  const logout = useAuthStore((state) => state.logout);
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Witaj w systemie! Jesteś zalogowany.</h1>
      <button 
        onClick={logout}
        className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
      >
        Wyloguj
      </button>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ścieżki publiczne */}
        <Route path="/login" element={<Login />} />

        {/* Ścieżki chronione - owinięte w naszego "bramkarza" */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<DashboardPlaceholder />} />
          {/* Tu w przyszłości dodamy: <Route path="/editor" element={<Editor />} /> */}
        </Route>

        {/* Jeśli ktoś wpisze dziwny adres, wrzucamy go na stronę główną */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}