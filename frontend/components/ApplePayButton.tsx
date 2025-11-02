'use client';

import { useEffect, useRef, useState } from 'react';
import { api } from '@/lib/api';

declare global {
  interface Window {
    ApplePaySession?: any;
  }
}

interface ApplePayButtonProps {
  amount: number;
  currency?: string;
  label?: string;
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
  recurring?: boolean;
  billingCycle?: string;
}

export default function ApplePayButton({
  amount,
  currency = 'JPY',
  label = 'Pay',
  onSuccess,
  onError,
  recurring = false,
  billingCycle = 'monthly',
}: ApplePayButtonProps) {
  const [isApplePayAvailable, setIsApplePayAvailable] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const buttonRef = useRef<HTMLDivElement>(null);
  const sessionRef = useRef<any>(null);

  useEffect(() => {
    // Check if Apple Pay is available
    if (typeof window !== 'undefined' && window.ApplePaySession) {
      const canMakePayments = window.ApplePaySession.canMakePayments();
      setIsApplePayAvailable(canMakePayments);
    }
  }, []);

  const handlePaymentClick = () => {
    // CRITICAL: Apple Pay session must be created synchronously within user gesture handler
    // Any async operations must happen AFTER session creation, in event handlers
    if (isProcessing || parseFloat(amount.toString()) <= 0) {
      return;
    }

    if (!window.ApplePaySession) {
      onError?.('Apple Pay is not available');
      return;
    }

    setIsProcessing(true);

    try {
      // Create payment request object (synchronous)
      const paymentRequest = {
        countryCode: 'JP',
        currencyCode: currency,
        merchantCapabilities: ['supports3DS'],
        supportedNetworks: ['visa', 'masterCard', 'amex', 'discover'],
        total: {
          label: label,
          amount: amount.toString(),
          type: 'final',
        },
      };

      // Add recurring payment info if applicable
      // According to 2025 Apple Pay documentation, recurringPaymentRequestItem should be used
      if (recurring) {
        // Apple Pay JS API version 3+ supports recurringPaymentRequestItem
        // This requires specific structure per Apple's 2025 documentation
        (paymentRequest as any).recurringPaymentRequestItem = {
          paymentDescription: `Recurring ${label}`,
          regularBilling: {
            amount: amount.toString(),
            label: label,
            intervalUnit: billingCycle === 'monthly' ? 'month' : 'year',
            intervalCount: 1,
          },
        };
      }

      // CRITICAL: Create Apple Pay session IMMEDIATELY (synchronously) within user gesture handler
      // Do NOT await anything before this line
      const session = new window.ApplePaySession(3, paymentRequest);
      sessionRef.current = session;

      // Handle merchant validation (async operations happen here)
      session.onvalidatemerchant = async (event: any) => {
        try {
          // Extract validation URL from the event (required by Apple Pay)
          const validationURL = event.validationURL;
          
          if (!validationURL) {
            console.error('[Apple Pay] Missing validationURL in event:', event);
            session.abort();
            setIsProcessing(false);
            onError?.('Invalid merchant validation request');
            return;
          }

          console.log('[Apple Pay] Validating merchant with URL:', validationURL);

          // Send validation URL to backend to get merchant session
          // The backend should validate with Apple's servers and return merchant session
          const validationResponse = await api.validateMerchantSession(validationURL);
          
          if (validationResponse && validationResponse.merchantSession) {
            // Complete merchant validation with the merchant session from backend
            // The merchantSession should be a JSON string containing the validated session
            session.completeMerchantValidation(validationResponse.merchantSession);
          } else {
            console.error('[Apple Pay] Merchant validation failed:', validationResponse);
            session.abort();
            setIsProcessing(false);
            onError?.(validationResponse?.error || 'Merchant validation failed');
          }
        } catch (error: any) {
          console.error('[Apple Pay] Merchant validation error:', error);
          session.abort();
          setIsProcessing(false);
          onError?.(error.message || 'Merchant validation error');
        }
      };

      // Handle payment authorization
      session.onpaymentauthorized = async (event: any) => {
        try {
          const paymentToken = event.payment.token;

          // Send payment token to backend for processing
          if (recurring) {
            const result = await api.setupRecurringPayment({
              token: JSON.stringify(paymentToken),
              amount: amount,
              currency: currency,
              billing_cycle: billingCycle,
            });

            if (result.status === 'active') {
              session.completePayment(window.ApplePaySession.STATUS_SUCCESS);
              setIsProcessing(false);
              onSuccess?.(result);
            } else {
              session.completePayment(window.ApplePaySession.STATUS_FAILURE);
              setIsProcessing(false);
              onError?.(result.error || 'Payment failed');
            }
          } else {
            const result = await api.processOneTimePayment({
              token: JSON.stringify(paymentToken),
              amount: amount,
              currency: currency,
            });

            if (result.status === 'completed') {
              session.completePayment(window.ApplePaySession.STATUS_SUCCESS);
              setIsProcessing(false);
              onSuccess?.(result);
            } else {
              session.completePayment(window.ApplePaySession.STATUS_FAILURE);
              setIsProcessing(false);
              onError?.(result.error || 'Payment failed');
            }
          }
        } catch (error: any) {
          session.completePayment(window.ApplePaySession.STATUS_FAILURE);
          setIsProcessing(false);
          onError?.(error.message || 'Payment processing error');
        }
      };

      // Handle cancellation
      session.oncancel = () => {
        setIsProcessing(false);
        onError?.('Payment cancelled');
      };

      // Start the session (must be called synchronously after creation)
      session.begin();
    } catch (error: any) {
      setIsProcessing(false);
      onError?.(error.message || 'Failed to initialize Apple Pay');
    }
  };

  if (!isApplePayAvailable) {
    return (
      <div className="fade-in">
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-4">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-200 mb-1">
                Apple Pay Not Available
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-300">
                Apple Pay is not available on this device or browser. Please use Safari on macOS or iOS to test Apple Pay.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={buttonRef} className="fade-in">
      {/* Official Apple Pay Button */}
      <button
        onClick={handlePaymentClick}
        disabled={isProcessing || parseFloat(amount.toString()) <= 0}
        className="apple-pay-button apple-pay-button-black"
        style={{
          width: '100%',
          maxWidth: '500px',
          minHeight: '44px',
          cursor: isProcessing ? 'wait' : 'pointer',
          opacity: isProcessing ? 0.7 : 1,
        }}
        aria-label="Pay with Apple Pay"
      >
        {isProcessing && (
          <style dangerouslySetInnerHTML={{
            __html: `
              .apple-pay-button::before {
                content: '';
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255,255,255,0.3);
                border-top-color: #fff;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-right: 8px;
              }
            `
          }} />
        )}
      </button>
      
      {/* Fallback for browsers that don't support -webkit-appearance */}
      <style dangerouslySetInnerHTML={{
        __html: `
          @supports not (-webkit-appearance: -apple-pay-button) {
            .apple-pay-button {
              display: none;
            }
            .apple-pay-button-fallback {
              display: inline-flex;
            }
          }
        `
      }} />
      
      <button
        onClick={handlePaymentClick}
        disabled={isProcessing || parseFloat(amount.toString()) <= 0}
        className="apple-pay-button-fallback"
        style={{ display: 'none' }}
        aria-label="Pay with Apple Pay"
      >
        {isProcessing ? (
          <>
            <div className="spinner" />
            <span>Processing...</span>
          </>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.96-3.24-1.44-1.41-.62-2.17-1.11-2.94-1.11-.36 0-.71.07-1.05.24l-1.07.49c-.28.13-.57.18-.85.18-.55 0-1.05-.22-1.49-.64-.88-.84-1.44-2.05-1.44-3.47 0-1.91 1.39-4.02 3.41-5.99 1.82-1.79 3.86-2.73 6.12-2.73 1.52 0 2.85.51 3.97 1.52.85.77 1.52 1.74 1.99 2.92l-2.86 1.25c-.36-.87-.89-1.6-1.58-2.16-.71-.57-1.63-.87-2.7-.87-1.66 0-2.95.71-3.87 2.13-.86 1.33-1.29 3.02-1.29 5.07 0 .81.07 1.5.21 2.08.13.55.35.99.66 1.32.29.32.62.48 1.01.48.26 0 .52-.08.77-.23l1.22-.56c.75-.34 1.21-.51 1.7-.51.85 0 1.49.38 1.92 1.14.39.69.58 1.64.58 2.85 0 .82-.14 1.48-.42 1.99zm-1.21-5.01c.13.06.28.09.42.09.45 0 .84-.21 1.15-.63.3-.4.44-.95.44-1.64 0-.9-.18-1.6-.54-2.09-.35-.48-.89-.72-1.61-.72-.23 0-.48.03-.75.09l-1.15.51c-.54.24-.9.36-1.09.36-.15 0-.25-.06-.3-.18-.06-.14-.08-.36-.08-.65 0-.81.15-1.44.43-1.88.27-.44.72-.66 1.35-.66.82 0 1.47.38 1.94 1.15.44.73.66 1.73.66 3.01 0 .47-.03.83-.08 1.08-.06.24-.12.4-.15.46-.05.09-.1.15-.14.18z"/>
            </svg>
            <span>Pay</span>
          </>
        )}
      </button>
    </div>
  );
}

