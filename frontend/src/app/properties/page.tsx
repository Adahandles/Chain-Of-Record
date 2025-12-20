// Properties search page
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useProperties } from '@/lib/hooks/useProperties';
import { formatCurrency, formatAcres } from '@/lib/utils/formatters';
import type { PropertySearchParams } from '@/lib/types/property';

export default function PropertiesPage() {
  const [searchParams, setSearchParams] = useState<PropertySearchParams>({ limit: 50 });
  const [county, setCounty] = useState('');
  const [minValue, setMinValue] = useState('');
  const [maxValue, setMaxValue] = useState('');

  const { data: properties, isLoading, error } = useProperties(searchParams);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchParams({
      county: county || undefined,
      min_value: minValue ? parseFloat(minValue) : undefined,
      max_value: maxValue ? parseFloat(maxValue) : undefined,
      limit: 50,
    });
  };

  const handleReset = () => {
    setCounty('');
    setMinValue('');
    setMaxValue('');
    setSearchParams({ limit: 50 });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Properties</h1>
          <p className="text-gray-600">Search and explore property records</p>
        </div>

        {/* Search Form */}
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <label htmlFor="county" className="mb-2 block text-sm font-medium">
                    County
                  </label>
                  <Input
                    id="county"
                    placeholder="e.g., Marion"
                    value={county}
                    onChange={(e) => setCounty(e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="minValue" className="mb-2 block text-sm font-medium">
                    Min Market Value
                  </label>
                  <Input
                    id="minValue"
                    type="number"
                    placeholder="0"
                    value={minValue}
                    onChange={(e) => setMinValue(e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="maxValue" className="mb-2 block text-sm font-medium">
                    Max Market Value
                  </label>
                  <Input
                    id="maxValue"
                    type="number"
                    placeholder="1000000"
                    value={maxValue}
                    onChange={(e) => setMaxValue(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex space-x-2">
                <Button type="submit">Search</Button>
                <Button type="button" variant="outline" onClick={handleReset}>
                  Reset
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        <div>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600">Error loading properties. Please try again.</p>
            </div>
          ) : properties && properties.length > 0 ? (
            <div>
              <p className="mb-4 text-sm text-gray-600">{properties.length} results found</p>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {properties.map((property) => (
                  <Link key={property.id} href={`/properties/${property.id}`}>
                    <Card className="transition-shadow hover:shadow-md">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold">Parcel {property.parcel_id}</h3>
                            <Badge variant="outline" className="mt-1">
                              {property.county} County
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          {property.market_value && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Market Value:</span>
                              <span className="font-medium">
                                {formatCurrency(property.market_value)}
                              </span>
                            </div>
                          )}
                          {property.acreage && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Size:</span>
                              <span>{formatAcres(property.acreage)}</span>
                            </div>
                          )}
                          {property.land_use_code && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Land Use:</span>
                              <span>{property.land_use_code}</span>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600">No properties found. Try adjusting your search criteria.</p>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
