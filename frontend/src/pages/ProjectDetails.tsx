import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsService, type Document } from '../api/documents';
import { chatsService, type Chat } from '../api/chats';
import { UploadZone } from '../components/project/UploadZone';
import { DocumentList } from '../components/project/DocumentList';
import { ChatWindow } from '../components/chat/ChatWindow';
import { ArrowLeft, MessageSquare, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const projectId = Number(id);

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<number | null>(null);

  useEffect(() => {
    if (projectId) {
      fetchDocuments();
      chatsService.getProjectChats(projectId).then(setChats);
    }
  }, [projectId]);

  const fetchDocuments = async () => {
    try {
      const allDocs = await documentsService.getAll();
      setDocuments(allDocs.filter(doc => doc.project.id === projectId));
    } catch (error) {
      console.error("Błąd pobierania plików:", error);
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
      alert("Nie udało się wgrać pliku.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!window.confirm("Usunąć ten plik z bazy wektorowej Qdrant?")) return;
    try {
      await documentsService.delete(docId);
      fetchDocuments();
    } catch (error) {
      console.error("Błąd usuwania:", error);
    }
  };

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
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <Button variant="ghost" onClick={() => navigate(`/dashboard`)} className="pl-0 hover:bg-transparent">
          <ArrowLeft className="mr-2 h-4 w-4" /> Powrót do panelu
        </Button>

        <Tabs defaultValue="documents" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="documents">Baza Wiedzy</TabsTrigger>
            <TabsTrigger value="chat">Asystent RAG</TabsTrigger>
          </TabsList>

          <TabsContent value="documents" className="mt-6 space-y-6">
            <UploadZone isUploading={isUploading} onFileSelect={handleFileSelect} />
            <DocumentList documents={documents} isPreviewLoading={false} onPreview={() => {}} onDelete={handleDelete} />
          </TabsContent>

          <TabsContent value="chat" className="mt-6 h-[700px] flex gap-6">
            {/* Lista Czatów */}
            <Card className="w-1/3 flex flex-col">
              <CardHeader className="p-4 border-b">
                <Button onClick={handleCreateChat} className="w-full">
                  <Plus className="mr-2 h-4 w-4" /> Nowy czat
                </Button>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-4 space-y-2">
                {chats.map(chat => (
                  <Button
                    key={chat.id}
                    variant={activeChatId === chat.id ? "secondary" : "ghost"}
                    className="w-full justify-start font-normal"
                    onClick={() => setActiveChatId(chat.id)}
                  >
                    <MessageSquare className="mr-2 h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{chat.title}</span>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* Okno Czatu */}
            <div className="w-2/3">
              {activeChatId ? (
                <ChatWindow chatId={activeChatId} />
              ) : (
                <Card className="h-full flex flex-col items-center justify-center border-dashed text-muted-foreground">
                  <MessageSquare className="h-12 w-12 mb-4 opacity-50" />
                  <p>Wybierz czat z historii lub utwórz nowy</p>
                </Card>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};