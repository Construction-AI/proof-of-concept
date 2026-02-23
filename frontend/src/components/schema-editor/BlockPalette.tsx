import { AlignLeft, LayoutList, Type } from 'lucide-react';
import { useSchemaStore } from '../../store/schemaStore';

export const BlockPalette = () => {
  const addNode = useSchemaStore((state) => state.addNode);

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4 flex flex-col overflow-y-auto">
      <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Blocks</h2>
      <div className="space-y-2">
        <button 
          onClick={() => addNode('section', null)}
          className="w-full flex items-center gap-3 p-3 text-left border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <LayoutList className="text-blue-500" size={20} />
          <div>
            <p className="font-medium text-gray-900 text-sm">Section</p>
            <p className="text-xs text-gray-500">Group items together</p>
          </div>
        </button>

        <button
          onClick={() => addNode("static-text", null)}
          className='w-full flex items-center gap-3 p-3 text-left border border-gray-200 rounded-lg hover:border-gray-500 hover:bg-gray-50 transition-colors'
        >
          <AlignLeft className="text-gray-500 size={20}" />
          <div>
            <p className="font-medium text-gray-900 text-sm">Static Text</p>
            <p className="text-xs text-gray-500">Fixed Paragraph</p>
          </div>
        </button>

        <button 
          onClick={() => addNode('list', null)}
          className="w-full flex items-center gap-3 p-3 text-left border border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors"
        >
          <Type className="text-green-500" size={20} />
          <div>
            <p className="font-medium text-gray-900 text-sm">List</p>
            <p className="text-xs text-gray-500">Bullet or numbered</p>
          </div>
        </button>
      </div>
    </div>
  );
};