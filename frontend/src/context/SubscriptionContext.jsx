import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api';

// Subscription Plans Configuration (matches backend)
export const SUBSCRIPTION_PLANS = {
    free: {
        id: 'free',
        plan_name: 'Free',
        monthly_price_inr: 0,
        token_limit: 10000, // 10K tokens/month
        operator_actions_per_day: 5,
        job_card_limit_per_month: 20,
        api_requests_per_minute: 10,
        enforcement_policy: 'hard_stop',
        features: {
            chat: true,
            dashboard: true,
            jobs: true,
            vehicles: true,
            mg_calculator: false, // Premium feature
            analytics: false, // Premium feature
            operator_ai: false, // Premium feature
            approvals: false, // Premium feature
            api_access: false,
            custom_integrations: false,
            priority_support: false,
        },
        description: 'Perfect for small workshops getting started',
    },
    starter: {
        id: 'starter',
        plan_name: 'Starter',
        monthly_price_inr: 1999,
        token_limit: 100000, // 100K tokens/month
        operator_actions_per_day: 50,
        job_card_limit_per_month: 200,
        api_requests_per_minute: 30,
        enforcement_policy: 'soft_limit',
        features: {
            chat: true,
            dashboard: true,
            jobs: true,
            vehicles: true,
            mg_calculator: true,
            analytics: true,
            operator_ai: true,
            approvals: true,
            api_access: false,
            custom_integrations: false,
            priority_support: false,
        },
        description: 'For growing workshops with moderate AI needs',
    },
    professional: {
        id: 'professional',
        plan_name: 'Professional',
        monthly_price_inr: 4999,
        token_limit: 500000, // 500K tokens/month
        operator_actions_per_day: 200,
        job_card_limit_per_month: 1000,
        api_requests_per_minute: 60,
        enforcement_policy: 'overage_billing',
        overage_rate_per_1k_tokens: 10, // ₹10 per 1000 tokens over
        features: {
            chat: true,
            dashboard: true,
            jobs: true,
            vehicles: true,
            mg_calculator: true,
            analytics: true,
            operator_ai: true,
            approvals: true,
            api_access: true,
            custom_integrations: false,
            priority_support: true,
        },
        description: 'For multi-branch workshops with high volume',
    },
    enterprise: {
        id: 'enterprise',
        plan_name: 'Enterprise',
        monthly_price_inr: 14999,
        token_limit: null, // Unlimited
        operator_actions_per_day: null, // Unlimited
        job_card_limit_per_month: null, // Unlimited
        api_requests_per_minute: 120,
        enforcement_policy: 'grace_period',
        features: {
            chat: true,
            dashboard: true,
            jobs: true,
            vehicles: true,
            mg_calculator: true,
            analytics: true,
            operator_ai: true,
            approvals: true,
            api_access: true,
            custom_integrations: true,
            priority_support: true,
        },
        description: 'Unlimited everything with custom SLAs',
    },
};

// Feature labels for UI
export const FEATURE_LABELS = {
    chat: 'EKA Intelligence Chat',
    dashboard: 'Dashboard & Analytics',
    jobs: 'Job Card Management',
    vehicles: 'Vehicle Registry',
    mg_calculator: 'MG Engine Calculator',
    analytics: 'Advanced Analytics',
    operator_ai: 'Operator AI Actions',
    approvals: 'Approval Workflows',
    api_access: 'API Access',
    custom_integrations: 'Custom Integrations',
    priority_support: 'Priority Support',
};

const SubscriptionContext = createContext(null);

