import { useState, useEffect, useCallback } from 'react';
import { SUBSCRIPTION_PLANS } from './SubscriptionConstants';
import { SubscriptionContext } from './SubscriptionContextObject';

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
            // Mock data for demonstration
            const mockSubscription = {
                id: 'sub_123',
                plan_id: 'free',
                status: 'active',
                billing_cycle_start: new Date().toISOString().split('T')[0],
                billing_cycle_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                auto_renew: true,
            };

            const mockUsage = {
                tenant_id: 'tenant_123',
                billing_cycle_start: mockSubscription.billing_cycle_start,
                total_tokens_consumed: 6500,
                total_operator_actions: 12,
                total_job_cards_created: 15,
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
            return { allowed: true };
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

    // Increment usage
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
            case 'chat': {
                const tokenCheck = checkTokenLimit();
                if (!tokenCheck.allowed) {
                    return { allowed: false, reason: 'Token limit reached', upgrade: true };
                }
                if (tokenCheck.isNearLimit) {
                    return { allowed: true, warning: `Token usage at ${tokenCheck.percentUsed.toFixed(0)}%`, upgrade: true };
                }
                return { allowed: true };
            }

            case 'operator_action': {
                if (!hasFeature('operator_ai')) {
                    return { allowed: false, reason: 'Operator AI is a premium feature', upgrade: true };
                }
                const actionCheck = checkOperatorActionLimit();
                if (!actionCheck.allowed) {
                    return { allowed: false, reason: 'Daily operator action limit reached', upgrade: true };
                }
                return { allowed: true, remaining: actionCheck.remaining };
            }

            case 'job_card_create': {
                const jobCheck = checkJobCardLimit();
                if (!jobCheck.allowed) {
                    return { allowed: false, reason: 'Monthly job card limit reached', upgrade: true };
                }
                if (jobCheck.isNearLimit) {
                    return { allowed: true, warning: `Job cards at ${jobCheck.percentUsed.toFixed(0)}%`, upgrade: true };
                }
                return { allowed: true, remaining: jobCheck.remaining };
            }

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
