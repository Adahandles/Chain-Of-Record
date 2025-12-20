// Entity Card component
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, getEntityTypeLabel, getStatusColor } from '@/lib/utils/formatters';
import type { EntityListItem } from '@/lib/types/entity';

interface EntityCardProps {
  entity: EntityListItem;
}

export function EntityCard({ entity }: EntityCardProps) {
  return (
    <Link href={`/entities/${entity.id}`}>
      <Card className="transition-shadow hover:shadow-md">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold text-lg">{entity.legal_name}</h3>
              <div className="mt-1 flex flex-wrap gap-2">
                <Badge variant="secondary">{getEntityTypeLabel(entity.type)}</Badge>
                {entity.jurisdiction && <Badge variant="outline">{entity.jurisdiction}</Badge>}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            {entity.status && (
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={getStatusColor(entity.status)}>{entity.status}</span>
              </div>
            )}
            {entity.formation_date && (
              <div className="flex justify-between">
                <span className="text-gray-600">Formation Date:</span>
                <span>{formatDate(entity.formation_date)}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
