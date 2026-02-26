import { useEffect, useState } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { librariesService, type TemplateLibrary } from '../../api/libraries';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Props {
  searchQuery: string;
}

export const LibraryGrid = ({ searchQuery }: Props) => {
  const [libraries, setLibraries] = useState<TemplateLibrary[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true);
      librariesService.getAll(searchQuery)
        .then(setLibraries)
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  if (loading) return <Loader2 className="animate-spin mx-auto my-12 h-8 w-8 text-emerald-500" />;
  if (libraries.length === 0) return <p className="text-center text-muted-foreground py-12">Brak wyników.</p>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {libraries.map((lib) => (
        <Card key={lib.id} className="flex flex-col justify-between hover:border-emerald-500/50 transition-colors">
          <CardHeader>
            <div className="flex justify-between items-start mb-2">
              <Badge variant="secondary" className="bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border-emerald-200">
                {lib.industry}
              </Badge>
              {lib.is_global && <Badge variant="outline" className="text-muted-foreground">Systemowe</Badge>}
            </div>
            <CardTitle>{lib.name}</CardTitle>
            <CardDescription className="line-clamp-3 mt-2">{lib.description}</CardDescription>
          </CardHeader>
          <CardFooter>
            <Button 
              variant="outline" 
              className="w-full hover:bg-emerald-50 hover:text-emerald-700 hover:border-emerald-200" 
              onClick={() => navigate(`/library/${lib.id}`)}
            >
              <Search className="mr-2 h-4 w-4" /> Przeglądaj
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};