import { useEffect, useState } from 'react';
import { Loader2, Plus } from 'lucide-react';
import { librariesService, type TemplateLibrary } from '../../api/libraries';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Props {
  templateId: number;
  onClose: () => void;
}

export const LibraryAssignModal = ({ templateId, onClose }: Props) => {
  const [libraries, setLibraries] = useState<TemplateLibrary[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<number | null>(null);

  useEffect(() => {
    librariesService.getAll().then(data => {
      setLibraries(data.filter((lib: any) => !lib.is_global));
      setLoading(false);
    });
  }, []);

  const handleAssign = async (libraryId: number) => {
    setProcessingId(libraryId);
    try {
      await librariesService.addTemplate(libraryId, templateId);
      alert('Przypisano!');
    } catch (e) {
      alert('Błąd przypisywania.');
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Przypisz do biblioteki</DialogTitle>
        </DialogHeader>
        
        {loading ? <Loader2 className="animate-spin mx-auto my-8 text-primary h-6 w-6" /> : (
          <ScrollArea className="max-h-64 mt-4">
            <div className="space-y-2">
              {libraries.length === 0 && <p className="text-muted-foreground text-sm text-center">Brak własnych bibliotek.</p>}
              {libraries.map(lib => (
                <div key={lib.id} className="flex justify-between items-center p-3 border rounded-md hover:bg-accent transition-colors">
                  <span className="font-medium text-sm">{lib.name}</span>
                  <Button 
                    variant="secondary"
                    size="icon"
                    onClick={() => handleAssign(lib.id)}
                    disabled={processingId === lib.id}
                  >
                    {processingId === lib.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </DialogContent>
    </Dialog>
  );
};