// Property Detail page
'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/shared/LoadingSpinner';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useProperty } from '@/lib/hooks/useProperties';
import { formatCurrency, formatDate, formatAcres } from '@/lib/utils/formatters';

export default function PropertyDetailPage() {
  const params = useParams();
  const propertyId = params.id ? parseInt(params.id as string) : null;

  const { data: property, isLoading } = useProperty(propertyId);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (!property) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold">Property Not Found</h2>
          <p className="mt-2 text-gray-600">The property you're looking for doesn't exist.</p>
          <Link href="/properties">
            <Button className="mt-4">Back to Properties</Button>
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
            <h1 className="text-3xl font-bold">Parcel {property.parcel_id}</h1>
            <div className="mt-2 flex flex-wrap gap-2">
              <Badge variant="outline">{property.county} County</Badge>
              {property.land_use_code && <Badge variant="secondary">{property.land_use_code}</Badge>}
            </div>
          </div>
          <Link href="/properties">
            <Button variant="outline">Back</Button>
          </Link>
        </div>

        {/* Content Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Property Details */}
          <Card>
            <CardHeader>
              <CardTitle>Property Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-3">
                <div>
                  <div className="text-sm text-gray-600">Parcel ID</div>
                  <div className="font-medium">{property.parcel_id}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">County</div>
                  <div className="font-medium">{property.county}</div>
                </div>
                {property.jurisdiction && (
                  <div>
                    <div className="text-sm text-gray-600">Jurisdiction</div>
                    <div className="font-medium">{property.jurisdiction}</div>
                  </div>
                )}
                {property.land_use_code && (
                  <div>
                    <div className="text-sm text-gray-600">Land Use Code</div>
                    <div className="font-medium">{property.land_use_code}</div>
                  </div>
                )}
                {property.acreage && (
                  <div>
                    <div className="text-sm text-gray-600">Acreage</div>
                    <div className="font-medium">{formatAcres(property.acreage)}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Financial Details */}
          <Card>
            <CardHeader>
              <CardTitle>Financial Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid gap-3">
                {property.market_value && (
                  <div>
                    <div className="text-sm text-gray-600">Market Value</div>
                    <div className="text-lg font-bold">{formatCurrency(property.market_value)}</div>
                  </div>
                )}
                {property.assessed_value && (
                  <div>
                    <div className="text-sm text-gray-600">Assessed Value</div>
                    <div className="font-medium">{formatCurrency(property.assessed_value)}</div>
                  </div>
                )}
                {property.last_sale_price && (
                  <div>
                    <div className="text-sm text-gray-600">Last Sale Price</div>
                    <div className="font-medium">{formatCurrency(property.last_sale_price)}</div>
                  </div>
                )}
                {property.last_sale_date && (
                  <div>
                    <div className="text-sm text-gray-600">Last Sale Date</div>
                    <div className="font-medium">{formatDate(property.last_sale_date)}</div>
                  </div>
                )}
                {property.tax_year && (
                  <div>
                    <div className="text-sm text-gray-600">Tax Year</div>
                    <div className="font-medium">{property.tax_year}</div>
                  </div>
                )}
                {property.homestead_exempt && (
                  <div>
                    <div className="text-sm text-gray-600">Homestead Exempt</div>
                    <div className="font-medium">{property.homestead_exempt}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Address */}
          {property.situs_address && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Property Address</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="font-medium">
                  {property.situs_address.line1}
                  {property.situs_address.line2 && <>, {property.situs_address.line2}</>}
                  <br />
                  {property.situs_address.city}, {property.situs_address.state}{' '}
                  {property.situs_address.postal_code}
                </div>
              </CardContent>
            </Card>
          )}

          {/* External Link */}
          {property.appraiser_url && (
            <Card className="lg:col-span-2">
              <CardContent className="pt-6">
                <a
                  href={property.appraiser_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  View on Property Appraiser Website →
                </a>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
