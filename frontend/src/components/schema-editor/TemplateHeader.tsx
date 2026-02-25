// src/components/schema-editor/TemplateHeader.tsx
import { Save, Check, Loader2, FileDown } from 'lucide-react';

interface TemplateHeaderProps {
  // Lista i wybór szablonu
  templates: any[]; 
  selectedTemplateId: number | null;
  onSelectTemplate: (id: number) => void;
  
  // Akcje
  onSave: () => void;
  onGenerate: () => void;
  
  // Stany
  isSaving: boolean;
  saveSuccess: boolean;
  isGenerating: boolean;
  isSchemaEmpty: boolean;
}

export const TemplateHeader = ({
  templates, selectedTemplateId, onSelectTemplate, 
  onSave, onGenerate, isSaving, saveSuccess, isGenerating, isSchemaEmpty
}: TemplateHeaderProps) => {

  return (
    <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between z-10">
      
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold text-gray-900">Edytor Raportu</h1>
        <div className="h-6 w-px bg-gray-300 mx-2"></div>
        
        {/* Dropdown z wyborem szablonu */}
        <select 
          value={selectedTemplateId || ''}
          onChange={(e) => onSelectTemplate(Number(e.target.value))}
          className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 outline-none"
        >
          <option value="" disabled>-- Wybierz szablon z biblioteki --</option>
          {templates.map(t => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onSave}
          disabled={isSaving || isSchemaEmpty || !selectedTemplateId}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 transition-colors"
        >
          {isSaving ? <Loader2 size={18} className="animate-spin" /> : saveSuccess ? <Check size={18} className="text-green-600" /> : <Save size={18} />}
          Zapisz
        </button>

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