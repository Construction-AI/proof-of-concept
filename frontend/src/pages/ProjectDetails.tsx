import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsService, type Document } from '../api/documents';
import { ProjectChat } from '../components/ProjectChat';
import { UploadZone } from '../components/project/UploadZone';
import { DocumentList } from '../components/project/DocumentList';

export const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // --- ZMODYFIKOWANA FUNKCJA PODGLĄDU ---
  const handlePreview = async (doc: Document) => {
    setIsPreviewLoading(true);
    try {
      const url = await documentsService.getDownloadUrl(doc.id);
      // Otwieramy pobrany, podpisany URL w nowej karcie przeglądarki
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
        <button onClick={() => navigate('/')} className="...">Wróć do projektów</button>

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