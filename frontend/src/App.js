import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Login Page Component
function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/request-magic-link`, {
        email: email
      });
      setMessage(response.data.message);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send magic link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>AAA Irrigation Service</h1>
            <p className="subtitle">Customer Portal</p>
          </div>

          {message ? (
            <div className="success-message">
              <svg className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <h3>Check Your Email!</h3>
              <p>{message}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="email" className="label">Email Address</label>
                <input
                  type="email"
                  id="email"
                  className="input-field"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  data-testid="email-input"
                />
              </div>

              {error && <div className="error-message" data-testid="error-message">{error}</div>}

              <button
                type="submit"
                className="btn-primary full-width"
                disabled={loading}
                data-testid="login-button"
              >
                {loading ? 'Sending...' : 'Send Magic Link'}
              </button>
            </form>
          )}

          <p className="powered-by">Powered by Boatman Systems™</p>
        </div>
      </div>
    </div>
  );
}

// Verify Token Page
function VerifyPage() {
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const verifyToken = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');

      if (!token) {
        setError('No token provided');
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${BACKEND_URL}/api/auth/verify?token=${token}`);
        setCustomer(response.data.customer);
        localStorage.setItem('customer', JSON.stringify(response.data.customer));
      } catch (err) {
        setError(err.response?.data?.detail || 'Invalid or expired token');
      } finally {
        setLoading(false);
      }
    };

    verifyToken();
  }, []);

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner"></div>
        <p>Verifying your access...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-page">
        <div className="error-card">
          <h2>Access Denied</h2>
          <p>{error}</p>
          <a href="/" className="btn-primary">Request New Link</a>
        </div>
      </div>
    );
  }

  if (customer) {
    return <Navigate to="/dashboard" replace />;
  }

  return null;
}

