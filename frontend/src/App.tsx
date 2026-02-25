// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Dashboard } from './pages/Dashboard';
import { ProjectDetails } from './pages/ProjectDetails';
import { SchemaBuilder } from './pages/SchemaBuilder';
import { Register } from './pages/Register';
import { Health } from './pages/Health';
import { Library } from './pages/Library';
import { LibraryTemplates } from './pages/LibraryTemplates';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ścieżki publiczne */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/health" element={<Health />} />

        {/* Ścieżki chronione - owinięte w naszego "bramkarza" */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:id" element={<ProjectDetails />} />
          <Route path="/templates-editor" element={<SchemaBuilder />} />
          <Route path="/library" element={<Library />} />
          <Route path="/library/:id" element={<LibraryTemplates />} />
        </Route>

        {/* Jeśli ktoś wpisze dziwny adres, wrzucamy go na stronę główną */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}