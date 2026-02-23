// src/components/schema-editor/SchemaTreeNode.tsx
import { AlignLeft, LayoutList, Type, Trash2, ChevronRight, ChevronDown, Sparkles } from 'lucide-react'; // Dodano Chevrons!
import type { NodeModel } from '@minoru/react-dnd-treeview';
import { useSchemaStore, type SchemaNode } from '../../store/schemaStore';

type Props = {
  node: NodeModel<SchemaNode>;
  depth: number;
  isOpen: boolean;
  onToggle: (id: string | number) => void;
  hasChild: boolean; // Nowy props z Kroku 1
};

export const SchemaTreeNode = ({ node, depth, isOpen, onToggle, hasChild }: Props) => {
  const { selectedNodeId, selectNode, removeNode } = useSchemaStore();
  const isSelected = node.id === selectedNodeId;

  const data = node.data as SchemaNode;

  return (
    <div
      className={`flex items-center justify-between p-2 mb-1 rounded cursor-pointer border transition-colors ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:bg-gray-50'
        }`}
      style={{ marginLeft: depth * 24 }}
      onClick={() => selectNode(String(node.id))}
    >
      <div className="flex items-center gap-2">

        {/* STRZAŁKA ZWIJANIA / ROZWIJANIA */}
        <div
          onClick={(e) => {
            e.stopPropagation(); // Blokuje kliknięcie przed zaznaczeniem całego klocka
            if (hasChild) {
              onToggle(node.id);
            }
          }}
          // Jeśli klocek ma dzieci, pokazujemy strzałkę. Jeśli nie - dajemy pustą przezroczystą ramkę, by wyrównanie ikon zostało nienaruszone.
          className={`p-1 rounded hover:bg-gray-200 text-gray-500 transition-colors ${hasChild ? 'visible cursor-pointer' : 'invisible'
            }`}
        >
          {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </div>

        {/* Ikona Typu Klocka */}
        {data.type === 'section' && <LayoutList size={16} className="text-blue-500" />}
        {data.type === 'list' && <Type size={16} className="text-green-500" />}
        {data.type === 'static_text' && <AlignLeft size={16} className="text-gray-500" />}
        {data.type === 'rag_extraction' && <Sparkles size={16} className="text-purple-500" />}
        
        <span className="font-medium text-sm text-gray-800">
          {data.type === 'static_text' 
            ? (data.data.text.length > 25 ? data.data.text.substring(0, 25) + '...' : data.data.text || 'Pusty tekst')
            : data.type === 'rag_extraction'
            ? (data.data.prompt.length > 25 ? data.data.prompt.substring(0, 25) + '...' : data.data.prompt || 'Pusty prompt')
            : node.text}
        </span>
      </div>

      {/* Przycisk Usuwania */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          removeNode(String(node.id));
        }}
        className="text-gray-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors"
        title="Usuń blok"
      >
        <Trash2 size={16} />
      </button>
    </div>
  );
};