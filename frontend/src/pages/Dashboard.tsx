import { useState } from 'react';
import { Navbar } from '../components/dashboard/Navbar';
import { ToolCards } from '../components/dashboard/ToolCards';
import { ProjectList } from '../components/dashboard/ProjectList';
import { TemplateList } from '../components/dashboard/TemplateList';
import { LibraryAssignModal } from '../components/libraries/LibraryAssignModal';

export const Dashboard = () => {
  const [assigningTemplateId, setAssigningTemplateId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <ToolCards />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          <ProjectList />
          <TemplateList onAssignToLibrary={(id) => setAssigningTemplateId(id)} />
        </div>
      </main>

      {assigningTemplateId && (
        <LibraryAssignModal 
          templateId={assigningTemplateId} 
          onClose={() => setAssigningTemplateId(null)} 
        />
      )}
    </div>
  );
};