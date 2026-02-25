// src/components/modals/LibraryAssignModal.tsx
import { useEffect, useState } from 'react';
import { X, Loader2, Plus } from 'lucide-react';
import { librariesService, type TemplateLibrary } from '../../api/libraries';

interface Props {
  templateId: number;
  onClose: () => void;
}

export const LibraryAssignModal = ({ templateId, onClose }: Props) => {
  const [libraries, setLibraries] = useState<TemplateLibrary[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<number | null>(null);

  useEffect(() => {
    librariesService.getAll().then(data => {
      // Filtrujemy tylko własne biblioteki (bez globalnych)
      setLibraries(data.filter((lib: any) => !lib.is_global));
      setLoading(false);
    });
  }, []);

  const handleAssign = async (libraryId: number) => {
    setProcessingId(libraryId);
    try {
      await librariesService.addTemplate(libraryId, templateId);
      alert('Przypisano!');
    } catch (e) {
      alert('Błąd przypisywania.');
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold">Przypisz do biblioteki</h3>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        
        {loading ? <Loader2 className="animate-spin mx-auto my-4 text-blue-500" /> : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {libraries.length === 0 ? <p className="text-gray-500 text-sm">Brak własnych bibliotek.</p> : null}
            {libraries.map(lib => (
              <div key={lib.id} className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50">
                <span className="font-medium">{lib.name}</span>
                <button 
                  onClick={() => handleAssign(lib.id)}
                  disabled={processingId === lib.id}
                  className="text-blue-600 bg-blue-50 p-2 rounded-md hover:bg-blue-100"
                >
                  {processingId === lib.id ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};