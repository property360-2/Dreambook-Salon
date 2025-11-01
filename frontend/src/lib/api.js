const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:4000/api';

async function request(path, options = {}) {
  const { token, data, headers, method = 'GET' } = options;

  const fetchOptions = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(headers ?? {}),
    },
    body: data ? JSON.stringify(data) : undefined,
  };

  if (token) {
    fetchOptions.headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, fetchOptions);

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');
  const payload = isJson ? await response.json() : null;

  if (!response.ok) {
    const message =
      payload?.message ?? `Request failed with status ${response.status}`;
    const error = new Error(message);
    error.status = response.status;
    error.details = payload;
    throw error;
  }

  return payload;
}

export function apiClient(token) {
  return {
    get: (path) => request(path, { token }),
    post: (path, data) => request(path, { method: 'POST', data, token }),
    put: (path, data) => request(path, { method: 'PUT', data, token }),
    delete: (path) => request(path, { method: 'DELETE', token }),
  };
}

export const api = {
  register: (payload) =>
    request('/auth/register', { method: 'POST', data: payload }),
  login: (payload) => request('/auth/login', { method: 'POST', data: payload }),
  currentUser: (token) => request('/users/me', { token }),
  services: ({ includeInactive = false, token } = {}) => {
    const query = includeInactive ? '?includeInactive=true' : '';
    return request(`/services${query}`, { token });
  },
  createService: (token, payload) =>
    request('/services', { method: 'POST', data: payload, token }),
  linkServiceInventory: (token, serviceId, payload) =>
    request(`/services/${serviceId}/inventory`, {
      method: 'POST',
      data: payload,
      token,
    }),
  unlinkServiceInventory: (token, serviceId, inventoryId) =>
    request(`/services/${serviceId}/inventory/${inventoryId}`, {
      method: 'DELETE',
      token,
    }),
  appointments: {
    list: (token, params = {}) => {
      const search = new URLSearchParams();
      if (Array.isArray(params.status) && params.status.length > 0) {
        search.set('status', params.status.join(','));
      }
      if (params.from instanceof Date) {
        search.set('from', params.from.toISOString());
      }
      if (params.to instanceof Date) {
        search.set('to', params.to.toISOString());
      }
      const query = search.toString();
      return request(`/appointments${query ? `?${query}` : ''}`, { token });
    },
    available: ({ serviceId, date }) => {
      const search = new URLSearchParams({
        serviceId,
        date,
      });
      return request(`/appointments/available?${search.toString()}`);
    },
    create: (payload) =>
      request('/appointments', { method: 'POST', data: payload }),
    updateStatus: (token, id, payload) =>
      request(`/appointments/${id}/status`, {
        method: 'PUT',
        data: payload,
        token,
      }),
  },
  settings: {
    get: (token) => request('/settings', { token }),
    update: (token, payload) =>
      request('/settings', { method: 'PUT', data: payload, token }),
    listBlocked: (token, params = {}) => {
      const search = new URLSearchParams();
      if (params.from instanceof Date) {
        search.set('from', params.from.toISOString());
      }
      if (params.to instanceof Date) {
        search.set('to', params.to.toISOString());
      }
      const query = search.toString();
      return request(`/settings/blocked${query ? `?${query}` : ''}`, {
        token,
      });
    },
    createBlocked: (token, payload) =>
      request('/settings/blocked', { method: 'POST', data: payload, token }),
    deleteBlocked: (token, id) =>
      request(`/settings/blocked/${id}`, { method: 'DELETE', token }),
  },
  payments: {
    createDemo: (payload) =>
      request('/payments/demo', { method: 'POST', data: payload }),
    updateDemo: (id, payload) =>
      request(`/payments/demo/${id}`, { method: 'PUT', data: payload }),
    getDemo: (id) => request(`/payments/demo/${id}`),
  },
  chatbot: {
    listRules: (token) => request('/chatbot/rules', { token }),
    createRule: (token, payload) =>
      request('/chatbot/rules', { method: 'POST', data: payload, token }),
    updateRule: (token, id, payload) =>
      request(`/chatbot/rules/${id}`, { method: 'PUT', data: payload, token }),
    deleteRule: (token, id) =>
      request(`/chatbot/rules/${id}`, { method: 'DELETE', token }),
    respond: (payload) =>
      request('/chatbot/respond', { method: 'POST', data: payload }),
  },
  inventory: {
    list: (token) => request('/inventory', { token }),
    create: (token, payload) =>
      request('/inventory', { method: 'POST', data: payload, token }),
    update: (token, id, payload) =>
      request(`/inventory/${id}`, { method: 'PUT', data: payload, token }),
  },
  uploads: {
    serviceImage: (token, image) =>
      request('/uploads/service-image', {
        method: 'POST',
        data: { image },
        token,
      }),
  },
};
