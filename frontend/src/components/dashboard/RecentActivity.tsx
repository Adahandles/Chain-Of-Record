// Recent Activity component
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDateTime } from '@/lib/utils/formatters';

interface Activity {
  id: string;
  type: string;
  description: string;
  timestamp: string;
}

interface RecentActivityProps {
  activities?: Activity[];
}

export function RecentActivity({ activities = [] }: RecentActivityProps) {
  // Mock data for now
  const mockActivities: Activity[] = [
    {
      id: '1',
      type: 'entity_created',
      description: 'New entity registered: ABC Properties LLC',
      timestamp: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'score_calculated',
      description: 'Risk score updated for XYZ Corporation',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: '3',
      type: 'alert_triggered',
      description: 'High-risk alert for DEF Holdings',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
  ];

  const displayActivities = activities.length > 0 ? activities : mockActivities;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest system events</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {displayActivities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3 border-b pb-3 last:border-0">
              <div className="mt-1 h-2 w-2 rounded-full bg-blue-600" />
              <div className="flex-1">
                <p className="text-sm">{activity.description}</p>
                <p className="text-xs text-gray-500">{formatDateTime(activity.timestamp)}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
