import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderGit2, Plus, LogOut, LayoutTemplate } from 'lucide-react'; // Dodano LayoutTemplate
import { projectsService, type Project } from '../api/projects';
import { useAuthStore } from '../store/authStore';

export const Dashboard = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newTitle, setNewTitle] = useState('');

  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const data = await projectsService.getAll();
      setProjects(data);
    } catch (error) {
      console.error('Błąd pobierania projektów', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      await projectsService.create(newTitle);
      setNewTitle('');
      fetchProjects();
    } catch (error) {
      console.error('Błąd tworzenia projektu', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
          <FolderGit2 className="text-blue-600" />
          RAG Builder
        </h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            Zalogowany jako: <span className="font-semibold">{user?.email}</span>
          </span>
          <button onClick={logout} className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors">
            <LogOut size={20} />
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">

        {/* --- NOWA SEKCJA: NARZĘDZIA GŁÓWNE --- */}
        <div className="mb-10 p-6 bg-linear-to-r from-blue-600 to-indigo-700 rounded-xl text-white shadow-lg flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">Kreator Szablonów</h2>
            <p className="text-blue-100 text-sm">Zbuduj strukturę dokumentów, która zostanie wypełniona danymi przez AI.</p>
          </div>
          <button
            onClick={() => navigate('/schema-editor')}
            className="flex items-center gap-2 bg-white text-blue-700 px-6 py-3 rounded-lg font-bold hover:bg-blue-50 transition-colors shadow-sm"
          >
            <LayoutTemplate size={20} />
            Otwórz Edytor
          </button>
        </div>

        {/* --- SEKCJA PROJEKTÓW --- */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Twoje Projekty (Baza Kontekstu)</h2>
        </div>

        <form onSubmit={handleCreateProject} className="mb-8 flex gap-4 bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          <input
            type="text"
            placeholder="Nazwa nowego projektu..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="flex-1 rounded-md border border-gray-300 px-4 py-2 focus:border-blue-500 focus:ring-blue-500 outline-none"
          />
          <button
            type="submit"
            disabled={!newTitle.trim()}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
          >
            <Plus size={20} />
            Utwórz
          </button>
        </form>

        {isLoading ? (
          <p className="text-gray-500">Ładowanie projektów...</p>
        ) : projects.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
            <p className="text-gray-500">Brak projektów. Utwórz swój pierwszy projekt budowlany powyżej.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/projects/${project.id}`)}
                className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 cursor-pointer transition-all group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <FolderGit2 className="text-gray-400 group-hover:text-blue-500 transition-colors" size={32} />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{project.title}</h3>
                </div>
                <p className="text-sm text-gray-500 mt-4 border-t border-gray-100 pt-3">
                  Utworzono: {new Date(project.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};