export function SubscriptionProvider({ children }) {
    const [subscription, setSubscription] = useState(null);
    const [usage, setUsage] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Get current plan details
    const currentPlan = subscription ? SUBSCRIPTION_PLANS[subscription.plan_id] : SUBSCRIPTION_PLANS.free;

    // Fetch subscription and usage data
    const refreshSubscription = useCallback(async () => {
        try {
            setLoading(true);
            // In a real app, these would be actual API calls
            // const subData = await api.getSubscription();
            // const usageData = await api.getUsage();
            
            // Mock data for demonstration
            const mockSubscription = {
                id: 'sub_123',
                plan_id: 'free', // Change to test different plans
                status: 'active',
                billing_cycle_start: new Date().toISOString().split('T')[0],
                billing_cycle_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                auto_renew: true,
            };
            
            const mockUsage = {
                tenant_id: 'tenant_123',
                billing_cycle_start: mockSubscription.billing_cycle_start,
                total_tokens_consumed: 6500, // Mock: 65% of free tier
                total_operator_actions: 12, // Mock: 2 days worth for free tier
                total_job_cards_created: 15, // Mock: 15 of 20 free tier
                total_api_requests: 245,
                total_mg_calculations: 0,
                last_updated: new Date().toISOString(),
            };
            
            setSubscription(mockSubscription);
            setUsage(mockUsage);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshSubscription();
    }, [refreshSubscription]);

    // Check if feature is available
    const hasFeature = (featureName) => {
        if (!currentPlan) return false;
        return currentPlan.features[featureName] === true;
    };

    // Check if limit is reached
    const checkLimit = (limitType, currentValue) => {
        if (!currentPlan) return { allowed: false, reason: 'No plan' };
        
        const limit = currentPlan[limitType];
        if (limit === null || limit === undefined) {
            return { allowed: true }; // Unlimited
        }
        
        const remaining = limit - currentValue;
        const percentUsed = (currentValue / limit) * 100;
        
        return {
            allowed: currentValue < limit,
            limit,
            current: currentValue,
            remaining: Math.max(0, remaining),
            percentUsed,
            isNearLimit: percentUsed >= 80,
            isAtLimit: percentUsed >= 100,
        };
    };

    // Check specific usage limits
    const checkTokenLimit = () => {
        if (!usage) return { allowed: true };
        return checkLimit('token_limit', usage.total_tokens_consumed);
    };

    const checkOperatorActionLimit = () => {
        if (!usage) return { allowed: true };
        return checkLimit('operator_actions_per_day', usage.total_operator_actions);
    };

    const checkJobCardLimit = () => {
        if (!usage) return { allowed: true };
        return checkLimit('job_card_limit_per_month', usage.total_job_cards_created);
    };

    // Increment usage (called after actions)
    const incrementUsage = useCallback((type, amount = 1) => {
        setUsage(prev => {
            if (!prev) return null;
            return {
                ...prev,
                [`total_${type}`]: (prev[`total_${type}`] || 0) + amount,
                last_updated: new Date().toISOString(),
            };
        });
    }, []);

    // Check if user can perform an action
    const canPerformAction = (actionType) => {
        switch (actionType) {
            case 'chat':
                const tokenCheck = checkTokenLimit();
                if (!tokenCheck.allowed) {
                    return { allowed: false, reason: 'Token limit reached', upgrade: true };
                }
                if (tokenCheck.isNearLimit) {
                    return { allowed: true, warning: `Token usage at ${tokenCheck.percentUsed.toFixed(0)}%`, upgrade: true };
                }
                return { allowed: true };
                
            case 'operator_action':
                if (!hasFeature('operator_ai')) {
                    return { allowed: false, reason: 'Operator AI is a premium feature', upgrade: true };
                }
                const actionCheck = checkOperatorActionLimit();
                if (!actionCheck.allowed) {
                    return { allowed: false, reason: 'Daily operator action limit reached', upgrade: true };
                }
                return { allowed: true, remaining: actionCheck.remaining };
                
            case 'job_card_create':
                const jobCheck = checkJobCardLimit();
                if (!jobCheck.allowed) {
                    return { allowed: false, reason: 'Monthly job card limit reached', upgrade: true };
                }
                if (jobCheck.isNearLimit) {
                    return { allowed: true, warning: `Job cards at ${jobCheck.percentUsed.toFixed(0)}%`, upgrade: true };
                }
                return { allowed: true, remaining: jobCheck.remaining };
                
            case 'mg_calculate':
                if (!hasFeature('mg_calculator')) {
                    return { allowed: false, reason: 'MG Calculator is a premium feature', upgrade: true };
                }
                return { allowed: true };
                
            case 'analytics':
                if (!hasFeature('analytics')) {
                    return { allowed: false, reason: 'Analytics is a premium feature', upgrade: true };
                }
                return { allowed: true };
                
            case 'approvals':
                if (!hasFeature('approvals')) {
                    return { allowed: false, reason: 'Approval workflows are a premium feature', upgrade: true };
                }
                return { allowed: true };
                
            default:
                return { allowed: true };
        }
    };

    // Get usage display data
    const getUsageDisplay = () => {
        if (!usage || !currentPlan) return [];
        
        return [
            {
                label: 'AI Tokens',
                current: usage.total_tokens_consumed,
                limit: currentPlan.token_limit,
                unit: 'tokens',
                percent: currentPlan.token_limit ? (usage.total_tokens_consumed / currentPlan.token_limit) * 100 : 0,
                icon: '💬',
            },
            {
                label: 'Operator Actions',
                current: usage.total_operator_actions,
                limit: currentPlan.operator_actions_per_day,
                unit: 'actions/day',
                percent: currentPlan.operator_actions_per_day ? (usage.total_operator_actions / currentPlan.operator_actions_per_day) * 100 : 0,
                icon: '⚡',
            },
            {
                label: 'Job Cards',
                current: usage.total_job_cards_created,
                limit: currentPlan.job_card_limit_per_month,
                unit: 'jobs/month',
                percent: currentPlan.job_card_limit_per_month ? (usage.total_job_cards_created / currentPlan.job_card_limit_per_month) * 100 : 0,
                icon: '📋',
            },
        ];
    };

    const value = {
        subscription,
        usage,
        currentPlan,
        loading,
        error,
        hasFeature,
        canPerformAction,
        checkTokenLimit,
        checkOperatorActionLimit,
        checkJobCardLimit,
        incrementUsage,
        getUsageDisplay,
        refreshSubscription,
        isFree: currentPlan?.id === 'free',
        isPaid: currentPlan?.id !== 'free',
    };

    return (
        <SubscriptionContext.Provider value={value}>
            {children}
        </SubscriptionContext.Provider>
    );
}

export const useSubscription = () => {
    const context = useContext(SubscriptionContext);
    if (!context) {
        throw new Error('useSubscription must be used within a SubscriptionProvider');
    }
    return context;
};
