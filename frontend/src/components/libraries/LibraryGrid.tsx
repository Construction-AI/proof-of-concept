import { useEffect, useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { librariesService, type TemplateLibrary } from '../../api/libraries';
import { useNavigate } from 'react-router-dom';

interface Props {
  searchQuery: string;
  onOpenLibrary: (lib: TemplateLibrary) => void;
}

export const LibraryGrid = ({ searchQuery }: Props) => {
  const [libraries, setLibraries] = useState<TemplateLibrary[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      librariesService.getAll(searchQuery)
        .then(setLibraries)
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  if (loading) return <Loader2 className="animate-spin mx-auto my-12 text-emerald-500" size={32} />;
  if (libraries.length === 0) return <p className="text-center text-gray-500 py-12">Brak wyników.</p>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {libraries.map((lib) => (
        <div key={lib.id} className="bg-white p-6 rounded-xl shadow-sm border flex flex-col justify-between hover:shadow-md">
          <div>
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-bold uppercase text-emerald-600 bg-emerald-50 px-2 py-1 rounded">{lib.industry}</span>
              {lib.is_global && <span className="text-xs text-gray-400">Systemowe</span>}
            </div>
            <h3 className="text-lg font-bold">{lib.name}</h3>
            <p className="text-sm text-gray-500 mt-2 line-clamp-3">{lib.description}</p>
          </div>
          <button onClick={() => navigate(`/library/${lib.id}`)} className="mt-6 flex items-center justify-center gap-2 w-full bg-gray-50 text-gray-700 border px-4 py-2 rounded-lg font-medium hover:bg-emerald-50 hover:text-emerald-700">
            <Search size={18} /> Przeglądaj
          </button>
        </div>
      ))}
    </div>
  );
};