// Dashboard page
'use client';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { TrustScoreCard } from '@/components/dashboard/TrustScoreCard';
import { RiskGradeChart } from '@/components/dashboard/RiskGradeChart';
import { AlertsList } from '@/components/dashboard/AlertsList';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useHighRiskEntities, useScoringStatistics } from '@/lib/hooks/useRiskScores';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatNumber } from '@/lib/utils/formatters';

export default function DashboardPage() {
  const { data: highRiskData, isLoading: loadingAlerts } = useHighRiskEntities('F', 10);
  const { data: stats, isLoading: loadingStats } = useScoringStatistics();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-600">Overview of entity and property intelligence</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Entities Scored</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingStats ? (
                <LoadingSpinner size="sm" />
              ) : (
                <div className="text-2xl font-bold">{formatNumber(stats?.total_entities_scored)}</div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Average Risk Score</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingStats ? (
                <LoadingSpinner size="sm" />
              ) : (
                <div className="text-2xl font-bold">
                  {stats?.average_score ? stats.average_score.toFixed(1) : 'N/A'}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">High-Risk Entities</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingAlerts ? (
                <LoadingSpinner size="sm" />
              ) : (
                <div className="text-2xl font-bold text-red-600">
                  {formatNumber(highRiskData?.total_entities)}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className="h-3 w-3 rounded-full bg-green-500" />
                <span className="text-sm font-medium">Operational</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-6">
            {!loadingStats && stats?.grade_distribution && (
              <RiskGradeChart distribution={stats.grade_distribution} />
            )}
            {!loadingAlerts && highRiskData && <AlertsList alerts={highRiskData.entities} />}
          </div>
          <div className="space-y-6">
            <RecentActivity />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
