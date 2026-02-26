import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, Copy, Edit, Loader2, ArrowLeft } from 'lucide-react';
import { librariesService } from '../api/libraries';
import { templatesService } from '../api/templates';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const LibraryTemplates = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [copyingId, setCopyingId] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      librariesService.getTemplates(Number(id))
        .then(setTemplates)
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleCopy = async (templateId: number) => {
    setCopyingId(templateId);
    try {
      await templatesService.copyTemplate(templateId);
      alert("Skopiowano do Twoich szablonów!");
    } catch (e) {
      alert("Błąd kopiowania.");
    } finally {
      setCopyingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/library')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-2xl font-bold">Zawartość biblioteki</h1>
        </div>

        {loading ? (
          <Loader2 className="animate-spin mx-auto mt-12 h-8 w-8 text-emerald-500" />
        ) : templates.length === 0 ? (
          <p className="text-center text-muted-foreground py-12">Ta biblioteka nie posiada jeszcze szablonów.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map(t => (
              <Card key={t.id} className="flex flex-col justify-between">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="bg-emerald-50 dark:bg-emerald-950/30 p-2 rounded-md">
                      <FileText className="h-6 w-6 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <CardTitle className="text-lg">{t.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-2 mt-auto">
                  <Button variant="outline" onClick={() => navigate(`/templates-editor?templateId=${t.id}`)}>
                    <Edit className="mr-2 h-4 w-4" /> Edytuj
                  </Button>
                  <Button 
                    variant="secondary"
                    className="bg-blue-50 text-blue-600 hover:bg-blue-100 dark:bg-blue-950/30 dark:text-blue-400"
                    onClick={() => handleCopy(t.id)} 
                    disabled={copyingId === t.id}
                  >
                    {copyingId === t.id ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Copy className="mr-2 h-4 w-4" />} 
                    Kopiuj
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};