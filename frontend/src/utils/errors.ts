const formatFieldName = (field: string) =>
  field
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());

const flattenErrors = (value: unknown, field?: string): string[] => {
  if (typeof value === 'string') {
    return [field && field !== 'non_field_errors' ? `${formatFieldName(field)}: ${value}` : value];
  }
  if (Array.isArray(value)) {
    return value.flatMap((item) => flattenErrors(item, field));
  }
  if (value && typeof value === 'object') {
    return Object.entries(value).flatMap(([key, item]) => flattenErrors(item, key));
  }
  return [];
};

export const getErrorMessage = (error: unknown) => {
  const responseData = (error as { response?: { data?: unknown } })?.response?.data;
  if (responseData && typeof responseData === 'object') {
    const payload = responseData as { errors?: unknown; message?: unknown };
    const validationMessages = flattenErrors(payload.errors);
    if (validationMessages.length) return validationMessages.join(' ');
    if (typeof payload.message === 'string' && payload.message.trim()) return payload.message;
  }

  const errorMessage = (error as { message?: unknown })?.message;
  return typeof errorMessage === 'string' && errorMessage.trim() ? errorMessage : 'Something went wrong.';
};
