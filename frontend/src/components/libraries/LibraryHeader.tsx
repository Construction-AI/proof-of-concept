import { Search, Library as LibIcon, ArrowLeft, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Props {
  onSearch: (val: string) => void;
  onCreateClick: () => void;
}

export const LibraryHeader = ({ onSearch, onCreateClick }: Props) => {
  const navigate = useNavigate();
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/')} className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-100">
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900">
            <LibIcon className="text-emerald-600" /> Baza Wiedzy - Biblioteki
          </h1>
        </div>
        <button onClick={onCreateClick} className="flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700">
          <Plus size={20} /> Utwórz bibliotekę
        </button>
      </div>
      <div className="bg-white p-4 rounded-xl shadow-sm flex items-center gap-3">
        <Search className="text-gray-400" />
        <input 
          type="text" 
          placeholder="Szukaj po nazwie..." 
          onChange={(e) => onSearch(e.target.value)} 
          className="flex-1 outline-none bg-transparent" 
        />
      </div>
    </div>
  );
};