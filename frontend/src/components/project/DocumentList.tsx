// src/components/project/DocumentList.tsx
import { FileText, Eye, Trash2 } from 'lucide-react';
import type { Document } from '../../api/documents';

interface DocumentListProps {
  documents: Document[];
  isPreviewLoading: boolean;
  onPreview: (doc: Document) => void;
  onDelete: (id: number) => void;
}

export const DocumentList = ({ documents, isPreviewLoading, onPreview, onDelete }: DocumentListProps) => {
  if (documents.length === 0) {
    return <p className="text-gray-500 italic">Brak dokumentów w tym projekcie.</p>;
  }

  return (
    <div className="grid gap-4 mb-12">
      {documents.map((doc) => (
        <div key={doc.id} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <FileText className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{doc.file_name}</p>
              <p className="text-sm text-gray-500">
                Dodano: {new Date(doc.created_at).toLocaleDateString()} • {Math.round(doc.size / 1024)} KB
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onPreview(doc)}
              disabled={isPreviewLoading}
              className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors disabled:opacity-50"
              title="Otwórz dokument"
            >
              <Eye size={20} />
            </button>
            <button
              onClick={() => onDelete(doc.id)}
              className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
              title="Usuń dokument"
            >
              <Trash2 size={20} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};