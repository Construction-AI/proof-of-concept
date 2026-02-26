import { useEffect, useState } from 'react';
import { FileText, FolderPlus } from 'lucide-react';
import { templatesService } from '../../api/templates';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface Props {
  onAssignToLibrary: (id: number) => void;
}

export const TemplateList = ({ onAssignToLibrary }: Props) => {
  const [templates, setTemplates] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    templatesService.getAll().then(setTemplates).catch(console.error);
  }, []);

  return (
    <Card className="h-full border-0 shadow-none sm:border sm:shadow-sm">
      <CardHeader className="px-0 sm:px-6">
        <CardTitle>Moje Szablony</CardTitle>
      </CardHeader>
      <CardContent className="px-0 sm:px-6">
        <div className="flex flex-col gap-2">
          {templates.length === 0 && <p className="text-sm text-muted-foreground">Brak utworzonych szablonów.</p>}
          {templates.map(t => (
            <div 
              key={t.id} 
              onClick={() => navigate(`/templates-editor?templateId=${t.id}`)} 
              className="flex items-center justify-between p-3 rounded-md border bg-card hover:bg-accent cursor-pointer transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                <span className="font-medium">{t.name}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onAssignToLibrary(t.id);
                }}
                className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity h-8"
              >
                <FolderPlus className="h-4 w-4 sm:mr-2" /> 
                <span className="hidden sm:inline">Do biblioteki</span>
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};