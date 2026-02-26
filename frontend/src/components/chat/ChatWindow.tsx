import { useEffect, useState, useRef } from 'react';
import { Send, Loader2, Bot, User } from 'lucide-react';
import { chatsService, type Message } from '../../api/chats';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

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
    if (!input.trim() || isTyping) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: userMsg }]);
    
    setIsTyping(true);
    try {
      const aiResponse = await chatsService.sendMessage(chatId, userMsg);
      setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: aiResponse }]);
    } catch {
      alert('Błąd komunikacji z AI.');
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <Card className="flex flex-col h-full border shadow-sm">
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4 pb-4">
          {messages.length === 0 && (
            <p className="text-center text-muted-foreground mt-10">Zadaj pytanie dotyczące dokumentacji...</p>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
              )}
              <div className={`p-3 max-w-[75%] rounded-lg text-sm ${
                msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-br-sm' : 'bg-muted rounded-bl-sm'
              }`}>
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                  <User className="h-4 w-4 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="flex gap-3 items-center text-muted-foreground text-sm">
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <Loader2 className="h-4 w-4 animate-spin" /> Piszę odpowiedź...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="p-4 border-t bg-background">
        <form onSubmit={handleSend} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Zapytaj asystenta..."
            disabled={isTyping}
            className="flex-1"
          />
          <Button type="submit" disabled={!input.trim() || isTyping} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </Card>
  );
};