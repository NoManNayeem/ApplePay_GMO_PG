'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ApplePayButton from '@/components/ApplePayButton';

export default function RecurringPaymentPage() {
  const router = useRouter();
  const [amount, setAmount] = useState<string>('1000');
  const [currency, setCurrency] = useState<string>('JPY');
  const [billingCycle, setBillingCycle] = useState<string>('monthly');
  const [status, setStatus] = useState<string>('');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');

  const handleSuccess = (result: any) => {
    setStatus('success');
    setResult(result);
    setError('');
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

  const getBillingCycleLabel = (cycle: string) => {
    const labels: Record<string, string> = {
      monthly: 'Monthly',
      yearly: 'Yearly',
      weekly: 'Weekly',
      daily: 'Daily',
    };
    return labels[cycle] || cycle;
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
            Recurring Payment / Subscription
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Set up a recurring payment subscription using Apple Pay
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          {/* Subscription Form Card */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-6 fade-in">
            <div className="space-y-6">
              {/* Amount Input */}
              <div>
                <label htmlFor="amount" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Amount per billing cycle
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

              {/* Billing Cycle Select */}
              <div>
                <label htmlFor="billingCycle" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Billing Cycle
                </label>
                <select
                  id="billingCycle"
                  value={billingCycle}
                  onChange={(e) => setBillingCycle(e.target.value)}
                  className="w-full px-4 py-3 text-lg border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white transition-all bg-white"
                >
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                  <option value="weekly">Weekly</option>
                  <option value="daily">Daily</option>
                </select>
              </div>

              {/* Subscription Summary */}
              {amount && parseFloat(amount) > 0 && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
                  <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Subscription Summary
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600 dark:text-gray-400">Billing Amount:</span>
                      <span className="text-2xl font-bold text-blue-900 dark:text-blue-200">
                        {formatCurrency(parseFloat(amount), currency)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Billing Frequency:</span>
                      <span className="font-semibold text-gray-900 dark:text-white">
                        {getBillingCycleLabel(billingCycle)}
                      </span>
                    </div>
                    <div className="pt-2 border-t border-blue-200 dark:border-blue-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        You will be charged {formatCurrency(parseFloat(amount), currency)} {billingCycle === 'monthly' ? 'per month' : billingCycle === 'yearly' ? 'per year' : `per ${billingCycle}`}.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Apple Pay Button */}
              <div className="pt-4">
                <ApplePayButton
                  amount={parseFloat(amount) || 0}
                  currency={currency}
                  label="Subscription Payment"
                  onSuccess={handleSuccess}
                  onError={handleError}
                  recurring={true}
                  billingCycle={billingCycle}
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
                    <h3 className="text-xl font-bold text-green-800 dark:text-green-200 mb-3">
                      Subscription Created Successfully! ✅
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Subscription ID:</span>
                        <span className="font-mono text-gray-900 dark:text-white">{result.subscription_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Amount:</span>
                        <span className="font-semibold text-gray-900 dark:text-white">
                          {formatCurrency(parseFloat(result.amount || amount), currency)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Billing Cycle:</span>
                        <span className="font-semibold text-gray-900 dark:text-white capitalize">
                          {result.billing_cycle || billingCycle}
                        </span>
                      </div>
                      {result.next_billing_date && (
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Next Billing Date:</span>
                          <span className="text-gray-900 dark:text-white">
                            {new Date(result.next_billing_date).toLocaleDateString()}
                          </span>
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
                      Subscription Setup Failed
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
