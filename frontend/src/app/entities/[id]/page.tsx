// Entity Detail page
'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { TrustScoreCard } from '@/components/dashboard/TrustScoreCard';
import { EntityRelationships } from '@/components/entities/EntityRelationships';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useEntity, useEntityRelationships } from '@/lib/hooks/useEntities';
import { useEntityScore } from '@/lib/hooks/useRiskScores';
import { formatDate, getEntityTypeLabel, getStatusColor } from '@/lib/utils/formatters';

export default function EntityDetailPage() {
  const params = useParams();
  const entityId = params.id ? parseInt(params.id as string) : null;

  const { data: entity, isLoading: loadingEntity } = useEntity(entityId);
  const { data: score, isLoading: loadingScore } = useEntityScore(entityId);
  const { data: relationshipsData, isLoading: loadingRelationships } = useEntityRelationships(entityId);

  if (loadingEntity) {
    return (
      <DashboardLayout>
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (!entity) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold">Entity Not Found</h2>
          <p className="mt-2 text-gray-600">The entity you&apos;re looking for doesn&apos;t exist.</p>
          <Link href="/entities">
            <Button className="mt-4">Back to Entities</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold">{entity.legal_name}</h1>
            <div className="mt-2 flex flex-wrap gap-2">
              <Badge variant="secondary">{getEntityTypeLabel(entity.type)}</Badge>
              {entity.jurisdiction && <Badge variant="outline">{entity.jurisdiction}</Badge>}
              {entity.status && (
                <Badge className={getStatusColor(entity.status)}>{entity.status}</Badge>
              )}
            </div>
          </div>
          <Link href="/entities">
            <Button variant="outline">Back</Button>
          </Link>
        </div>

        {/* Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Entity Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <div className="text-sm text-gray-600">External ID</div>
                    <div className="font-medium">{entity.external_id || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Source System</div>
                    <div className="font-medium">{entity.source_system}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Formation Date</div>
                    <div className="font-medium">{formatDate(entity.formation_date)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">EIN Status</div>
                    <div className="font-medium">
                      {entity.ein_verified ? 'Verified' : entity.ein_available ? 'Available' : 'N/A'}
                    </div>
                  </div>
                </div>

                {entity.registered_agent && (
                  <div className="pt-3 border-t">
                    <div className="text-sm text-gray-600">Registered Agent</div>
                    <div className="font-medium">{entity.registered_agent.full_name}</div>
                  </div>
                )}

                {entity.primary_address && (
                  <div className="pt-3 border-t">
                    <div className="text-sm text-gray-600">Primary Address</div>
                    <div className="font-medium">
                      {entity.primary_address.line1}
                      {entity.primary_address.line2 && <>, {entity.primary_address.line2}</>}
                      <br />
                      {entity.primary_address.city}, {entity.primary_address.state}{' '}
                      {entity.primary_address.postal_code}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Relationships */}
            {!loadingRelationships && relationshipsData && (
              <EntityRelationships relationships={relationshipsData.relationships} />
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {loadingScore ? (
              <Card>
                <CardContent className="flex justify-center py-8">
                  <LoadingSpinner />
                </CardContent>
              </Card>
            ) : score ? (
              <TrustScoreCard score={score} />
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Trust Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">No risk score available</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
