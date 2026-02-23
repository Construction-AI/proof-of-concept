import { Tree, type NodeModel } from '@minoru/react-dnd-treeview';
import { PlusCircle } from 'lucide-react';
import { useSchemaStore, type SchemaNode } from '../../store/schemaStore';
import { SchemaTreeNode } from './SchemaTreeNode';

export const TreeEditor = () => {
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

  return (
    <div className="flex-1 flex flex-col p-8 overflow-y-auto">
      <div className="max-w-3xl mx-auto w-full">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Document Schema Editor</h1>
          <p className="text-gray-500">Add blocks, drag them to reorder, or nest them inside each other.</p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 min-h-[400px]">
          {nodes.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-400 py-20">
              <PlusCircle size={48} className="mb-4 opacity-20" />
              <p>Your schema is empty. Click a block on the left to start.</p>
            </div>
          ) : (
            <Tree
              tree={treeData}
              rootId={0}
              // DODAŁEM `initialOpen={true}`, żeby drzewo było domyślnie rozwinięte
              initialOpen={true}
              // DODAŁEM `hasChild` do argumentów wyciąganych z biblioteki
              render={(node, { depth, isOpen, onToggle, hasChild }) => (
                <SchemaTreeNode
                  node={node}
                  depth={depth}
                  isOpen={isOpen}
                  onToggle={onToggle}
                  hasChild={hasChild} // <--- Przekazujemy to do naszego komponentu
                />
              )}
              onDrop={handleDrop}
              classes={{
                root: "tree-root pb-4",
                draggingSource: "opacity-50",
                dropTarget: "bg-blue-50 border-blue-500 border-dashed"
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};