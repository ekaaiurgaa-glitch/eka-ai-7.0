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
