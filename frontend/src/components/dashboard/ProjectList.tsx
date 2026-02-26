import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderGit2, Plus } from 'lucide-react';
import { projectsService, type Project } from '../../api/projects';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const ProjectList = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [newTitle, setNewTitle] = useState('');
  const navigate = useNavigate();

  useEffect(() => { fetchProjects(); }, []);
  
  const fetchProjects = async () => {
    const data = await projectsService.getAll();
    setProjects(data);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    await projectsService.create(newTitle);
    setNewTitle('');
    fetchProjects();
  };

  return (
    <Card className="h-full border-0 shadow-none sm:border sm:shadow-sm">
      <CardHeader className="px-0 sm:px-6">
        <CardTitle>Twoje Projekty</CardTitle>
      </CardHeader>
      <CardContent className="px-0 sm:px-6 space-y-4">
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input 
            placeholder="Nazwa nowego projektu..." 
            value={newTitle} 
            onChange={(e) => setNewTitle(e.target.value)} 
          />
          <Button type="submit" disabled={!newTitle.trim()}>
            <Plus className="h-4 w-4 sm:mr-2" /> 
            <span className="hidden sm:inline">Dodaj</span>
          </Button>
        </form>
        
        <div className="flex flex-col gap-2 pt-2">
          {projects.length === 0 && <p className="text-sm text-muted-foreground">Brak projektów.</p>}
          {projects.map((p) => (
            <div 
              key={p.id} 
              onClick={() => navigate(`/projects/${p.id}`)} 
              className="flex items-center gap-3 p-3 rounded-md border bg-card hover:bg-accent hover:text-accent-foreground cursor-pointer transition-colors"
            >
              <FolderGit2 className="h-5 w-5 text-muted-foreground" />
              <span className="font-medium">{p.title}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};