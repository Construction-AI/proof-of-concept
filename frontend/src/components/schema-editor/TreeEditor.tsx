// src/components/schema-editor/TreeEditor.tsx
import { Tree, type NodeModel } from '@minoru/react-dnd-treeview';
import { PlusCircle, Loader2 } from 'lucide-react';
import { useSchemaStore, type SchemaNode } from '../../store/schemaStore';
import { SchemaTreeNode } from './SchemaTreeNode';

// 1. Definiujemy interfejs dla propsów
interface TreeEditorProps {
  isLoading: boolean;
}

// 2. Wstrzykujemy isLoading jako prop
export const TreeEditor = ({ isLoading }: TreeEditorProps) => {
  // Wyciągamy tylko to, co potrzebne do renderowania drzewa
  const { nodes, reorderNodes } = useSchemaStore();

  const treeData: NodeModel<SchemaNode>[] = nodes.map((node) => ({
    id: node.id,
    parent: node.parent_id === null ? 0 : node.parent_id,
    droppable: true,
    text: node.type === 'section' ? node.data.title : 'List Container',
    data: node,
  }));

  const handleDrop = (newTree: NodeModel<SchemaNode>[]) => {
    const updatedNodes: SchemaNode[] = newTree.map((node) => ({
      ...node.data!,
      parent_id: node.parent === 0 ? null : String(node.parent),
    }));
    reorderNodes(updatedNodes);
  };

  const handleCanDrop = (tree: NodeModel[], { dropTarget }: any) => {
    if (!dropTarget) return true;
    const targetData = dropTarget.data as SchemaNode;
    return targetData.type === 'section' || targetData.type === 'list';
  };

  return (
    <div className="flex-1 flex flex-col p-8 overflow-y-auto">
      <div className="max-w-3xl mx-auto w-full">
        {/* Usunięto cały blok z nagłówkiem i przyciskiem Zapisz */}

        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 min-h-100">
          {isLoading ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
              <Loader2 size={48} className="mb-4 text-blue-500 animate-spin" />
              <p>Wczytywanie schematu z bazy danych...</p>
            </div>
          ) : nodes.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
              <PlusCircle size={48} className="mb-4 opacity-20" />
              <p>Twój schemat jest pusty. Kliknij blok po lewej, aby zacząć.</p>
            </div>
          ) : (
            <Tree
              tree={treeData}
              rootId={0}
              initialOpen={true}
              sort={false}
              canDrop={handleCanDrop}
              onDrop={handleDrop}
              placeholderRender={(node, { depth }) => (
                <div
                  className="flex items-center z-10 py-1"
                  style={{ marginLeft: depth * 24 }}
                >
                  <div className="h-1.5 w-full bg-blue-500 rounded-full relative shadow-sm">
                    <div className="absolute -left-2 -top-1.5 w-4 h-4 rounded-full border-4 border-blue-500 bg-white" />
                  </div>
                </div>
              )}
              render={(node, { depth, isOpen, onToggle, hasChild }) => (
                <SchemaTreeNode node={node} depth={depth} isOpen={isOpen} onToggle={onToggle} hasChild={hasChild} />
              )}
              classes={{
                root: "tree-root pb-12",
                draggingSource: "opacity-40 scale-95 transition-transform",
                dropTarget: "bg-blue-50 ring-2 ring-blue-400 ring-inset rounded"
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};