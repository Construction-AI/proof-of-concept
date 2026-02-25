import { useEffect, useState } from 'react';
import { librariesService, type TemplateLibrary } from '../api/libraries';
import { LibraryHeader } from '../components/libraries/LibraryHeader';
import { LibraryGrid } from '../components/libraries/LibraryGrid';
import { CreateLibraryModal } from '../components/libraries/CreateLibraryModal';
import { LibraryTemplates } from './LibraryTemplates';
import { useNavigate } from 'react-router-dom';

export const Library = () => {
  const [libraries, setLibraries] = useState<TemplateLibrary[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Stany dla modala Tworzenia Biblioteki
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  // Stany dla modala Przeglądania Szablonów w Bibliotece
  const [selectedLibrary, setSelectedLibrary] = useState<TemplateLibrary | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => fetchLibraries(), 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchLibraries = async () => {
    setIsLoading(true);
    try {
      const data = await librariesService.getAll(search);
      setLibraries(data);
    } catch (error) {
      console.error('Błąd pobierania bibliotek', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <LibraryHeader onSearch={setSearch} onCreateClick={() => setShowCreateModal(true)} />
        <LibraryGrid searchQuery={search} onOpenLibrary={setSelectedLibrary} />
        
        {showCreateModal && <CreateLibraryModal onClose={() => setShowCreateModal(false)} />}
      </div>
    </div>
  );
};