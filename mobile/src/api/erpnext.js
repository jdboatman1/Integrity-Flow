import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ERPNEXT_URL = 'https://erp.aaairrigationservice.com';

const api = axios.create({
  baseURL: ERPNEXT_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Add auth token to requests
api.interceptors.request.use(
  async config => {
    const apiKey = await AsyncStorage.getItem('api_key');
    const apiSecret = await AsyncStorage.getItem('api_secret');

    if (apiKey && apiSecret) {
      config.headers.Authorization = `token ${apiKey}:${apiSecret}`;
    }

    return config;
  },
  error => Promise.reject(error),
);

// Handle errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      AsyncStorage.multiRemove(['api_key', 'api_secret', 'user_data']);
    }
    return Promise.reject(error);
  },
);

export const erpnextAPI = {
  // Authentication
  login: async (username, password) => {
    const response = await api.post('/api/method/login', {
      usr: username,
      pwd: password,
    });
    return response.data;
  },

  // Customers
  getCustomers: async (filters = {}) => {
    const response = await api.get('/api/resource/Customer', {
      params: {
        fields: JSON.stringify(['name', 'customer_name', 'mobile_no', 'email_id']),
        filters: JSON.stringify(filters),
        limit_page_length: 50,
      },
    });
    return response.data.data;
  },

  getCustomer: async customerId => {
    const response = await api.get(`/api/resource/Customer/${customerId}`);
    return response.data.data;
  },

  // Quotations (Estimates)
  getQuotations: async (filters = {}) => {
    const response = await api.get('/api/resource/Quotation', {
      params: {
        fields: JSON.stringify(['*']),
        filters: JSON.stringify(filters),
        limit_page_length: 50,
      },
    });
    return response.data.data;
  },

  createQuotation: async quotationData => {
    const response = await api.post('/api/resource/Quotation', quotationData);
    return response.data.data;
  },

  updateQuotation: async (quotationId, quotationData) => {
    const response = await api.put(
      `/api/resource/Quotation/${quotationId}`,
      quotationData,
    );
    return response.data.data;
  },

  // Sales Invoices
  createInvoice: async invoiceData => {
    const response = await api.post('/api/resource/Sales Invoice', invoiceData);
    return response.data.data;
  },

  // File Upload
  uploadFile: async (file, doctype, docname) => {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: file.type || 'image/jpeg',
      name: file.fileName || 'photo.jpg',
    });
    formData.append('doctype', doctype);
    formData.append('docname', docname);

    const response = await api.post('/api/method/upload_file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.message;
  },

  // Custom App API
  getCustomerPortalData: async customerId => {
    const response = await api.get(
      '/api/method/integrity_flow_custom.api.get_customer_portal_data',
      {
        params: {customer_id: customerId},
      },
    );
    return response.data.message;
  },

  syncToGCal: async quotationId => {
    const response = await api.post(
      '/api/method/integrity_flow_custom.api.sync_estimate_to_gcal',
      {quotation_id: quotationId},
    );
    return response.data.message;
  },
};

export default api;
