import { useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface UploadZoneProps {
  isUploading: boolean;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const UploadZone = ({ isUploading, onFileSelect }: UploadZoneProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFileSelect(e);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <Card className="p-10 border-2 border-dashed flex flex-col items-center justify-center text-center bg-muted/10 hover:bg-muted/30 transition-colors">
      <UploadCloud className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">Zasil bazę wiedzy RAG</h3>
      <p className="text-sm text-muted-foreground mb-6">
        Wgraj dokumenty (PDF, DOCX), które posłużą jako kontekst dla tego projektu.
      </p>
      <input type="file" ref={fileInputRef} onChange={handleChange} className="hidden" accept=".pdf,.txt,.docx" />
      <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
        {isUploading ? "Indeksowanie w Qdrant..." : "Wybierz plik z dysku"}
      </Button>
    </Card>
  );
};