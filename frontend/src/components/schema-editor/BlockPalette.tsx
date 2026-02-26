import { AlignLeft, LayoutList, Sparkles, Type } from 'lucide-react';
import { useSchemaStore } from '../../store/schemaStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

export const BlockPalette = () => {
  const addNode = useSchemaStore((state) => state.addNode);

  return (
    <div className="w-64 bg-background border-r p-4 flex flex-col h-full overflow-y-auto">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">Bloki struktury</h2>
      <div className="space-y-2">
        <Card className="p-1 hover:border-primary/50 transition-colors cursor-pointer group" onClick={() => addNode('section', null)}>
          <Button variant="ghost" className="w-full justify-start h-auto p-2">
            <LayoutList className="mr-3 h-5 w-5 text-blue-500" />
            <div className="text-left">
              <p className="font-medium text-sm">Sekcja</p>
              <p className="text-xs text-muted-foreground font-normal">Grupuj elementy</p>
            </div>
          </Button>
        </Card>

        <Card className="p-1 hover:border-primary/50 transition-colors cursor-pointer group" onClick={() => addNode("static_text", null)}>
          <Button variant="ghost" className="w-full justify-start h-auto p-2">
            <AlignLeft className="mr-3 h-5 w-5 text-gray-500" />
            <div className="text-left">
              <p className="font-medium text-sm">Stały tekst</p>
              <p className="text-xs text-muted-foreground font-normal">Niezmienny akapit</p>
            </div>
          </Button>
        </Card>

        <Card className="p-1 hover:border-purple-500/50 transition-colors cursor-pointer group bg-purple-50/30 dark:bg-purple-950/20" onClick={() => addNode('rag_extraction', null)}>
          <Button variant="ghost" className="w-full justify-start h-auto p-2 hover:bg-transparent">
            <div className="p-1.5 bg-purple-100 dark:bg-purple-900 rounded-md mr-3">
              <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="text-left">
              <p className="font-medium text-sm">Ekstrakcja RAG</p>
              <p className="text-xs text-muted-foreground font-normal">Treść od AI</p>
            </div>
          </Button>
        </Card>

        <Card className="p-1 hover:border-primary/50 transition-colors cursor-pointer group" onClick={() => addNode('list', null)}>
          <Button variant="ghost" className="w-full justify-start h-auto p-2">
            <Type className="mr-3 h-5 w-5 text-green-500" />
            <div className="text-left">
              <p className="font-medium text-sm">Lista</p>
              <p className="text-xs text-muted-foreground font-normal">Punktowana / Numerowana</p>
            </div>
          </Button>
        </Card>
      </div>
    </div>
  );
};