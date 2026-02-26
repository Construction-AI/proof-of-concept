import { Check, Loader2, FileDown, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface TemplateHeaderProps {
  templates: any[]; 
  selectedTemplateId: number | null;
  onSelectTemplate: (id: number) => void;
  onGenerate: () => void;
  onCreate: () => void;
  onDelete: () => void;
  isSaving: boolean;
  saveSuccess: boolean;
  isGenerating: boolean;
  isSchemaEmpty: boolean;
}

export const TemplateHeader = ({
  templates, selectedTemplateId, onSelectTemplate, 
  onGenerate, onCreate, onDelete, 
  isSaving, saveSuccess, isGenerating, isSchemaEmpty
}: TemplateHeaderProps) => {

  return (
    <div className="bg-background border-b px-6 py-3 flex items-center justify-between z-10 shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-bold">Edytor Raportu</h1>
        <div className="h-6 w-px bg-border mx-2"></div>
        
        <div className="flex items-center gap-2">
          <Select 
            value={selectedTemplateId ? String(selectedTemplateId) : undefined} 
            onValueChange={(v) => onSelectTemplate(Number(v))}
          >
            <SelectTrigger className="w-[280px]">
              <SelectValue placeholder="Wybierz szablon z biblioteki..." />
            </SelectTrigger>
            <SelectContent>
              {templates.map(t => (
                <SelectItem key={t.id} value={String(t.id)}>{t.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button variant="outline" size="icon" onClick={onCreate} title="Utwórz nowy szablon">
            <Plus className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={onDelete} disabled={!selectedTemplateId} className="hover:text-destructive hover:bg-destructive/10" title="Usuń szablon">
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-xs text-muted-foreground w-24 flex justify-end">
           {isSaving ? (
             <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin"/> Zapisywanie</span>
           ) : saveSuccess ? (
             <span className="flex items-center gap-1 text-green-600"><Check className="h-3 w-3"/> Zapisano</span>
           ) : null}
        </div>
        <Button onClick={onGenerate} disabled={isGenerating || isSchemaEmpty || !selectedTemplateId}>
          {isGenerating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileDown className="mr-2 h-4 w-4" />}
          Generuj PDF
        </Button>
      </div>
    </div>
  );
};