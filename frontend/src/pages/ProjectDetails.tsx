// src/pages/ProjectDetails.tsx
import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ArrowLeft, Trash2, Eye } from 'lucide-react'; // Usunąłem nieużywany X
import { documentsService, type Document } from '../api/documents';
import { ProjectChat } from '../components/ProjectChat';

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

        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-500 hover:text-blue-600 mb-6 transition-colors"
        >
          <ArrowLeft size={20} /> Wróć do projektów
        </button>

        <div className="bg-white p-10 rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-center mb-8">
          <UploadCloud className="text-gray-400 mb-4" size={48} />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Zasil bazę wiedzy RAG
          </h3>
          <p className="text-gray-500 mb-6">
            Wgraj dokumenty (PDF, DOCX), które posłużą jako kontekst dla tego projektu.
          </p>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.txt,.docx"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium"
          >
            {isUploading ? "Indeksowanie w Qdrant..." : "Wybierz plik z dysku"}
          </button>
        </div>

        <h3 className="text-lg font-bold text-gray-900 mb-4">Wgrane dokumenty:</h3>

        {documents.length === 0 ? (
          <p className="text-gray-500 italic">Brak dokumentów w tym projekcie.</p>
        ) : (
          <div className="grid gap-4">
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
                    onClick={() => handlePreview(doc)}
                    disabled={isPreviewLoading}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors disabled:opacity-50"
                    title="Otwórz dokument"
                  >
                    <Eye size={20} />
                  </button>

                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                    title="Usuń dokument"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>

              </div>
            ))}
          </div>
        )}

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Przeszukaj bazę wiedzy</h2>
          <ProjectChat projectId={Number(id)} />
        </div>
        
      </div>
    </div>
  );
};