import { useState } from 'react';
import { Send, Bot, User, AlertCircle, BookOpen, X, FileText } from 'lucide-react'; // Dodano X i FileText
import { ragService, type Source } from '../api/rag';

type Message = {
  id: string;
  role: 'user' | 'ai';
  text: string;
  confidence?: number;
  reasoning?: string;
  sources?: Source[];
};

interface ProjectChatProps {
  projectId: number;
}

export const ProjectChat = ({ projectId }: ProjectChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSource, setSelectedSource] = useState<Source | null>(null);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuestion = input.trim();
    
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: userQuestion,
    };
    
    setMessages((prev) => [...prev, newUserMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await ragService.askProject(projectId, userQuestion);
      
      const newAiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        text: response.answer,
        confidence: response.llm_confidence,
        reasoning: response.reasoning,
        sources: response.sources,
      };
      
      setMessages((prev) => [...prev, newAiMsg]);
    } catch (error) {
      console.error("Błąd RAG:", error);
      setMessages((prev) => [...prev, {
        id: Date.now().toString(),
        role: 'ai',
        text: 'Wystąpił błąd podczas komunikacji z bazą wiedzy. Spróbuj ponownie.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="flex flex-col h-[600px] bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mt-8 relative">
        <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center gap-2">
          <Bot className="text-blue-600" />
          <h3 className="font-semibold text-gray-800">Asystent Projektu (RAG)</h3>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50/50">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400">
              <Bot size={48} className="mb-4 opacity-50" />
              <p>Zadaj pytanie dotyczące dokumentów w tym projekcie.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'ai' && (
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Bot size={18} className="text-blue-600" />
                  </div>
                )}

                <div className={`max-w-[80%] rounded-2xl p-4 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-tr-sm' 
                    : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm' 
                }`}>
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                  
                  {msg.role === 'ai' && msg.confidence !== undefined && (
                    <div className="mt-4 pt-3 border-t border-gray-100 text-sm space-y-2">
                      <div className="flex items-center gap-2">
                        <AlertCircle size={14} className={msg.confidence > 0.7 ? "text-green-500" : "text-amber-500"} />
                        <span className="text-gray-500 font-medium">
                          Pewność odpowiedzi: <span className={msg.confidence > 0.7 ? "text-green-600" : "text-amber-600"}>
                            {Math.round(msg.confidence * 100)}%
                          </span>
                        </span>
                      </div>

                      {msg.reasoning && (
                        <p className="text-gray-500 italic text-xs border-l-2 border-gray-200 pl-2">
                          {msg.reasoning}
                        </p>
                      )}

                      {msg.sources && msg.sources.length > 0 && (
                        <div className="flex items-start gap-2 text-gray-500 mt-2">
                          <BookOpen size={14} className="mt-0.5" />
                          <div className="flex flex-wrap gap-1">
                            {msg.sources.map((source, idx) => (
                              // ZAMIANA NA KLIKALNY PRZYCISK
                              <button 
                                key={idx} 
                                onClick={() => setSelectedSource(source)}
                                className="bg-gray-100 hover:bg-blue-100 hover:text-blue-700 px-2 py-0.5 rounded text-xs cursor-pointer transition-colors border border-transparent hover:border-blue-200 text-left"
                              >
                                {source.source}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <User size={18} className="text-gray-600" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-4 justify-start">
               <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <Bot size={18} className="text-blue-600" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm p-4 text-gray-500 flex items-center gap-2 shadow-sm">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-gray-200 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Zapytaj o detale z dokumentacji..."
            disabled={isLoading}
            className="flex-1 bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors flex items-center justify-center w-12"
          >
            <Send size={20} />
          </button>
        </form>
      </div>

      {/* --- POPUP (MODAL) ZE ŹRÓDŁEM --- */}
      {selectedSource && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          
          {/* Główny kontener popupa */}
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col animate-in fade-in zoom-in duration-200">
            
            {/* Nagłówek popupa */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <FileText className="text-blue-600" size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{selectedSource.source}</h3>
                  <p className="text-xs text-gray-500">Kontekst znaleziony w wektorowej bazie danych</p>
                </div>
              </div>
              
              <button 
                onClick={() => setSelectedSource(null)}
                className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Ciało popupa ze scrollowanym kontekstem */}
            <div className="p-6 overflow-y-auto bg-gray-50">
              <div className="bg-white border border-gray-200 rounded-lg p-4 font-mono text-sm text-gray-700 whitespace-pre-wrap leading-relaxed shadow-inner">
                {selectedSource.context_window}
              </div>
            </div>
            
            {/* Stopka popupa */}
            <div className="p-4 border-t border-gray-200 flex justify-end">
               <button 
                onClick={() => setSelectedSource(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md transition-colors text-sm font-medium"
              >
                Zamknij
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
};