// Dashboard Page
function Dashboard() {
  const [customer, setCustomer] = useState(null);
  const [quotations, setQuotations] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const customerData = localStorage.getItem('customer');
    if (!customerData) {
      window.location.href = '/';
      return;
    }

    const customer = JSON.parse(customerData);
    setCustomer(customer);

    // Fetch customer data
    const fetchData = async () => {
      try {
        const [quotRes, invRes] = await Promise.all([
          axios.get(`${BACKEND_URL}/api/customer/${customer.id}/quotations`),
          axios.get(`${BACKEND_URL}/api/customer/${customer.id}/invoices`)
        ]);
        setQuotations(quotRes.data.data || []);
        setInvoices(invRes.data.data || []);
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('customer');
    window.location.href = '/';
  };

  if (!customer) return null;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <h1>AAA Irrigation Service</h1>
            <button onClick={handleLogout} className="btn-secondary" data-testid="logout-button">Logout</button>
          </div>
        </div>
      </header>

      <div className="container dashboard-container">
        <div className="welcome-section">
          <h2>Welcome, {customer.name}!</h2>
          <p className="customer-email">{customer.email}</p>
        </div>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
            data-testid="overview-tab"
          >
            Overview
          </button>
          <button
            className={`tab ${activeTab === 'quotes' ? 'active' : ''}`}
            onClick={() => setActiveTab('quotes')}
            data-testid="quotes-tab"
          >
            Estimates ({quotations.length})
          </button>
          <button
            className={`tab ${activeTab === 'invoices' ? 'active' : ''}`}
            onClick={() => setActiveTab('invoices')}
            data-testid="invoices-tab"
          >
            Invoices ({invoices.length})
          </button>
          <button
            className={`tab ${activeTab === 'schedule' ? 'active' : ''}`}
            onClick={() => setActiveTab('schedule')}
            data-testid="schedule-tab"
          >
            Schedule Service
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-grid">
              <div className="stat-card">
                <h3>{quotations.length}</h3>
                <p>Active Estimates</p>
              </div>
              <div className="stat-card">
                <h3>{invoices.length}</h3>
                <p>Invoices</p>
              </div>
              <div className="stat-card">
                <h3>
                  ${invoices.reduce((sum, inv) => sum + (inv.grand_total || 0), 0).toFixed(2)}
                </h3>
                <p>Total Billed</p>
              </div>
            </div>
          )}

          {activeTab === 'quotes' && (
            <div className="quotes-list">
              {loading ? (
                <div className="spinner"></div>
              ) : quotations.length === 0 ? (
                <div className="empty-state">
                  <p>No estimates yet</p>
                </div>
              ) : (
                quotations.map((quote) => (
                  <div key={quote.name} className="quote-card card">
                    <div className="quote-header">
                      <h3>Estimate #{quote.name}</h3>
                      <span className={`status-badge status-${quote.status.toLowerCase()}`}>
                        {quote.status}
                      </span>
                    </div>
                    <div className="quote-details">
                      <p><strong>Date:</strong> {quote.transaction_date}</p>
                      <p><strong>Amount:</strong> ${quote.grand_total || 0}</p>
                      {quote.custom_service_description && (
                        <p><strong>Description:</strong> {quote.custom_service_description}</p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'invoices' && (
            <div className="invoices-list">
              {loading ? (
                <div className="spinner"></div>
              ) : invoices.length === 0 ? (
                <div className="empty-state">
                  <p>No invoices yet</p>
                </div>
              ) : (
                invoices.map((invoice) => (
                  <div key={invoice.name} className="invoice-card card">
                    <div className="invoice-header">
                      <h3>Invoice #{invoice.name}</h3>
                      <span className={`status-badge status-${invoice.status.toLowerCase()}`}>
                        {invoice.status}
                      </span>
                    </div>
                    <div className="invoice-details">
                      <p><strong>Date:</strong> {invoice.posting_date}</p>
                      <p><strong>Due Date:</strong> {invoice.due_date}</p>
                      <p><strong>Amount:</strong> ${invoice.grand_total || 0}</p>
                      <p><strong>Outstanding:</strong> ${invoice.outstanding_amount || 0}</p>
                    </div>
                    {invoice.outstanding_amount > 0 && (
                      <button className="btn-primary">Pay Now</button>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'schedule' && (
            <ScheduleServiceForm customerId={customer.id} customerEmail={customer.email} />
          )}
        </div>
      </div>

      <footer className="dashboard-footer">
        <p className="powered-by">Powered by Boatman Systems™</p>
      </footer>
    </div>
  );
}

// Schedule Service Form Component
function ScheduleServiceForm({ customerId, customerEmail }) {
  const [formData, setFormData] = useState({
    service_type: 'Residential Repair',
    preferred_date: '',
    preferred_time: '9AM-11AM',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    setError('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/schedule-appointment`, {
        customer_email: customerEmail,
        ...formData
      });
      setMessage('Appointment scheduled successfully! We will contact you soon.');
      setFormData({
        service_type: 'Residential Repair',
        preferred_date: '',
        preferred_time: '9AM-11AM',
        description: ''
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to schedule appointment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="schedule-form card">
      <h2>Schedule a Service</h2>

      {message && <div className="success-message">{message}</div>}
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="label">Service Type</label>
          <select
            className="input-field"
            value={formData.service_type}
            onChange={(e) => setFormData({ ...formData, service_type: e.target.value })}
            data-testid="service-type-select"
          >
            <option>Residential Repair</option>
            <option>Commercial Management</option>
            <option>Backflow Testing</option>
            <option>New Installation</option>
            <option>System Maintenance</option>
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="label">Preferred Date</label>
            <input
              type="date"
              className="input-field"
              value={formData.preferred_date}
              onChange={(e) => setFormData({ ...formData, preferred_date: e.target.value })}
              required
              data-testid="preferred-date-input"
            />
          </div>

          <div className="form-group">
            <label className="label">Preferred Time</label>
            <select
              className="input-field"
              value={formData.preferred_time}
              onChange={(e) => setFormData({ ...formData, preferred_time: e.target.value })}
              data-testid="preferred-time-select"
            >
              <option>9AM-11AM</option>
              <option>11AM-1PM</option>
              <option>1PM-3PM</option>
              <option>3PM-5PM</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="label">Service Description</label>
          <textarea
            className="input-field"
            rows="4"
            placeholder="Describe the issue or service needed..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
            data-testid="description-textarea"
          ></textarea>
        </div>

        <button
          type="submit"
          className="btn-primary full-width"
          disabled={loading}
          data-testid="schedule-button"
        >
          {loading ? 'Scheduling...' : 'Schedule Appointment'}
        </button>
      </form>
    </div>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/auth/verify" element={<VerifyPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;