"""
苹果应用服务 SDK
包含苹果内购验证和促销优惠管理功能
"""

# 苹果内购服务
from .sdk_支付验证 import 苹果内购支付服务_官方库, 苹果内购支付服务

# 促销优惠管理服务
from .sdk_促销优惠管理 import (
    苹果内购优惠管理服务,
    Model促销优惠签名请求,
    Model促销优惠签名结果
)

# 数据模型
from .models import (
    ApplePaymentResult,
    SubscriptionStatus,
    SubscriptionTransactionInfo,
    PendingRenewalInfo,
    ApplePaymentMapper
)

__all__ = [
    # 苹果内购服务
    '苹果内购支付服务_官方库',
    '苹果内购支付服务',

    # 促销优惠管理
    '苹果内购优惠管理服务',
    'Model促销优惠签名请求',
    'Model促销优惠签名结果',

    # 数据模型
    'ApplePaymentResult',
    'SubscriptionStatus',
    'SubscriptionTransactionInfo',
    'PendingRenewalInfo',
    'ApplePaymentMapper'
]
