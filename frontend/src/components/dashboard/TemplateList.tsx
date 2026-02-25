import { useEffect, useState } from 'react';
import { FileText, FolderPlus } from 'lucide-react';
import { templatesService } from '../../api/templates'; // Wymaga metody getAll() w serwisie
import { useNavigate } from 'react-router-dom';

interface Props {
  onAssignToLibrary: (id: number) => void;
}

export const TemplateList = ({ onAssignToLibrary }: Props) => {
  const [templates, setTemplates] = useState<any[]>([]);

  const navigate = useNavigate();

  useEffect(() => {
    // Zakładam, że masz metodę pobierania szablonów danego usera
    templatesService.getAll().then(setTemplates).catch(console.error);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4">
      {templates.length === 0 ? <p className="text-gray-500">Brak utworzonych szablonów.</p> : null}

      {templates.map(t => (
        <div key={t.id} onClick={() => navigate(`/templates-editor?templateId=${t.id}`)} className="bg-white p-4 rounded-lg border hover:border-emerald-300 cursor-pointer flex items-center justify-between shadow-sm transition-colors">
          <div className="flex items-center gap-3">
            <FileText className="text-emerald-500" size={24} />
            <span className="font-semibold text-gray-800">{t.name}</span>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAssignToLibrary(t.id);
            }}
            className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-1.5 rounded-md border hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200 transition-colors"
          >
            <FolderPlus size={16} /> Dodaj do biblioteki
          </button>
        </div>
      ))}
    </div>
  );
};