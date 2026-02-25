import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Copy, Edit, Loader2, ArrowLeft } from 'lucide-react';
import { librariesService } from '../api/libraries';
import { templatesService } from '../api/templates';

export const LibraryTemplates = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copyingId, setCopyingId] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      librariesService.getTemplates(Number(id))
        .then(setTemplates)
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleCopy = async (templateId: number) => {
    setCopyingId(templateId);
    try {
      await templatesService.copyTemplate(templateId);
      alert("Skopiowano do Twoich szablonów!");
    } catch (e) {
      alert("Błąd kopiowania.");
    } finally {
      setCopyingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <button onClick={() => navigate('/library')} className="p-2 bg-white rounded-full shadow-sm hover:bg-gray-100">
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Zawartość biblioteki</h1>
        </div>

        {loading ? (
          <Loader2 className="animate-spin mx-auto mt-12 text-emerald-500" size={32} />
        ) : templates.length === 0 ? (
          <p className="text-center text-gray-500 py-12">Ta biblioteka nie posiada jeszcze szablonów.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map(t => (
              <div key={t.id} className="bg-white p-6 rounded-xl shadow-sm border flex flex-col justify-between hover:shadow-md">
                <div className="flex items-center gap-3 mb-6">
                  <div className="bg-emerald-50 p-3 rounded-lg">
                    <FileText className="text-emerald-600" size={24} />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">{t.name}</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-2 mt-4">
                  <button 
                    onClick={() => navigate(`/templates-editor?templateId=${t.id}`)} 
                    className="flex items-center justify-center gap-2 bg-gray-50 text-gray-700 border px-3 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                  >
                    <Edit size={16} /> Edytuj
                  </button>
                  <button 
                    onClick={() => handleCopy(t.id)} 
                    disabled={copyingId === t.id}
                    className="flex items-center justify-center gap-2 bg-blue-50 text-blue-600 px-3 py-2 rounded-lg font-medium hover:bg-blue-600 hover:text-white transition-colors disabled:opacity-50"
                  >
                    {copyingId === t.id ? <Loader2 size={16} className="animate-spin" /> : <Copy size={16} />} 
                    Kopiuj
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};