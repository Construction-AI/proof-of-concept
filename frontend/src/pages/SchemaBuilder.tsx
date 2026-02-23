import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { BlockPalette } from '../components/schema-editor/BlockPalette';
import { TreeEditor } from '../components/schema-editor/TreeEditor';
import { PropertyPanel } from '../components/schema-editor/PropertyPanel';

export const SchemaBuilder = () => {
  return (
    <DndProvider backend={HTML5Backend}>
      {/* Główny kontener o wysokości okna */}
      <div className="flex h-screen bg-gray-100 overflow-hidden">
        
        <BlockPalette />
        <TreeEditor />
        <PropertyPanel />
        
      </div>
    </DndProvider>
  );
};