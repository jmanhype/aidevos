import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../index';

// Define base API with authentication headers
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      // Get the token from the auth state
      const token = (getState() as RootState).auth.token;
      
      // If we have a token, add it to the headers
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      
      return headers;
    },
  }),
  tagTypes: ['Agents', 'Deployments', 'Monitoring', 'Projects'],
  endpoints: (builder) => ({
    // Define API endpoints here
  }),
});

// Export endpoints for use in components
export const {
  // Export hooks here when endpoints are defined
} = api;