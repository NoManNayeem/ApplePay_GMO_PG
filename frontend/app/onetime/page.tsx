'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ApplePayButton from '@/components/ApplePayButton';

export default function OneTimePaymentPage() {
  const router = useRouter();
  const [amount, setAmount] = useState<string>('1000');
  const [currency, setCurrency] = useState<string>('JPY');
  const [status, setStatus] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSuccess = (result: any) => {
    setStatus('success');
    setResult(result);
    setError('');
    // Scroll to result
    setTimeout(() => {
      document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleError = (errorMessage: string) => {
    setStatus('error');
    setError(errorMessage);
    setResult(null);
    setTimeout(() => {
      document.getElementById('result')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const formatCurrency = (value: number, curr: string) => {
    if (curr === 'JPY') {
      return `¥${value.toLocaleString('ja-JP')}`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: curr,
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 slide-in">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 mb-4 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Home
          </button>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            One-Time Payment
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Test a single Apple Pay transaction using GMO Payment Gateway
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          {/* Payment Form Card */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-6 fade-in">
            <div className="space-y-6">
              {/* Amount Input */}
              <div>
                <label htmlFor="amount" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Payment Amount
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="amount"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-4 py-3 text-lg border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all"
                    placeholder="Enter amount"
                    min="1"
                    step="0.01"
                  />
                  {amount && parseFloat(amount) > 0 && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 font-medium">
                      {formatCurrency(parseFloat(amount), currency)}
                    </div>
                  )}
                </div>
              </div>

              {/* Currency Select */}
              <div>
                <label htmlFor="currency" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Currency
                </label>
                <select
                  id="currency"
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all bg-white"
                >
                  <option value="JPY">JPY (Japanese Yen)</option>
                  <option value="USD">USD (US Dollar)</option>
                  <option value="EUR">EUR (Euro)</option>
                </select>
              </div>

              {/* Payment Summary */}
              {amount && parseFloat(amount) > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-6 border-2 border-gray-200 dark:border-gray-600">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600 dark:text-gray-400">Amount</span>
                    <span className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatCurrency(parseFloat(amount), currency)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    This is a test transaction. No real payment will be processed.
                  </div>
                </div>
              )}

              {/* Apple Pay Button */}
              <div className="pt-4">
                <ApplePayButton
                  amount={parseFloat(amount) || 0}
                  currency={currency}
                  label="Test Payment"
                  onSuccess={handleSuccess}
                  onError={handleError}
                />
              </div>
            </div>
          </div>

          {/* Results */}
          <div id="result" className="fade-in">
            {status === 'success' && result && (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6 border-2 border-green-200 dark:border-green-800">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-green-800 dark:text-green-200 mb-2">
                      Payment Successful! ✅
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Transaction ID:</span>
                        <span className="font-mono text-gray-900 dark:text-white">{result.transaction_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Amount:</span>
                        <span className="font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(parseFloat(result.amount || amount), currency)}
                        </span>
                      </div>
                      {result.gmo_order_id && (
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Order ID:</span>
                          <span className="font-mono text-gray-900 dark:text-white text-xs">{result.gmo_order_id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {status === 'error' && error && (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 border-2 border-red-200 dark:border-red-800">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-red-800 dark:text-red-200 mb-2">
                      Payment Failed
                    </h3>
                    <p className="text-red-700 dark:text-red-300">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
