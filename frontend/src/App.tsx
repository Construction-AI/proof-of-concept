// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Dashboard } from './pages/Dashboard';
import { ProjectDetails } from './pages/ProjectDetails';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ścieżki publiczne */}
        <Route path="/login" element={<Login />} />

        {/* Ścieżki chronione - owinięte w naszego "bramkarza" */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:id" element={<ProjectDetails />} />
        </Route>

        {/* Jeśli ktoś wpisze dziwny adres, wrzucamy go na stronę główną */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}