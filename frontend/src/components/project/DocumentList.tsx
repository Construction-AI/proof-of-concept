import { FileText, Eye, Trash2 } from 'lucide-react';
import type { Document } from '../../api/documents';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface DocumentListProps {
  documents: Document[];
  isPreviewLoading: boolean;
  onPreview: (doc: Document) => void;
  onDelete: (id: number) => void;
}

export const DocumentList = ({ documents, isPreviewLoading, onPreview, onDelete }: DocumentListProps) => {
  if (documents.length === 0) return <p className="text-muted-foreground text-sm">Brak dokumentów w projekcie.</p>;

  return (
    <div className="grid gap-3">
      {documents.map((doc) => (
        <Card key={doc.id} className="p-4 flex items-center justify-between hover:border-primary/50 transition-colors">
          <div className="flex items-center gap-4">
            <div className="bg-primary/10 p-2 rounded-md">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="font-medium">{doc.file_name}</p>
              <p className="text-xs text-muted-foreground">
                Dodano: {new Date(doc.created_at).toLocaleDateString()} • {Math.round(doc.size / 1024)} KB
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => onPreview(doc)} disabled={isPreviewLoading}>
              <Eye className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => onDelete(doc.id)} className="text-destructive hover:text-destructive hover:bg-destructive/10">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
};