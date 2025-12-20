// Entity Relationships component
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Relationship } from '@/lib/types';

interface EntityRelationshipsProps {
  relationships: Relationship[];
}

export function EntityRelationships({ relationships }: EntityRelationshipsProps) {
  if (relationships.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Relationships</CardTitle>
          <CardDescription>No relationships found</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Relationships</CardTitle>
        <CardDescription>{relationships.length} connections found</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {relationships.map((rel) => (
            <div key={rel.id} className="border-b pb-3 last:border-0">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge variant={rel.direction === 'outgoing' ? 'default' : 'secondary'}>
                      {rel.direction}
                    </Badge>
                    <span className="text-sm font-medium">{rel.type}</span>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <div>
                      From: {rel.from_type} #{rel.from_id}
                    </div>
                    <div>
                      To: {rel.to_type} #{rel.to_id}
                    </div>
                  </div>
                  {rel.confidence && (
                    <div className="mt-1 text-xs text-gray-500">
                      Confidence: {(rel.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
