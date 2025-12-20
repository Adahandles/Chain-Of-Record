// Alerts List component
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime } from '@/lib/utils/formatters';
import type { HighRiskEntity } from '@/lib/types/score';

interface AlertsListProps {
  alerts: HighRiskEntity[];
}

export function AlertsList({ alerts }: AlertsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>High-Risk Alerts</CardTitle>
        <CardDescription>Entities requiring attention</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <p className="text-sm text-gray-500">No high-risk alerts at this time</p>
          ) : (
            alerts.map((alert) => (
              <div key={alert.entity.id} className="flex items-start justify-between border-b pb-3 last:border-0">
                <div className="flex-1">
                  <h4 className="font-medium">{alert.entity.legal_name}</h4>
                  <p className="text-sm text-gray-500">
                    {alert.entity.type} • {alert.entity.jurisdiction}
                  </p>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {alert.flags.slice(0, 2).map((flag, idx) => (
                      <span key={idx} className="text-xs text-gray-600">
                        {flag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="ml-4 flex flex-col items-end">
                  <Badge variant="danger">Grade {alert.grade}</Badge>
                  <span className="mt-1 text-xs text-gray-500">
                    {formatDateTime(alert.calculated_at)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
