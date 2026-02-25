// src/pages/Dashboard.tsx
import { useState } from 'react';
import { Navbar } from '../components/dashboard/Navbar'; // Wyprowadzone do osobnego pliku
import { ToolCards } from '../components/dashboard/ToolCards';
import { ProjectList } from '../components/dashboard/ProjectList';
import { TemplateList } from '../components/dashboard/TemplateList';
import { LibraryAssignModal } from '../components/libraries/LibraryAssignModal';

export const Dashboard = () => {
  const [assigningTemplateId, setAssigningTemplateId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-8">
        
        <ToolCards /> {/* Dwa duże kolorowe kafelki */}
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 mt-10">
          {/* Lewa kolumna: Projekty */}
          <section>
             <h2 className="text-2xl font-bold text-gray-900 mb-6">Twoje Projekty</h2>
             <ProjectList />
          </section>

          {/* Prawa kolumna: Szablony */}
          <section>
             <h2 className="text-2xl font-bold text-gray-900 mb-6">Moje Szablony</h2>
             <TemplateList onAssignToLibrary={(id) => setAssigningTemplateId(id)} />
          </section>
        </div>

      </main>

      {/* Renderowanie Modala */}
      {assigningTemplateId && (
        <LibraryAssignModal 
          templateId={assigningTemplateId} 
          onClose={() => setAssigningTemplateId(null)} 
        />
      )}
    </div>
  );
};