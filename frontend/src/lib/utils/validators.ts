// Validation utilities

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidPassword(password: string): boolean {
  // At least 8 characters
  return password.length >= 8;
}

export function validateSearchQuery(query: string): boolean {
  // At least 2 characters for search
  return query.trim().length >= 2;
}

export function sanitizeSearchInput(input: string): string {
  // Remove special characters that might cause issues
  return input.trim().replace(/[<>]/g, '');
}
