import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsService, type Document } from '../api/documents';
import { chatsService, type Chat } from '../api/chats';
import { UploadZone } from '../components/project/UploadZone';
import { DocumentList } from '../components/project/DocumentList';
import { ChatWindow } from '../components/chat/ChatWindow';
import { ArrowLeft, MessageSquare, Plus } from 'lucide-react';

export const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const projectId = Number(id);

  // --- STAN DOKUMENTÓW ---
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- STAN CZATÓW ---
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);

  useEffect(() => {
    if (projectId) {
      fetchDocuments();
      chatsService.getProjectChats(projectId).then(setChats);
    }
  }, [projectId]);

  // --- LOGIKA DOKUMENTÓW ---
  const fetchDocuments = async () => {
    try {
      const allDocs = await documentsService.getAll();
      const projectDocs = allDocs.filter(doc => doc.project.id === projectId);
      setDocuments(projectDocs);
    } catch (error) {
      console.error("Błąd pobierania plików:", error);
    }
  };

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

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !projectId) return;

    setIsUploading(true);
    try {
      await documentsService.upload(projectId, file);
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

  // --- LOGIKA CZATÓW ---
  const handleCreateChat = async () => {
    try {
      const newChat = await chatsService.createChat(projectId);
      setChats([newChat, ...chats]);
      setActiveChatId(newChat.id);
    } catch (e) {
      alert("Nie udało się utworzyć czatu.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center">
      <div className="w-full max-w-6xl">
        {/* HEADER */}
        <div className="text-black py-2 flex items-center mb-4">
          <button onClick={() => navigate(`/dashboard`)} className="flex items-center gap-1 hover:text-blue-600 transition-colors">
            <ArrowLeft size={16} /> Powrót do panelu użytkownika
          </button>
        </div>

        {/* SEKCJA DOKUMENTÓW */}
        <div className="mb-10">
          <UploadZone isUploading={isUploading} onFileSelect={handleFileSelect} />
          <h3 className="text-lg font-bold text-gray-900 mt-6 mb-4">Wgrane dokumenty:</h3>
          <DocumentList
            documents={documents}
            isPreviewLoading={isPreviewLoading}
            onPreview={handlePreview}
            onDelete={handleDelete}
          />
        </div>

        {/* SEKCJA CZATÓW */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Przeszukaj bazę wiedzy</h2>
        <div className="flex h-150 gap-6">
          
          {/* LEWA KOLUMNA: Lista czatów */}
          <div className="w-1/3 flex flex-col gap-4">
            <button 
              onClick={handleCreateChat}
              className="flex items-center justify-center gap-2 w-full bg-emerald-600 text-white p-3 rounded-xl font-bold hover:bg-emerald-700 transition-colors shadow-sm"
            >
              <Plus size={20} /> Nowy czat z bazą
            </button>

            <div className="bg-white rounded-xl shadow-sm border p-4 flex-1 overflow-y-auto space-y-2">
              <h3 className="font-semibold text-gray-500 text-sm mb-3 uppercase tracking-wider">Historia konwersacji</h3>
              {chats.length === 0 && <p className="text-sm text-gray-400">Brak historii. Rozpocznij nowy czat.</p>}
              
              {chats.map(chat => (
                <button
                  key={chat.id}
                  onClick={() => setActiveChatId(chat.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors ${
                    activeChatId === chat.id ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'hover:bg-gray-50 text-gray-700 border border-transparent'
                  }`}
                >
                  <MessageSquare size={18} className={activeChatId === chat.id ? 'text-blue-600' : 'text-gray-400'} />
                  <span className="truncate font-medium">{chat.title}</span>
                </button>
              ))}
            </div>
          </div>

          {/* PRAWA KOLUMNA: Okno czatu */}
          <div className="w-2/3">
            {activeChatId ? (
              <ChatWindow key={activeChatId} chatId={activeChatId} />
            ) : (
              <div className="h-full flex flex-col items-center justify-center bg-white rounded-xl shadow-sm border border-dashed border-gray-300 text-gray-500">
                <MessageSquare size={48} className="mb-4 text-gray-300" />
                <p className="text-lg font-medium">Wybierz czat z historii lub utwórz nowy</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};