import { Settings, Sparkles } from 'lucide-react';
import { useSchemaStore } from '../../store/schemaStore';

export const PropertyPanel = () => {
  const { nodes, selectedNodeId, updateNodeData } = useSchemaStore();
  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="w-80 bg-white border-l border-gray-200 p-6 overflow-y-auto shadow-xl z-10 flex flex-col">
      <div className="flex items-center gap-2 mb-6 border-b border-gray-100 pb-4">
        <Settings className="text-gray-400" size={20} />
        <h2 className="font-semibold text-gray-800">Node Properties</h2>
      </div>

      {!selectedNode ? (
        <p className="text-sm text-gray-500 italic">Select a node in the tree to edit its properties.</p>
      ) : (
        <div className="space-y-6">

          {/* Properties for SECTION */}
          {selectedNode.type === 'section' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Section Title</label>
                <input
                  type="text"
                  value={selectedNode.data.title}
                  onChange={(e) => updateNodeData(selectedNode.id, { title: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedNode.data.show_title}
                  onChange={(e) => updateNodeData(selectedNode.id, { show_title: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Show Title in Document</span>
              </label>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Heading Level</label>
                <select
                  value={selectedNode.data.heading_level}
                  onChange={(e) => updateNodeData(selectedNode.id, { heading_level: Number(e.target.value) })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value={1}>H1 (Main Chapter)</option>
                  <option value={2}>H2 (Sub-chapter)</option>
                  <option value={3}>H3 (Section)</option>
                </select>
              </div>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedNode.data.page_before_break}
                  onChange={(e) => updateNodeData(selectedNode.id, { page_before_break: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Page Break Before</span>
              </label>
            </>
          )}

          {/* Properties for LIST */}
          {selectedNode.type === 'list' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">List Type</label>
                <select
                  value={selectedNode.data.list_type}
                  onChange={(e) => updateNodeData(selectedNode.id, { list_type: e.target.value as 'bullet' | 'numbered' })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 text-sm"
                >
                  <option value="bullet">Bullet Points</option>
                  <option value="numbered">Numbered (1, 2, 3...)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Spacing</label>
                <select
                  value={selectedNode.data.spacing}
                  onChange={(e) => updateNodeData(selectedNode.id, { spacing: e.target.value as 'compact' | 'normal' | 'relaxed' })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 text-sm"
                >
                  <option value="compact">Compact</option>
                  <option value="normal">Normal</option>
                  <option value="relaxed">Relaxed</option>
                </select>
              </div>
            </>
          )}
          {/* Properties for STATIC TEXT */}
          {selectedNode.type === 'static_text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Text Content</label>
              <textarea
                value={selectedNode.data.text}
                onChange={(e) => updateNodeData(selectedNode.id, { text: e.target.value })}
                rows={6}
                className="w-full p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 text-sm resize-y"
                placeholder="Wpisz treść akapitu..."
              />
              <p className="text-xs text-gray-500 mt-2">
                Ten tekst pojawi się w każdym wygenerowanym dokumencie dokładnie w takiej formie.
              </p>
            </div>
          )}
          {/* Properties for RAG EXTRACTION */}
          {selectedNode.type === 'rag_extraction' && (
            <div className="space-y-5 animate-in fade-in slide-in-from-right-4 duration-300">

              <div className="bg-purple-50 border border-purple-200 p-3 rounded-md flex items-start gap-2">
                <Sparkles className="text-purple-600 mt-0.5" size={16} />
                <p className="text-xs text-purple-800">
                  Ten blok automatycznie przeszuka wgrane dokumenty projektu (RAG) i wygeneruje treść na podstawie poniższego promptu.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AI Prompt <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={selectedNode.data.prompt}
                  onChange={(e) => updateNodeData(selectedNode.id, { prompt: e.target.value })}
                  rows={5}
                  className="w-full p-3 border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500 text-sm resize-y"
                  placeholder="np. Przeanalizuj dziennik budowy i wypunktuj wszystkie przestoje betonowania wraz z ich przyczyną..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tekst zastępczy (Fallback)</label>
                <input
                  type="text"
                  value={selectedNode.data.fallback_text}
                  onChange={(e) => updateNodeData(selectedNode.id, { fallback_text: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-purple-500 focus:border-purple-500 text-sm"
                  placeholder="np. Brak odnotowanych przestojów w tym tygodniu."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Pojawi się w dokumencie, jeśli model nie znajdzie w wektorowej bazie danych kontekstu pasującego do Twojego promptu.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};