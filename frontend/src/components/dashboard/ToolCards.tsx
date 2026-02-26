import { useNavigate } from 'react-router-dom';
import { LayoutTemplate, Library as LibraryIcon } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

export const ToolCards = () => {
  const navigate = useNavigate();
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <Card 
        className="cursor-pointer hover:border-primary hover:bg-accent/50 transition-all group"
        onClick={() => navigate('/templates-editor')}
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LayoutTemplate className="h-5 w-5 text-primary" />
            Kreator Szablonów
          </CardTitle>
          <CardDescription>Zbuduj strukturę dokumentów dla AI.</CardDescription>
        </CardHeader>
      </Card>
      
      <Card 
        className="cursor-pointer hover:border-emerald-500 hover:bg-emerald-50/50 dark:hover:bg-emerald-950/20 transition-all group"
        onClick={() => navigate('/library')}
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LibraryIcon className="h-5 w-5 text-emerald-600" />
            Biblioteka Szablonów
          </CardTitle>
          <CardDescription>Przeglądaj i kopiuj gotowe szablony dla branż.</CardDescription>
        </CardHeader>
      </Card>
    </div>
  );
};