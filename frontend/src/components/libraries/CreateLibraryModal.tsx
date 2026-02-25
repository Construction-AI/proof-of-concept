import { useState } from 'react';
import { librariesService } from '../../api/libraries';

export const CreateLibraryModal = ({ onClose }: { onClose: () => void }) => {
  const [form, setForm] = useState({ name: '', industry: 'Budownictwo', description: '' });

  const handleSubmit = async () => {
    if (!form.name) return;
    await librariesService.create(form.name, form.industry, form.description);
    onClose();
    window.location.reload(); // Najszybsze odświeżenie siatki po dodaniu
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <h3 className="text-xl font-bold mb-4">Utwórz nową bibliotekę</h3>
        <div className="space-y-4">
          <input type="text" placeholder="Nazwa" onChange={e => setForm({...form, name: e.target.value})} className="w-full border p-2 rounded-md outline-none" />
          <select onChange={e => setForm({...form, industry: e.target.value})} className="w-full border p-2 rounded-md outline-none">
            <option value="Budownictwo">Budownictwo</option>
            <option value="Architektura">Architektura</option>
            <option value="BHP">BHP</option>
          </select>
          <textarea placeholder="Opis" onChange={e => setForm({...form, description: e.target.value})} className="w-full border p-2 rounded-md outline-none" rows={3}></textarea>
          <div className="flex justify-end gap-3 mt-4">
            <button onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md">Anuluj</button>
            <button onClick={handleSubmit} disabled={!form.name} className="px-4 py-2 bg-emerald-600 text-white rounded-md">Utwórz</button>
          </div>
        </div>
      </div>
    </div>
  );
};