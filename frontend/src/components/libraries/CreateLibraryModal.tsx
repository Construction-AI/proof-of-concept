import { useState } from 'react';
import { librariesService } from '../../api/libraries';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export const CreateLibraryModal = ({ onClose }: { onClose: () => void }) => {
  const [form, setForm] = useState({ name: '', industry: 'Budownictwo', description: '' });

  const handleSubmit = async () => {
    if (!form.name) return;
    await librariesService.create(form.name, form.industry, form.description);
    onClose();
    window.location.reload(); 
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Utwórz nową bibliotekę</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <Input 
            placeholder="Nazwa" 
            value={form.name}
            onChange={e => setForm({...form, name: e.target.value})} 
          />
          <Select value={form.industry} onValueChange={v => setForm({...form, industry: v})}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="Budownictwo">Budownictwo</SelectItem>
              <SelectItem value="Architektura">Architektura</SelectItem>
              <SelectItem value="BHP">BHP</SelectItem>
            </SelectContent>
          </Select>
          <Textarea 
            placeholder="Opis" 
            value={form.description}
            onChange={e => setForm({...form, description: e.target.value})} 
            rows={3} 
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Anuluj</Button>
          <Button onClick={handleSubmit} disabled={!form.name} className="bg-emerald-600 hover:bg-emerald-700">Utwórz</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};