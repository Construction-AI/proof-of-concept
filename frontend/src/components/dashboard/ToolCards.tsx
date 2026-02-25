import { useNavigate } from 'react-router-dom';
import { LayoutTemplate, Library as LibraryIcon } from 'lucide-react';

export const ToolCards = () => {
  const navigate = useNavigate();
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
      <div className="p-6 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl text-white shadow-lg flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-1">Kreator Szablonów</h2>
          <p className="text-blue-100 text-sm">Zbuduj strukturę dokumentów dla AI.</p>
        </div>
        <button onClick={() => navigate('/templates-editor')} className="flex items-center gap-2 bg-white text-blue-700 px-6 py-3 rounded-lg font-bold hover:bg-blue-50 shadow-sm">
          <LayoutTemplate size={20} /> Otwórz
        </button>
      </div>
      <div className="p-6 bg-gradient-to-r from-emerald-600 to-teal-700 rounded-xl text-white shadow-lg flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-1">Biblioteka Szablonów</h2>
          <p className="text-emerald-100 text-sm">Przeglądaj i kopiuj gotowe szablony dla branż.</p>
        </div>
        <button onClick={() => navigate('/library')} className="flex items-center gap-2 bg-white text-emerald-700 px-6 py-3 rounded-lg font-bold hover:bg-emerald-50 shadow-sm">
          <LibraryIcon size={20} /> Przeglądaj
        </button>
      </div>
    </div>
  );
};