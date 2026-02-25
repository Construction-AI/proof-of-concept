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
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const { nodes, setNodes } = useSchemaStore();
  
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingNodes, setIsLoadingNodes] = useState(false);

  // NOWOŚĆ: Stan przechowujący strukturę jako string, aby sprawdzić czy zaszły faktyczne zmiany (do autosave'a)
  const [lastSavedState, setLastSavedState] = useState<string>('');

  const fetchTemplates = async () => {
    try {
      const data = await templatesService.getAll();
      setTemplates(data);
    } catch (error) {
      console.error("Błąd pobierania szablonów", error);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  // --- ZARZĄDZANIE SZABLONAMI ---

  const handleSelectTemplate = async (templateId: number) => {
    setSelectedTemplateId(templateId);
    setIsLoadingNodes(true);
    try {
      const savedNodes = await templatesService.getNodes(templateId);
      setNodes(savedNodes);
      setLastSavedState(JSON.stringify(savedNodes)); // Zabezpieczenie przed autosavem pustych zmian po załadowaniu
    } catch (error) {
      console.error("Błąd pobierania struktury", error);
    } finally {
      setIsLoadingNodes(false);
    }
  };

  const handleCreateTemplate = async () => {
    const name = window.prompt("Podaj nazwę dla nowego szablonu:");
    if (!name || !name.trim()) return;
    
    try {
      const newTemplate = await templatesService.create(name.trim());
      await fetchTemplates(); // Odśwież listę
      
      // Automatycznie przejdź do nowego, pustego szablonu
      setSelectedTemplateId(newTemplate.id);
      setNodes([]);
      setLastSavedState('[]');
    } catch (error) {
      alert("Nie udało się utworzyć szablonu.");
    }
  };

  const handleDeleteTemplate = async () => {
    if (!selectedTemplateId) return;
    if (!window.confirm("Czy na pewno chcesz usunąć ten szablon? Usunięcie jest nieodwracalne.")) return;

    try {
      await templatesService.delete(selectedTemplateId);
      await fetchTemplates(); // Odśwież listę
      
      // Wyczyść edytor
      setSelectedTemplateId(null);
      setNodes([]);
      setLastSavedState('');
    } catch (error) {
      alert("Nie udało się usunąć szablonu.");
    }
  };

  // --- LOGIKA ZAPISYWANIA ---

  const handleSave = async () => {
    if (!selectedTemplateId || isSaving) return;
    setIsSaving(true);
    try {
      await templatesService.saveNodes(selectedTemplateId, nodes);
      setLastSavedState(JSON.stringify(nodes)); // Po zapisie to jest nasz nowy punkt odniesienia
      
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (error) {
      console.error("Błąd zapisu!", error);
    } finally {
      setIsSaving(false);
    }
  };

  // --- MAGIA AUTOSAVE'A (DEBOUNCE) ---
  useEffect(() => {
    // Nie robimy autosave'a, jeśli ładujemy dane lub nic nie jest wybrane
    if (!selectedTemplateId || isLoadingNodes) return;

    const currentState = JSON.stringify(nodes);
    
    // Zapobiegamy pętli - zapisujemy tylko jeśli stan w edytorze różni się od ostatnio zapisanego w bazie
    if (currentState === lastSavedState) return;

    // Ustawiamy "stoper". Zapis nastąpi 2.5 sekundy po tym, jak użytkownik przestanie przesuwać klocki/pisać.
    const timeoutId = setTimeout(() => {
      handleSave();
    }, 2500);

    // Jeśli w ciągu tych 2.5 sek. `nodes` znowu się zmieni, czyścimy stary stoper i odpalamy nowy
    return () => clearTimeout(timeoutId);
  }, [nodes, selectedTemplateId, isLoadingNodes, lastSavedState]);


  // --- GENEROWANIE ---
  const handleGenerate = async () => {
    if (!selectedTemplateId || !projectId) return;
    setIsGenerating(true);
    try {
      // Dla pewności przed wygenerowaniem wymuszamy ostateczny zapis
      await templatesService.saveNodes(selectedTemplateId, nodes);
      setLastSavedState(JSON.stringify(nodes));
      
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
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center text-sm">
        <button onClick={() => navigate(`/projects/${projectId}`)} className="flex items-center gap-1 hover:text-blue-300 transition-colors">
          <ArrowLeft size={16} /> Powrót do projektu
        </button>
      </div>

      <TemplateHeader 
        templates={templates}
        selectedTemplateId={selectedTemplateId}
        onSelectTemplate={handleSelectTemplate}
        onSave={handleSave} // Zostawiłem, ale de facto i tak działa autosave w tle
        onGenerate={handleGenerate}
        onCreate={handleCreateTemplate}
        onDelete={handleDeleteTemplate}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        isGenerating={isGenerating}
        isSchemaEmpty={nodes.length === 0}
      />

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