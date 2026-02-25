// src/pages/SchemaBuilder.tsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { ArrowLeft } from 'lucide-react';

import { BlockPalette } from '../components/schema-editor/BlockPalette';
import { TreeEditor } from '../components/schema-editor/TreeEditor';
import { PropertyPanel } from '../components/schema-editor/PropertyPanel';
import { TemplateHeader } from '../components/schema-editor/TemplateHeader';

import { useSchemaStore } from '../store/schemaStore';
import { templatesService } from '../api/templates';
import { generatorService } from '../api/generator';

export const SchemaBuilder = () => {
  const { projectId } = useParams(); // ID projektu z adresu URL!
  const navigate = useNavigate();
  
  const { nodes, setNodes } = useSchemaStore();
  
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingNodes, setIsLoadingNodes] = useState(false);

  // 1. Pobierz listę dostępnych szablonów użytkownika po wejściu na stronę
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const data = await templatesService.getAll();
        setTemplates(data);
      } catch (error) {
        console.error("Błąd pobierania szablonów", error);
      }
    };
    fetchTemplates();
  }, []);

  // 2. Kiedy użytkownik wybierze szablon z listy, pobierz jego klocki (nodes) z bazy
  const handleSelectTemplate = async (templateId: number) => {
    setSelectedTemplateId(templateId);
    setIsLoadingNodes(true);
    try {
      const savedNodes = await templatesService.getNodes(templateId);
      setNodes(savedNodes);
    } catch (error) {
      console.error("Błąd pobierania struktury", error);
    } finally {
      setIsLoadingNodes(false);
    }
  };

  // 3. Zapisywanie
  const handleSave = async () => {
    if (!selectedTemplateId) return;
    setIsSaving(true);
    try {
      await templatesService.saveNodes(selectedTemplateId, nodes);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (error) {
      alert("Błąd zapisu!");
    } finally {
      setIsSaving(false);
    }
  };

  // 4. GENEROWANIE RAPORTU (Zapis + Strzał do API LLM)
  const handleGenerate = async () => {
    if (!selectedTemplateId || !projectId) return;
    setIsGenerating(true);
    try {
      // Zawsze upewniamy się, że najnowszy stan jest w bazie przed generowaniem
      await templatesService.saveNodes(selectedTemplateId, nodes);
      
      // Wywołujemy nasz nowy silnik!
      await generatorService.generatePdf(Number(projectId), selectedTemplateId);
    } catch (error) {
      console.error(error);
      alert("Wystąpił błąd podczas generowania dokumentu AI.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 overflow-hidden">
      
      {/* Pasek Nawigacji Powrotnej */}
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center text-sm">
        <button onClick={() => navigate(`/projects/${projectId}`)} className="flex items-center gap-1 hover:text-blue-300 transition-colors">
          <ArrowLeft size={16} /> Powrót do projektu
        </button>
      </div>

      {/* Wyciągnięty Header Szablonów */}
      <TemplateHeader 
        templates={templates}
        selectedTemplateId={selectedTemplateId}
        onSelectTemplate={handleSelectTemplate}
        onSave={handleSave}
        onGenerate={handleGenerate}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        isGenerating={isGenerating}
        isSchemaEmpty={nodes.length === 0}
      />

      {/* Obszar roboczy Drag & Drop */}
      <div className="flex flex-1 overflow-hidden">
        <DndProvider backend={HTML5Backend}>
          <BlockPalette />
          <TreeEditor isLoading={isLoadingNodes} /> 
          <PropertyPanel />
        </DndProvider>
      </div>

    </div>
  );
};