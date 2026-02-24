// src/components/project/UploadZone.tsx
import { useRef } from 'react';
import { UploadCloud } from 'lucide-react';

interface UploadZoneProps {
  isUploading: boolean;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const UploadZone = ({ isUploading, onFileSelect }: UploadZoneProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Funkcja czyszcząca input po wybraniu pliku (aby można było wgrać ten sam plik ponownie)
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFileSelect(e);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="bg-white p-10 rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center text-center mb-8">
      <UploadCloud className="text-gray-400 mb-4" size={48} />
      <h3 className="text-xl font-semibold text-gray-800 mb-2">
        Zasil bazę wiedzy RAG
      </h3>
      <p className="text-gray-500 mb-6">
        Wgraj dokumenty (PDF, DOCX), które posłużą jako kontekst dla tego projektu.
      </p>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleChange}
        className="hidden"
        accept=".pdf,.txt,.docx"
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isUploading}
        className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors font-medium"
      >
        {isUploading ? "Indeksowanie w Qdrant..." : "Wybierz plik z dysku"}
      </button>
    </div>
  );
};