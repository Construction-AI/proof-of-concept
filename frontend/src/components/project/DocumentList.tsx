import { FileText, Eye, Trash2, AlertTriangle, RefreshCw, Upload } from 'lucide-react';
import type { Document, DocumentValidation } from '../../api/documents';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface DocumentListProps {
  documents: Document[];
  validations: Record<number, DocumentValidation>;
  isPreviewLoading: boolean;
  onPreview: (doc: Document) => void;
  onDelete: (id: number) => void;
  onReindex: (id: number) => void;
  onReupload: (id: number, file: File) => void;
}

export const DocumentList = ({ documents, validations, isPreviewLoading, onPreview, onDelete, onReindex, onReupload }: DocumentListProps) => {
  if (documents.length === 0) return <p className="text-muted-foreground text-sm">Brak dokumentów w projekcie.</p>;

  return (
    <div className="grid gap-3">
      {documents.map((doc) => {
        const validation = validations[doc.id];
        
        return (
          <Card key={doc.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-primary/50 transition-colors">
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

            <div className="flex items-center gap-4 flex-wrap">
              {/* Obsługa błędów walidacji */}
              {validation && !validation.file_storage && (
                <div className="flex items-center gap-2 text-destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="text-xs font-medium">Brak pliku na dysku</span>
                  <label className="cursor-pointer">
                    <div className="flex items-center gap-1 bg-destructive/10 hover:bg-destructive/20 text-destructive px-2 py-1 rounded text-xs transition-colors">
                      <Upload className="h-3 w-3" /> Wgraj ponownie
                    </div>
                    <input type="file" className="hidden" accept=".pdf,.txt,.docx" onChange={(e) => {
                      if (e.target.files?.[0]) onReupload(doc.id, e.target.files[0]);
                    }} />
                  </label>
                </div>
              )}

              {validation && validation.file_storage && !validation.vector_store && (
                <div className="flex items-center gap-2 text-orange-500">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="text-xs font-medium">Brak w Qdrant</span>
                  <Button variant="outline" size="sm" className="h-7 text-xs border-orange-500 text-orange-500 hover:bg-orange-50" onClick={() => onReindex(doc.id)}>
                    <RefreshCw className="mr-1 h-3 w-3" /> Reindeksuj
                  </Button>
                </div>
              )}

              {/* Standardowe akcje */}
              <div className="flex items-center gap-2 ml-auto">
                <Button variant="ghost" size="icon" onClick={() => onPreview(doc)} disabled={isPreviewLoading || (!validation?.file_storage)}>
                  <Eye className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => onDelete(doc.id)} className="text-destructive hover:text-destructive hover:bg-destructive/10">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};