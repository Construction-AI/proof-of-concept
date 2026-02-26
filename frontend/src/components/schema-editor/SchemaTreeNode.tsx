import { AlignLeft, LayoutList, Type, Trash2, ChevronRight, ChevronDown, Sparkles } from 'lucide-react';
import type { NodeModel } from '@minoru/react-dnd-treeview';
import { useSchemaStore, type SchemaNode } from '../../store/schemaStore';
import { Button } from '@/components/ui/button';

type Props = {
  node: NodeModel<SchemaNode>;
  depth: number;
  isOpen: boolean;
  onToggle: (id: string | number) => void;
  hasChild: boolean;
};

export const SchemaTreeNode = ({ node, depth, isOpen, onToggle, hasChild }: Props) => {
  const { selectedNodeId, selectNode, removeNode } = useSchemaStore();
  const isSelected = node.id === selectedNodeId;
  const data = node.data as SchemaNode;

  return (
    <div
      className={`flex items-center justify-between py-2 px-3 my-1 rounded-md cursor-grab active:cursor-grabbing border bg-card transition-all ${
        isSelected ? 'border-primary ring-1 ring-primary/20 shadow-sm' : 'hover:border-primary/50'
      }`}
      style={{ marginLeft: depth * 24 }}
      onClick={() => selectNode(String(node.id))}
    >
      <div className="flex items-center gap-2">
        <div
          onClick={(e) => {
            e.stopPropagation();
            if (hasChild) onToggle(node.id);
          }}
          className={`p-1 rounded-sm hover:bg-accent text-muted-foreground transition-colors ${hasChild ? 'cursor-pointer' : 'invisible'}`}
        >
          {isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>

        {data.type === 'section' && <LayoutList size={16} className="text-blue-500" />}
        {data.type === 'list' && <Type size={16} className="text-green-500" />}
        {data.type === 'static_text' && <AlignLeft size={16} className="text-gray-500" />}
        {data.type === 'rag_extraction' && <Sparkles size={16} className="text-purple-500" />}

        <span className="font-medium text-sm">
          {data.type === 'static_text'
            ? (data.data.text.length > 30 ? data.data.text.substring(0, 30) + '...' : data.data.text || 'Pusty tekst')
            : data.type === 'rag_extraction'
              ? (data.data.prompt.length > 30 ? data.data.prompt.substring(0, 30) + '...' : data.data.prompt || 'Pusty prompt')
              : node.text}
        </span>
      </div>

      <Button
        variant="ghost"
        size="icon"
        className="h-7 w-7 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
        onClick={(e) => {
          e.stopPropagation();
          removeNode(String(node.id));
        }}
      >
        <Trash2 size={14} />
      </Button>
    </div>
  );
};