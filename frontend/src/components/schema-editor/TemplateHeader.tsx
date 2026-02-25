import { Save, Check, Loader2, FileDown, Plus, Trash2 } from 'lucide-react'; // Dodano Plus i Trash2

interface TemplateHeaderProps {
  templates: any[]; 
  selectedTemplateId: number | null;
  onSelectTemplate: (id: number) => void;
  
  onSave: () => void;
  onGenerate: () => void;
  onCreate: () => void; // NOWE
  onDelete: () => void; // NOWE
  
  isSaving: boolean;
  saveSuccess: boolean;
  isGenerating: boolean;
  isSchemaEmpty: boolean;
}

export const TemplateHeader = ({
  templates, selectedTemplateId, onSelectTemplate, 
  onSave, onGenerate, onCreate, onDelete, 
  isSaving, saveSuccess, isGenerating, isSchemaEmpty
}: TemplateHeaderProps) => {

  return (
    <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between z-10 shadow-sm">
      
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-gray-900">Edytor Raportu</h1>
        <div className="h-6 w-px bg-gray-300 mx-2"></div>
        
        {/* Grupa wyboru i zarządzania szablonem */}
        <div className="flex items-center gap-2">
          <select 
            value={selectedTemplateId || ''}
            onChange={(e) => onSelectTemplate(Number(e.target.value))}
            className="border border-gray-300 rounded-md px-4 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 outline-none w-64 bg-gray-50"
          >
            <option value="" disabled>-- Wybierz szablon z biblioteki --</option>
            {templates.map(t => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>

          <button 
            onClick={onCreate}
            title="Utwórz nowy szablon"
            className="p-2 text-blue-600 hover:bg-blue-50 border border-blue-200 rounded-md transition-colors"
          >
            <Plus size={18} />
          </button>

          <button 
            onClick={onDelete}
            disabled={!selectedTemplateId}
            title="Usuń wybrany szablon"
            className="p-2 text-red-600 hover:bg-red-50 border border-red-200 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Kontrolka Auto-zapisu */}
        <div className="text-xs text-gray-500 mr-2 flex items-center w-24 justify-end">
           {isSaving ? (
             <span className="flex items-center gap-1"><Loader2 size={12} className="animate-spin"/> Zapisywanie...</span>
           ) : saveSuccess ? (
             <span className="flex items-center gap-1 text-green-600"><Check size={12}/> Zapisano</span>
           ) : null}
        </div>

        <button
          onClick={onGenerate}
          disabled={isGenerating || isSchemaEmpty || !selectedTemplateId}
          className="flex items-center gap-2 px-6 py-2 rounded-lg font-bold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 transition-colors shadow-sm"
        >
          {isGenerating ? <Loader2 size={18} className="animate-spin" /> : <FileDown size={18} />}
          Generuj PDF
        </button>
      </div>
    </div>
  );
};