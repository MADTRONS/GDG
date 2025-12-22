import useSWR from 'swr';
import { fetchAdminMetrics } from '@/lib/api';

export function useAdminMetrics({ refreshInterval = 30000 } = {}) {
  const { data, error, isLoading } = useSWR('adminMetrics', fetchAdminMetrics, {
    refreshInterval,
    revalidateOnFocus: true,
  });

  return {
    data,
    isLoading,
    error,
  };
}