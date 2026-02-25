import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsService, type Document } from '../api/documents';
import { ProjectChat } from '../components/ProjectChat';
import { UploadZone } from '../components/project/UploadZone';
import { DocumentList } from '../components/project/DocumentList';
import { LayoutTemplate } from 'lucide-react';

export const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const handlePreview = async (doc: Document) => {
    setIsPreviewLoading(true);
    try {
      const url = await documentsService.getDownloadUrl(doc.id);
      window.open(url, '_blank', 'noopener,noreferrer');
    } catch (error) {
      console.error("Błąd pobierania linku podglądu:", error);
      alert("Nie udało się otworzyć podglądu.");
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchDocuments();
  }, [id]);

  const fetchDocuments = async () => {
    try {
      const allDocs = await documentsService.getAll();
      const projectDocs = allDocs.filter(doc => doc.project.id === Number(id));
      setDocuments(projectDocs);
    } catch (error) {
      console.error("Błąd pobierania plików:", error);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !id) return;

    setIsUploading(true);
    try {
      await documentsService.upload(Number(id), file);
      fetchDocuments();
    } catch (error) {
      console.error("Błąd wgrywania:", error);
      alert("Nie udało się wgrać pliku.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm("Na pewno usunąć ten plik? Zniknie z bazy wektorowej Qdrant.")) return;

    try {
      await documentsService.delete(docId);
      fetchDocuments();
    } catch (error) {
      console.error("Błąd usuwania:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors">
            Wróć do projektów
          </button>

          <button
            onClick={() => navigate(`/templates-editor`)}
            className="flex items-center gap-2 bg-linear-to-r from-blue-600 to-indigo-700 text-white px-6 py-2 rounded-lg font-bold hover:shadow-lg transition-all"
          >
            <LayoutTemplate size={20} />
            Kreator Raportów
          </button>
        </div>

        <UploadZone isUploading={isUploading} onFileSelect={handleFileSelect} />

        <h3 className="text-lg font-bold text-gray-900 mb-4">Wgrane dokumenty:</h3>
        <DocumentList
          documents={documents}
          isPreviewLoading={isPreviewLoading}
          onPreview={handlePreview}
          onDelete={handleDelete}
        />

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Przeszukaj bazę wiedzy</h2>
          <ProjectChat projectId={Number(id)} />
        </div>
      </div>
    </div>
  );
};