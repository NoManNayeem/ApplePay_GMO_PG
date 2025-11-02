'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface ConfigStatus {
  all_valid: boolean;
  gmo_pg: {
    valid: boolean;
    errors: string[];
    warnings: string[];
    configured: {
      shop_id_set: boolean;
      shop_pass_set: boolean;
      api_endpoint: string;
    };
  };
  apple_pay: {
    valid: boolean;
    errors: string[];
    warnings: string[];
    configured: {
      merchant_id_set: boolean;
    };
  };
  setup_guide: {
    gmo_pg: string;
    apple_pay: string;
    env_file: string;
  };
}

export default function ConfigStatus() {
  const [status, setStatus] = useState<ConfigStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkConfig = async () => {
      try {
        const configStatus = await api.getConfigStatus();
        setStatus(configStatus);
      } catch (err: any) {
        setError(err.message || 'Failed to check configuration');
      } finally {
        setLoading(false);
      }
    };

    checkConfig();
  }, []);

  if (loading) {
    return (
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="spinner" />
          <span className="text-blue-700 dark:text-blue-300">Checking configuration...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-red-800 dark:text-red-200 mb-1">
              Configuration Check Failed
            </h4>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-2">
              Ensure the backend is running and accessible at {process.env.NEXT_PUBLIC_API_URL || 'backend URL'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!status) return null;

  const allValid = status.all_valid;

  return (
    <div className={`border rounded-lg p-4 mb-6 ${
      allValid 
        ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' 
        : 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
    }`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {allValid ? (
            <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>
        <div className="flex-1">
          <h3 className={`font-semibold mb-2 ${
            allValid 
              ? 'text-green-800 dark:text-green-200' 
              : 'text-amber-800 dark:text-amber-200'
          }`}>
            {allValid ? '✅ Configuration Complete' : '⚠️ Configuration Incomplete'}
          </h3>

          {/* GMO PG Status */}
          <div className="mb-3">
            <h4 className="font-medium text-sm mb-1">GMO Payment Gateway:</h4>
            {status.gmo_pg.valid ? (
              <div className="text-sm text-green-700 dark:text-green-300">
                ✓ Configured (Endpoint: {status.gmo_pg.configured.api_endpoint})
              </div>
            ) : (
              <div className="text-sm">
                {status.gmo_pg.errors.map((err, idx) => (
                  <div key={idx} className="text-red-700 dark:text-red-300 mb-1">
                    ✗ {err}
                  </div>
                ))}
              </div>
            )}
            {status.gmo_pg.warnings.map((warn, idx) => (
              <div key={idx} className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                ℹ️ {warn}
              </div>
            ))}
          </div>

          {/* Apple Pay Status */}
          <div className="mb-3">
            <h4 className="font-medium text-sm mb-1">Apple Pay:</h4>
            {status.apple_pay.valid ? (
              <div className="text-sm text-green-700 dark:text-green-300">
                ✓ Merchant ID configured
              </div>
            ) : (
              <div className="text-sm">
                {status.apple_pay.errors.map((err, idx) => (
                  <div key={idx} className="text-red-700 dark:text-red-300 mb-1">
                    ✗ {err}
                  </div>
                ))}
              </div>
            )}
            {status.apple_pay.warnings.map((warn, idx) => (
              <div key={idx} className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                ℹ️ {warn}
              </div>
            ))}
          </div>

          {!allValid && (
            <div className="mt-3 pt-3 border-t border-amber-200 dark:border-amber-700">
              <p className="text-xs text-amber-700 dark:text-amber-300 mb-2">
                <strong>Setup Instructions:</strong>
              </p>
              <ul className="text-xs text-amber-700 dark:text-amber-300 list-disc list-inside space-y-1">
                <li>{status.setup_guide.env_file}</li>
                <li>{status.setup_guide.gmo_pg}</li>
                <li>{status.setup_guide.apple_pay}</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

