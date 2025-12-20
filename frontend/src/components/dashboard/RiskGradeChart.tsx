// Risk Grade Chart component
'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface RiskGradeChartProps {
  distribution: Record<string, number>;
}

const GRADE_COLORS: Record<string, string> = {
  A: '#10b981',
  B: '#3b82f6',
  C: '#eab308',
  D: '#f97316',
  F: '#ef4444',
};

export function RiskGradeChart({ distribution }: RiskGradeChartProps) {
  const data = Object.entries(distribution).map(([grade, count]) => ({
    grade,
    count,
    color: GRADE_COLORS[grade] || '#6b7280',
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Grade Distribution</CardTitle>
        <CardDescription>Entity risk grades across the system</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="grade" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" radius={[8, 8, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
