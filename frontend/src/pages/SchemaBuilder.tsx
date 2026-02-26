import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export const SchemaBuilder = () => {
  const [searchParams] = useSearchParams();
  const templateId = searchParams.get('templateId');
  const navigate = useNavigate();
  const { nodes, setNodes } = useSchemaStore();
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoadingNodes, setIsLoadingNodes] = useState(false);
  const [lastSavedState, setLastSavedState] = useState<string>('');

  const [projects, setProjects] = useState<Project[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);

  const fetchTemplates = async () => {
    try {
      setTemplates(await templatesService.getAll());
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => { fetchTemplates(); }, []);

  useEffect(() => {
    if (templateId) handleSelectTemplate(Number(templateId));
  }, [templateId]);

  const handleSelectTemplate = async (id: number) => {
    setSelectedTemplateId(id);
    setIsLoadingNodes(true);
    try {
      const savedNodes = await templatesService.getNodes(id);
      setNodes(savedNodes);
      setLastSavedState(JSON.stringify(savedNodes));
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoadingNodes(false);
    }
  };

  const handleCreateTemplate = async () => {
    const name = window.prompt("Podaj nazwę dla nowego szablonu:"); // Możesz zamienić na Dialog z shadcn
    if (!name?.trim()) return;
    try {
      const newTemplate = await templatesService.create(name.trim());
      await fetchTemplates();
      setSelectedTemplateId(newTemplate.id);
      setNodes([]);
      setLastSavedState('[]');
    } catch {
      alert("Nie udało się utworzyć szablonu.");
    }
  };

  const handleDeleteTemplate = async () => {
    if (!selectedTemplateId || !window.confirm("Na pewno usunąć?")) return;
    try {
      await templatesService.delete(selectedTemplateId);
      await fetchTemplates();
      setSelectedTemplateId(null);
      setNodes([]);
      setLastSavedState('');
    } catch {
      alert("Błąd usuwania.");
    }
  };

  const handleOpenGenerateModal = async () => {
    if (!selectedTemplateId) return;
    setShowModal(true);
    try {
      setProjects(await projectsService.getAll());
    } catch (error) {
      console.error(error);
    }
  };

  const handleConfirmGenerate = async () => {
    if (!selectedTemplateId || !selectedProjectId) return;
    setIsGenerating(true);
    setShowModal(false);
    try {
      await templatesService.saveNodes(selectedTemplateId, nodes);
      await generatorService.generatePdf(selectedProjectId, selectedTemplateId);
    } catch {
      alert("Błąd generowania.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSave = async () => {
    if (!selectedTemplateId || isSaving) return;
    setIsSaving(true);
    try {
      await templatesService.saveNodes(selectedTemplateId, nodes);
      setLastSavedState(JSON.stringify(nodes));
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    if (!selectedTemplateId || isLoadingNodes) return;
    const currentState = JSON.stringify(nodes);
    if (currentState === lastSavedState) return;
    const timeoutId = setTimeout(handleSave, 2500);
    return () => clearTimeout(timeoutId);
  }, [nodes, selectedTemplateId, isLoadingNodes, lastSavedState]);

  return (
    <div className="flex flex-col h-screen bg-muted/20 overflow-hidden">
      <div className="bg-slate-900 text-slate-100 px-4 py-2 flex items-center text-sm shrink-0">
        <Button variant="ghost" size="sm" onClick={() => navigate(`/dashboard`)} className="hover:bg-slate-800 hover:text-white h-auto py-1">
          <ArrowLeft className="mr-2 h-4 w-4" /> Powrót do panelu
        </Button>
      </div>

      <TemplateHeader
        templates={templates}
        selectedTemplateId={selectedTemplateId}
        onSelectTemplate={handleSelectTemplate}
        onCreate={handleCreateTemplate}
        onDelete={handleDeleteTemplate}
        isSaving={isSaving}
        saveSuccess={saveSuccess}
        isGenerating={isGenerating}
        isSchemaEmpty={nodes.length === 0}
        onGenerate={handleOpenGenerateModal}
      />

      <div className="flex flex-1 overflow-hidden">
        <DndProvider backend={HTML5Backend}>
          <BlockPalette />
          <TreeEditor isLoading={isLoadingNodes} />
          <PropertyPanel />
        </DndProvider>
      </div>

      <Dialog open={showModal} onOpenChange={setShowModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Wybierz projekt docelowy</DialogTitle>
            <DialogDescription>
              Z jakiej bazy wiedzy (projektu) AI ma pobrać dane do tego szablonu?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Select onValueChange={(v) => setSelectedProjectId(Number(v))}>
              <SelectTrigger>
                <SelectValue placeholder="Wybierz projekt..." />
              </SelectTrigger>
              <SelectContent>
                {projects.map(p => (
                  <SelectItem key={p.id} value={String(p.id)}>{p.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowModal(false)}>Anuluj</Button>
            <Button onClick={handleConfirmGenerate} disabled={!selectedProjectId}>Generuj raport</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};