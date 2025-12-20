// Entity Search Form component
'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface EntitySearchFormProps {
  onSearch: (params: {
    name?: string;
    jurisdiction?: string;
    entity_type?: string;
    status?: string;
  }) => void;
}

export function EntitySearchForm({ onSearch }: EntitySearchFormProps) {
  const [name, setName] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [entityType, setEntityType] = useState('');
  const [status, setStatus] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      name: name || undefined,
      jurisdiction: jurisdiction || undefined,
      entity_type: entityType || undefined,
      status: status || undefined,
    });
  };

  const handleReset = () => {
    setName('');
    setJurisdiction('');
    setEntityType('');
    setStatus('');
    onSearch({});
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <label htmlFor="name" className="mb-2 block text-sm font-medium">
                Entity Name
              </label>
              <Input
                id="name"
                placeholder="Search by name..."
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="jurisdiction" className="mb-2 block text-sm font-medium">
                Jurisdiction
              </label>
              <Input
                id="jurisdiction"
                placeholder="e.g., FL"
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="entityType" className="mb-2 block text-sm font-medium">
                Entity Type
              </label>
              <select
                id="entityType"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                value={entityType}
                onChange={(e) => setEntityType(e.target.value)}
              >
                <option value="">All Types</option>
                <option value="llc">LLC</option>
                <option value="corp">Corporation</option>
                <option value="trust">Trust</option>
                <option value="nonprofit">Non-Profit</option>
              </select>
            </div>
            <div>
              <label htmlFor="status" className="mb-2 block text-sm font-medium">
                Status
              </label>
              <select
                id="status"
                className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
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
  );
}
