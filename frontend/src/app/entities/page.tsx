// Entities list page
'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { EntitySearchForm } from '@/components/entities/EntitySearchForm';
import { EntityCard } from '@/components/entities/EntityCard';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { useEntities } from '@/lib/hooks/useEntities';
import type { EntitySearchParams } from '@/lib/types/entity';

export default function EntitiesPage() {
  const [searchParams, setSearchParams] = useState<EntitySearchParams>({ limit: 50 });
  const { data: entities, isLoading, error } = useEntities(searchParams);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Entities</h1>
          <p className="text-gray-600">Search and explore business entities</p>
        </div>

        <EntitySearchForm onSearch={(params) => setSearchParams({ ...params, limit: 50 })} />

        <div>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600">Error loading entities. Please try again.</p>
            </div>
          ) : entities && entities.length > 0 ? (
            <div>
              <p className="mb-4 text-sm text-gray-600">{entities.length} results found</p>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {entities.map((entity) => (
                  <EntityCard key={entity.id} entity={entity} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">No entities found. Try adjusting your search criteria.</p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
