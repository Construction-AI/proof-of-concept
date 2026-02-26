import { Settings, Sparkles } from 'lucide-react';
import { useSchemaStore } from '../../store/schemaStore';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card } from '@/components/ui/card';

export const PropertyPanel = () => {
  const { nodes, selectedNodeId, updateNodeData } = useSchemaStore();
  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="w-80 bg-background border-l p-6 flex flex-col h-full overflow-y-auto shadow-sm">
      <div className="flex items-center gap-2 mb-6 pb-4 border-b">
        <Settings className="h-5 w-5 text-muted-foreground" />
        <h2 className="font-semibold">Właściwości węzła</h2>
      </div>

      {!selectedNode ? (
        <p className="text-sm text-muted-foreground italic text-center mt-10">Wybierz blok na drzewie, aby edytować jego właściwości.</p>
      ) : (
        <div className="space-y-6">
          {/* SECTION */}
          {selectedNode.type === 'section' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Tytuł sekcji</Label>
                <Input value={selectedNode.data.title} onChange={(e) => updateNodeData(selectedNode.id, { title: e.target.value })} />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="show_title" checked={selectedNode.data.show_title} onCheckedChange={(c) => updateNodeData(selectedNode.id, { show_title: !!c })} />
                <Label htmlFor="show_title" className="font-normal cursor-pointer">Pokaż tytuł w dokumencie</Label>
              </div>
              <div className="space-y-2">
                <Label>Poziom nagłówka</Label>
                <Select value={String(selectedNode.data.heading_level)} onValueChange={(v) => updateNodeData(selectedNode.id, { heading_level: Number(v) })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">H1 (Główny rozdział)</SelectItem>
                    <SelectItem value="2">H2 (Podrozdział)</SelectItem>
                    <SelectItem value="3">H3 (Sekcja)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="page_break" checked={selectedNode.data.page_before_break} onCheckedChange={(c) => updateNodeData(selectedNode.id, { page_before_break: !!c })} />
                <Label htmlFor="page_break" className="font-normal cursor-pointer">Zacznij od nowej strony</Label>
              </div>
            </div>
          )}

          {/* LIST */}
          {selectedNode.type === 'list' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Typ listy</Label>
                <Select value={selectedNode.data.list_type} onValueChange={(v) => updateNodeData(selectedNode.id, { list_type: v as 'bullet' | 'numbered' })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bullet">Punktowana</SelectItem>
                    <SelectItem value="numbered">Numerowana (1, 2, 3...)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Odstępy</Label>
                <Select value={selectedNode.data.spacing} onValueChange={(v) => updateNodeData(selectedNode.id, { spacing: v as 'compact' | 'normal' | 'relaxed' })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="compact">Kompaktowe</SelectItem>
                    <SelectItem value="normal">Normalne</SelectItem>
                    <SelectItem value="relaxed">Luźne</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {/* STATIC TEXT */}
          {selectedNode.type === 'static_text' && (
            <div className="space-y-2">
              <Label>Treść stała</Label>
              <Textarea value={selectedNode.data.text} onChange={(e) => updateNodeData(selectedNode.id, { text: e.target.value })} rows={8} placeholder="Wpisz stałą treść..." />
              <p className="text-xs text-muted-foreground mt-2">Ten tekst pojawi się w każdym dokumencie w tej formie.</p>
            </div>
          )}

          {/* RAG EXTRACTION */}
          {selectedNode.type === 'rag_extraction' && (
            <div className="space-y-4">
              <Card className="bg-purple-50/50 dark:bg-purple-950/20 border-purple-200 dark:border-purple-900 p-3 flex items-start gap-2 shadow-none">
                <Sparkles className="h-4 w-4 text-purple-600 mt-0.5 shrink-0" />
                <p className="text-xs text-purple-800 dark:text-purple-300">Blok automatycznie przeszuka dokumentację (RAG) i wygeneruje treść na podstawie promptu.</p>
              </Card>
              <div className="space-y-2">
                <Label>Prompt dla AI <span className="text-destructive">*</span></Label>
                <Textarea value={selectedNode.data.prompt} onChange={(e) => updateNodeData(selectedNode.id, { prompt: e.target.value })} rows={6} placeholder="np. Wypisz usterki z raportu..." className="focus-visible:ring-purple-500" />
              </div>
              <div className="space-y-2">
                <Label>Tekst zastępczy (Fallback)</Label>
                <Input value={selectedNode.data.fallback_text} onChange={(e) => updateNodeData(selectedNode.id, { fallback_text: e.target.value })} placeholder="Brak danych." className="focus-visible:ring-purple-500" />
                <p className="text-xs text-muted-foreground">Pojawi się, gdy AI nie znajdzie kontekstu w bazie.</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};