import { FolderGit2, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export const Navbar = () => {
  const { user, logout } = useAuthStore();
  return (
    <nav className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
      <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
        <FolderGit2 className="text-blue-600" /> RAG Builder
      </h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600">
          Zalogowany jako: <span className="font-semibold">{user?.email}</span>
        </span>
        <button onClick={logout} className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-full">
          <LogOut size={20} />
        </button>
      </div>
    </nav>
  );
};