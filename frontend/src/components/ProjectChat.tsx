// src/components/ProjectChat.tsx
import { useState } from 'react';
import { Send, Bot, User, AlertCircle, BookOpen } from 'lucide-react';
import { ragService } from '../api/rag';

// Definiujemy, jak wygląda pojedyncza wiadomość w naszym interfejsie
type Message = {
  id: string;
  role: 'user' | 'ai';
  text: string;
  // Pola opcjonalne (tylko dla odpowiedzi AI)
  confidence?: number;
  reasoning?: string;
  sources?: string[];
};

interface ProjectChatProps {
  projectId: number;
}

export const ProjectChat = ({ projectId }: ProjectChatProps) => {
  // REACT: Stan przechowujący listę wiadomości. Na start jest pusta.
  const [messages, setMessages] = useState<Message[]>([]);
  // REACT: Stan przechowujący to, co użytkownik aktualnie wpisuje w input
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuestion = input.trim();
    
    // 1. Dodajemy pytanie użytkownika do historii konwersacji
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text: userQuestion,
    };
    
    // Używamy tzw. funkcji aktualizującej stan (prev => ...), 
    // aby bezpiecznie dodać element do istniejącej tablicy
    setMessages((prev) => [...prev, newUserMsg]);
    setInput(''); // Czyścimy pole tekstowe
    setIsLoading(true);

    try {
      // 2. Odpytujemy backend
      const response = await ragService.askProject(projectId, userQuestion);
      
      // 3. Formatuje odpowiedź AI i dodajemy do historii
      const newAiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        text: response.structured_answer.answer,
        confidence: response.structured_answer.confidence_score,
        reasoning: response.structured_answer.reasoning,
        sources: response.sources,
      };
      
      setMessages((prev) => [...prev, newAiMsg]);
    } catch (error) {
      console.error("Błąd RAG:", error);
      // Obsługa błędu jako wiadomość systemu
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
    // TAILWIND: flex-col (układ pionowy), h-[600px] (wymuszona wysokość)
    <div className="flex flex-col h-[600px] bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mt-8">
      
      {/* Nagłówek czatu */}
      <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center gap-2">
        <Bot className="text-blue-600" />
        <h3 className="font-semibold text-gray-800">Asystent Projektu (RAG)</h3>
      </div>

      {/* Okno z wiadomościami (scrollowane) */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-50/50">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <Bot size={48} className="mb-4 opacity-50" />
            <p>Zadaj pytanie dotyczące dokumentów w tym projekcie.</p>
          </div>
        ) : (
          messages.map((msg) => (
            // TAILWIND: justify-end wypycha wiadomość użytkownika na prawą stronę
            <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              {/* Awatar AI */}
              {msg.role === 'ai' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <Bot size={18} className="text-blue-600" />
                </div>
              )}

              {/* Dymek wiadomości */}
              <div className={`max-w-[80%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' // Styl dla użytkownika
                  : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm' // Styl dla AI
              }`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
                
                {/* Meta-dane RAG (tylko dla AI) */}
                {msg.role === 'ai' && msg.confidence !== undefined && (
                  <div className="mt-4 pt-3 border-t border-gray-100 text-sm space-y-2">
                    
                    <div className="flex items-center gap-2">
                      {/* Jeśli confidence > 0.7 kolor zielony, w przeciwnym razie pomarańczowy */}
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
                            <span key={idx} className="bg-gray-100 px-2 py-0.5 rounded text-xs">
                              {source}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Awatar Użytkownika */}
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <User size={18} className="text-gray-600" />
                </div>
              )}
            </div>
          ))
        )}
        
        {/* Wskaźnik ładowania */}
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

      {/* Pole wpisywania (Formularz) */}
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
  );
};