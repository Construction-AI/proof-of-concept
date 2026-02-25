import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderGit2, Plus } from 'lucide-react';
import { projectsService, type Project } from '../../api/projects';

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
    <div>
      <form onSubmit={handleCreate} className="mb-6 flex gap-4 bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <input 
          type="text" placeholder="Nazwa projektu..." value={newTitle} 
          onChange={(e) => setNewTitle(e.target.value)} 
          className="flex-1 border px-4 py-2 rounded-md outline-none focus:border-blue-500" 
        />
        <button type="submit" disabled={!newTitle.trim()} className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
          <Plus size={20} /> Utwórz
        </button>
      </form>
      
      <div className="grid grid-cols-1 gap-4">
        {projects.length === 0 ? <p className="text-gray-500">Brak projektów.</p> : null}
        {projects.map((p) => (
          <div key={p.id} onClick={() => navigate(`/projects/${p.id}`)} className="bg-white p-4 rounded-lg border hover:border-blue-300 cursor-pointer flex items-center gap-4 shadow-sm transition-colors">
            <FolderGit2 className="text-blue-500" size={24} />
            <span className="font-semibold text-gray-800">{p.title}</span>
          </div>
        ))}
      </div>
    </div>
  );
};