// src/pages/ProjectDetails.tsx
import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, ArrowLeft, Trash2 } from 'lucide-react';
import { documentsService, type Document } from '../api/documents';
import { ProjectChat } from '../components/ProjectChat';

export const ProjectDetails = () => {
  // 1. REACT: useParams wyciąga zmienną ":id" z paska adresu URL
  const { id } = useParams(); 
  const navigate = useNavigate();

  // 2. REACT: useState przechowuje stan aplikacji. Zmiana stanu powoduje przeładowanie (re-render) widoku.
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // 3. REACT: useRef to odwołanie do fizycznego elementu HTML (tutaj ukrytego <input type="file">)
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 4. REACT: useEffect wykonuje się automatycznie. Pusta tablica [] na końcu oznacza: "wykonaj tylko raz po załadowaniu strony".
  useEffect(() => {
    fetchDocuments();
  }, [id]);

  const fetchDocuments = async () => {
    try {
      const allDocs = await documentsService.getAll();
      // Filtrujemy dokumenty, by pokazać tylko te dla obecnego projektu
      const projectDocs = allDocs.filter(doc => doc.project.id === Number(id));
      setDocuments(projectDocs);
    } catch (error) {
      console.error("Błąd pobierania plików:", error);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; // Pobieramy wybrany plik
    if (!file || !id) return;

    setIsUploading(true);
    try {
      await documentsService.upload(Number(id), file);
      fetchDocuments(); // Odświeżamy listę po udanym wgraniu
    } catch (error) {
      console.error("Błąd wgrywania:", error);
      alert("Nie udało się wgrać pliku.");
    } finally {
      setIsUploading(false);
      // Czyścimy input, by móc wgrać ten sam plik ponownie, jeśli to konieczne
      if (fileInputRef.current) fileInputRef.current.value = ''; 
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm("Na pewno usunąć ten plik? Zniknie z bazy wektorowej Qdrant.")) return;
    
    try {
      await documentsService.delete(docId);
      fetchDocuments(); // Odśwież listę
    } catch (error) {
      console.error("Błąd usuwania:", error);
    }
  };

  return (
    // TAILWIND: bg-gray-50 (jasnoszare tło), min-h-screen (minimalna wysokość na cały ekran)
    <div className="min-h-screen bg-gray-50 p-6">
      
      {/* TAILWIND: max-w-5xl (maksymalna szerokość), mx-auto (wyśrodkowanie w poziomie - margin x auto) */}
      <div className="max-w-5xl mx-auto">
        
        {/* Przycisk powrotu */}
        <button 
          onClick={() => navigate('/')}
          // TAILWIND: flex, items-center (wyśrodkowanie w pionie), gap-2 (odstęp między ikoną a tekstem)
          // hover:text-blue-600 (zmiana koloru tekstu po najechaniu myszką)
          className="flex items-center gap-2 text-gray-500 hover:text-blue-600 mb-6 transition-colors"
        >
          <ArrowLeft size={20} /> Wróć do projektów
        </button>

        {/* Strefa Wgrywania (Upload Zone) */}
        {/* TAILWIND: border-2 (grubość ramki 2px), border-dashed (przerywana linia), rounded-xl (zaokrąglone rogi) */}
        <div className="bg-white p-10 rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-center mb-8">
          
          <UploadCloud className="text-gray-400 mb-4" size={48} />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Zasil bazę wiedzy RAG
          </h3>
          <p className="text-gray-500 mb-6">
            Wgraj dokumenty (PDF, DOCX), które posłużą jako kontekst dla tego projektu.
          </p>

          {/* Magia wgrywania: Ukrywamy prawdziwy <input> i stylujemy <label>, który działa jak przycisk */}
          <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleFileSelect}
            className="hidden" // TAILWIND: ukrywa element
            accept=".pdf,.txt,.docx" // Ograniczenie formatów
          />
          <button
            onClick={() => fileInputRef.current?.click()} // Kliknięcie przycisku symuluje kliknięcie w input
            disabled={isUploading}
            // TAILWIND: px-6 py-2 (padding w poziomie i pionie), disabled:opacity-50 (półprzezroczysty gdy zablokowany)
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium"
          >
            {isUploading ? "Indeksowanie w Qdrant..." : "Wybierz plik z dysku"}
          </button>
        </div>

        {/* Lista wgranych dokumentów */}
        <h3 className="text-lg font-bold text-gray-900 mb-4">Wgrane dokumenty:</h3>
        
        {documents.length === 0 ? (
          <p className="text-gray-500 italic">Brak dokumentów w tym projekcie.</p>
        ) : (
          // TAILWIND: grid (siatka), gap-4 (odstępy 16px między kafelkami)
          <div className="grid gap-4">
            {documents.map((doc) => (
              // TAILWIND: flex, justify-between (rozpycha elementy do lewej i prawej krawędzi)
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

                <button 
                  onClick={() => handleDelete(doc.id)}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors"
                  title="Usuń dokument"
                >
                  <Trash2 size={20} />
                </button>

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