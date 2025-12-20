// Trust Score Card component
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatRiskGrade } from '@/lib/utils/formatters';
import type { RiskScore } from '@/lib/types/score';

interface TrustScoreCardProps {
  score: RiskScore;
}

export function TrustScoreCard({ score }: TrustScoreCardProps) {
  const gradeInfo = formatRiskGrade(score.grade);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Trust Score</CardTitle>
        <CardDescription>Current risk assessment</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-4xl font-bold">{score.score}</div>
              <div className="text-sm text-gray-500">Risk Score</div>
            </div>
            <Badge className={`${gradeInfo.bgColor} ${gradeInfo.color} text-lg px-4 py-2`}>
              Grade {score.grade}
            </Badge>
          </div>
          <div>
            <div className={`text-sm font-medium ${gradeInfo.color}`}>{gradeInfo.label}</div>
            <div className="mt-2 space-y-1">
              {score.flags.slice(0, 3).map((flag, idx) => (
                <div key={idx} className="text-xs text-gray-600">
                  • {flag}
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
