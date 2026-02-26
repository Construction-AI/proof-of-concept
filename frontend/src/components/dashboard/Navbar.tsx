import { FolderGit2, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { Button } from '@/components/ui/button';

export const Navbar = () => {
  const { user, logout } = useAuthStore();
  
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center justify-between mx-auto px-4 max-w-6xl">
        <div className="flex items-center gap-2 font-bold text-lg">
          <FolderGit2 className="h-5 w-5 text-primary" />
          <span>RAG Builder</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-muted-foreground hidden sm:inline-block">
            {user?.email}
          </span>
          <Button variant="ghost" size="icon" onClick={logout} title="Wyloguj">
            <LogOut className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
    </header>
  );
};