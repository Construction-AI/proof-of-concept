import { useState } from 'react';
import { LibraryHeader } from '../components/libraries/LibraryHeader';
import { LibraryGrid } from '../components/libraries/LibraryGrid';
import { CreateLibraryModal } from '../components/libraries/CreateLibraryModal';

export const Library = () => {
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto">
        <LibraryHeader onSearch={setSearch} onCreateClick={() => setShowCreateModal(true)} />
        <LibraryGrid searchQuery={search} />
        {showCreateModal && <CreateLibraryModal onClose={() => setShowCreateModal(false)} />}
      </div>
    </div>
  );
};