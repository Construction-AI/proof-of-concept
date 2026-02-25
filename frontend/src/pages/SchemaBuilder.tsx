import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsService, type Project } from '../api/projects';
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

  // --- NOWE STANY DLA MODALA ---
  const [projects, setProjects] = useState<Project[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);

  // 1. Otwarcie modala i pobranie listy projektów
  const handleOpenGenerateModal = async () => {
    if (!selectedTemplateId) return;
    setShowModal(true);
    try {
      const data = await projectsService.getAll();
      setProjects(data);
    } catch (error) {
      console.error("Błąd pobierania projektów", error);
    }
  };

  // 2. Faktyczne generowanie po zatwierdzeniu w modalu
  const handleConfirmGenerate = async () => {
    if (!selectedTemplateId || !selectedProjectId) return;
    setIsGenerating(true);
    setShowModal(false); // Zamykamy modal
    try {
      await templatesService.saveNodes(selectedTemplateId, nodes);
      await generatorService.generatePdf(selectedProjectId, selectedTemplateId);
    } catch (error) {
      alert("Wystąpił błąd podczas generowania dokumentu.");
    } finally {
      setIsGenerating(false);
    }
  };

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

  return (
    <div className="flex flex-col h-screen bg-gray-100 overflow-hidden">
      <div className="bg-gray-800 text-white px-4 py-2 flex items-center text-sm">
        <button onClick={() => navigate(`/dashboard`)} className="flex items-center gap-1 hover:text-blue-300 transition-colors">
          <ArrowLeft size={16} /> Powrót do panelu użytkownika
        </button>
      </div>

      <TemplateHeader
        templates={templates}
        selectedTemplateId={selectedTemplateId}
        onSelectTemplate={handleSelectTemplate}
        onSave={handleSave} // Zostawiłem, ale de facto i tak działa autosave w tle
        onCreate={handleCreateTemplate}
        onDelete={handleDeleteTemplate}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        isGenerating={isGenerating}
        isSchemaEmpty={nodes.length === 0}
        onGenerate={handleOpenGenerateModal} // ZMIANA: Podpinamy nową funkcję
      />

      <div className="flex flex-1 overflow-hidden">
        <DndProvider backend={HTML5Backend}>
          <BlockPalette />
          <TreeEditor isLoading={isLoadingNodes} />
          <PropertyPanel />
        </DndProvider>
      </div>

      {/* --- NOWY MODAL WYBORU PROJEKTU --- */}
      {showModal && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl w-96 shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Wybierz projekt docelowy</h3>
            <p className="text-sm text-gray-500 mb-6">Z jakiej bazy wiedzy (projektu) AI ma pobrać dane do tego szablonu?</p>

            <select
              className="w-full border border-gray-300 p-2 rounded-lg mb-6 outline-none focus:ring-2 focus:ring-blue-500"
              onChange={(e) => setSelectedProjectId(Number(e.target.value))}
              defaultValue=""
            >
              <option value="" disabled>-- Wybierz projekt --</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.title}</option>
              ))}
            </select>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors"
              >
                Anuluj
              </button>
              <button
                onClick={handleConfirmGenerate}
                disabled={!selectedProjectId}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
              >
                Generuj raport
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};