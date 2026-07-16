export const getErrorMessage = (error: any) => {
  const message = error?.response?.data?.message || error?.message || 'Something went wrong.';
  return message;
};
