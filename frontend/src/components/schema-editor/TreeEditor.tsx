// src/components/schema-editor/TreeEditor.tsx
import { useState } from 'react';
import { Tree, type NodeModel } from '@minoru/react-dnd-treeview';
import { PlusCircle, Save, Check } from 'lucide-react';
import { useSchemaStore, type SchemaNode } from '../../store/schemaStore';
import { SchemaTreeNode } from './SchemaTreeNode';
import { templatesService } from '../../api/templates';

export const TreeEditor = () => {
  const { nodes, reorderNodes } = useSchemaStore();
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const treeData: NodeModel<SchemaNode>[] = nodes.map((node) => ({
    id: node.id,
    parent: node.parent_id === null ? 0 : node.parent_id,
    // Zmieniamy: Tylko sekcje i listy mogą być "folderami" przyjmującymi inne klocki!
    droppable: node.type === 'section' || node.type === 'list',
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

  // --- NOWOŚĆ 1: Reguły upuszczania ---
  // Upewniamy się, że nie można wrzucić niczego DO ŚRODKA klocków tekstowych/RAG
  const handleCanDrop = (tree: NodeModel[], { dropTarget }: any) => {
    if (!dropTarget) return true; // Można upuszczać na najwyższym poziomie (root)
    const targetData = dropTarget.data as SchemaNode;
    // Zezwalamy na upuszczanie DO ŚRODKA tylko dla kontenerów
    return targetData.type === 'section' || targetData.type === 'list';
  };

  const handleSaveSchema = async () => {
    /* ... (twój dotychczasowy kod zapisu) ... */
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      await templatesService.saveNodes(1, nodes);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      console.error("Błąd zapisu schematu:", error);
      alert("Nie udało się zapisać schematu w bazie. Sprawdź konsolę.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col p-8 overflow-y-auto">
      <div className="max-w-3xl mx-auto w-full">
        
        {/* ... (Nagłówek i przycisk zapisu bez zmian) ... */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Document Schema Editor</h1>
            <p className="text-gray-500">Dodawaj klocki, przeciągaj i konfiguruj układ.</p>
          </div>
          <button
            onClick={handleSaveSchema}
            disabled={isSaving || nodes.length === 0}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-medium text-white transition-all ${
              saveSuccess ? 'bg-green-500' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSaving ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : saveSuccess ? <><Check size={20} /> Zapisano!</> : <><Save size={20} /> Zapisz Schemat</>}
          </button>
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
              initialOpen={true}
              sort={false}
              canDrop={handleCanDrop} // Podpinamy reguły
              onDrop={handleDrop}
              // --- NOWOŚĆ 2: Wyraźny wskaźnik upuszczania (Placeholder) ---
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
                root: "tree-root pb-12", // Więcej miejsca na dole, by łatwo upuścić na koniec
                draggingSource: "opacity-40 scale-95 transition-transform", // Lepszy efekt brania klocka
                dropTarget: "bg-blue-50 ring-2 ring-blue-400 ring-inset rounded" // Lepszy efekt najechania na folder
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};