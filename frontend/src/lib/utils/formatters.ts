// Formatter utilities for displaying data

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatDate(date: string | null | undefined): string {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(date: string | null | undefined): string {
  if (!date) return 'N/A';
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatAcres(acres: number | null | undefined): string {
  if (acres === null || acres === undefined) return 'N/A';
  return `${acres.toFixed(2)} acres`;
}

export function formatRiskGrade(grade: string): {
  label: string;
  color: string;
  bgColor: string;
} {
  const gradeMap: Record<string, { label: string; color: string; bgColor: string }> = {
    A: { label: 'Low Risk', color: 'text-green-700', bgColor: 'bg-green-100' },
    B: { label: 'Moderate Risk', color: 'text-blue-700', bgColor: 'bg-blue-100' },
    C: { label: 'Medium Risk', color: 'text-yellow-700', bgColor: 'bg-yellow-100' },
    D: { label: 'High Risk', color: 'text-orange-700', bgColor: 'bg-orange-100' },
    F: { label: 'Critical Risk', color: 'text-red-700', bgColor: 'bg-red-100' },
  };
  return gradeMap[grade] || gradeMap.C;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function getEntityTypeLabel(type: string): string {
  const typeMap: Record<string, string> = {
    llc: 'LLC',
    corp: 'Corporation',
    trust: 'Trust',
    nonprofit: 'Non-Profit',
    person: 'Individual',
  };
  return typeMap[type.toLowerCase()] || type;
}

export function getStatusColor(status: string | null | undefined): string {
  if (!status) return 'text-gray-500';
  const statusLower = status.toLowerCase();
  if (statusLower.includes('active')) return 'text-green-600';
  if (statusLower.includes('inactive') || statusLower.includes('dissolved')) return 'text-red-600';
  return 'text-yellow-600';
}
