import { useEffect, useState, useRef } from 'react';
import { Send, Loader2, Bot, User } from 'lucide-react';
import { chatsService, type Message } from '../../api/chats';

export const ChatWindow = ({ chatId }: { chatId: number }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatsService.getChatMessages(chatId).then(setMessages);
  }, [chatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: userMsg }]);
    
    setIsTyping(true);
    try {
      const aiResponse = await chatsService.sendMessage(chatId, userMsg);
      setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: aiResponse }]);
    } catch (error) {
      alert('Błąd komunikacji z AI.');
    } finally {
      setIsTyping(false);
    }
  };

  console.log("Messages:", messages)

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <p className="text-center text-gray-500 mt-10">Zadaj pytanie dotyczące dokumentacji projektu...</p>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex shrink-0 items-center justify-center text-blue-600">
                  <Bot size={18} />
                </div>
              )}
              <div className={`p-3 max-w-[75%] rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-200 flex shrink-0 items-center justify-center text-gray-600">
                  <User size={18} />
                </div>
              )}
            </div>
          ))
        )}
        {isTyping && (
          <div className="flex gap-3 items-center text-gray-500">
             <div className="w-8 h-8 rounded-full bg-blue-100 flex shrink-0 items-center justify-center text-blue-600">
               <Bot size={18} />
             </div>
             {/* Przeniesiono className="animate-spin" na element span */}
             <span className="animate-spin flex items-center justify-center">
               <Loader2 size={16} />
             </span> 
             Piszę odpowiedź...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 border-t flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Zapytaj o detale projektu..."
          className="flex-1 border p-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isTyping}
        />
        <button type="submit" disabled={!input.trim() || isTyping} className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};