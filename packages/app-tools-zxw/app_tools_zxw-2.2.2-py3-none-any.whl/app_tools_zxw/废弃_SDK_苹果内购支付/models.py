"""
# File       : models.py
# Time       ：2025/7/28 03:39
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app_tools_zxw.models_payment import PaymentMethod, OrderStatus


class SubscriptionTransactionInfo(BaseModel):
    """订阅交易信息"""
    transaction_id: str = Field(..., description="交易ID")
    original_transaction_id: str = Field(..., description="原始交易ID")
    product_id: str = Field(..., description="产品ID")
    purchase_date: Optional[str] = Field(None, description="购买日期")
    purchase_date_ms: Optional[str] = Field(None, description="购买日期毫秒时间戳")
    expires_date: Optional[str] = Field(None, description="过期日期")
    expires_date_ms: Optional[str] = Field(None, description="过期日期毫秒时间戳")
    web_order_line_item_id: Optional[str] = Field(None, description="网页订单行项目ID")
    is_trial_period: Optional[str] = Field(None, description="是否试用期")
    is_in_intro_offer_period: Optional[str] = Field(None, description="是否在介绍性优惠期")
    is_upgraded: Optional[str] = Field(None, description="是否已升级")
    cancellation_date: Optional[str] = Field(None, description="取消日期")
    cancellation_date_ms: Optional[str] = Field(None, description="取消日期毫秒时间戳")
    cancellation_reason: Optional[str] = Field(None, description="取消原因")
    promotional_offer_id: Optional[str] = Field(None, description="促销优惠ID")
    subscription_group_identifier: Optional[str] = Field(None, description="订阅组标识符")
    offer_code_ref_name: Optional[str] = Field(None, description="优惠码引用名称")

    class Config:
        # 允许额外字段，增强兼容性
        extra = "allow"


class PendingRenewalInfo(BaseModel):
    """待续费信息"""
    auto_renew_product_id: str = Field(..., description="自动续费产品ID")
    original_transaction_id: str = Field(..., description="原始交易ID")
    product_id: str = Field(..., description="产品ID")
    auto_renew_status: str = Field(..., description="自动续费状态，1=开启，0=关闭")
    is_in_billing_retry_period: Optional[str] = Field(None, description="是否在计费重试期")
    price_consent_status: Optional[str] = Field(None, description="价格同意状态")
    grace_period_expires_date: Optional[str] = Field(None, description="宽限期过期日期")
    grace_period_expires_date_ms: Optional[str] = Field(None, description="宽限期过期日期毫秒时间戳")
    promotional_offer_id: Optional[str] = Field(None, description="促销优惠ID")
    offer_code_ref_name: Optional[str] = Field(None, description="优惠码引用名称")
    expiration_intent: Optional[str] = Field(None, description="过期意图")

    class Config:
        # 允许额外字段，增强兼容性
        extra = "allow"


class SubscriptionStatus(BaseModel):
    """订阅状态详细信息"""
    环境: str = Field(..., description="验证环境，Sandbox或Production")
    最新收据: Optional[str] = Field(None, description="最新收据数据")
    最新交易信息: List[SubscriptionTransactionInfo] = Field(default_factory=list, description="最新交易信息列表")
    待续费信息: List[PendingRenewalInfo] = Field(default_factory=list, description="待续费信息列表")

    # 便于理解的订阅状态字段
    是否有效订阅: bool = Field(False, description="当前是否有有效订阅")
    订阅状态: str = Field("unknown", description="订阅状态：active/expired/cancelled/trial/grace_period/billing_retry")
    过期时间: Optional[datetime] = Field(None, description="订阅过期时间")
    自动续费状态: bool = Field(False, description="是否开启自动续费")
    是否试用期: bool = Field(False, description="是否在试用期")
    是否宽限期: bool = Field(False, description="是否在宽限期")
    是否计费重试期: bool = Field(False, description="是否在计费重试期")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApplePaymentResult(BaseModel):
    商户订单号: str = Field(..., title="商户订单号", description="transaction_id")
    支付平台交易号: str = Field(..., title="支付平台交易号", description="Apple transaction_id")
    原始交易号: str = Field(..., title="原始交易号", description="original_transaction_id")
    产品ID: str = Field(..., title="产品ID", description="product_id")
    商品数量: Optional[str] = Field(None, title="商品数量", description="quantity")
    交易金额: Optional[float] = Field(None, title="交易金额", description="amount，苹果不直接提供")
    交易状态: OrderStatus
    支付时间: Optional[datetime] = Field(None, title="支付时间", description="purchase_date")
    支付时间戳: Optional[str] = Field(None, title="支付时间戳", description="purchase_date_ms")
    支付时间PST: Optional[datetime] = Field(None, title="支付时间PST", description="purchase_date_pst")
    原始购买时间: Optional[datetime] = Field(None, title="原始购买时间", description="original_purchase_date")
    原始购买时间戳: Optional[str] = Field(None, title="原始购买时间戳", description="original_purchase_date_ms")
    原始购买时间PST: Optional[datetime] = Field(None, title="原始购买时间PST", description="original_purchase_date_pst")
    过期时间: Optional[datetime] = Field(None, title="过期时间", description="expires_date，仅订阅")
    过期时间戳: Optional[str] = Field(None, title="过期时间戳", description="expires_date_ms，仅订阅")
    过期时间PST: Optional[datetime] = Field(None, title="过期时间PST", description="expires_date_pst，仅订阅")
    网页订单行项目ID: Optional[str] = Field(None, title="网页订单行项目ID", description="web_order_line_item_id")
    支付方式: PaymentMethod = PaymentMethod.APPLE_PAY
    验证环境: str = Field(..., title="验证环境", description="Sandbox或Production")
    是否试用期: Optional[bool] = Field(None, title="是否试用期", description="is_trial_period")
    是否介绍性优惠期: Optional[bool] = Field(None, title="是否在介绍性优惠期", description="is_in_intro_offer_period")
    是否已退款: bool = Field(False, title="是否已退款", description="是否已申请退款")
    退款时间: Optional[datetime] = Field(None, title="退款时间", description="cancellation_date")
    退款原因: Optional[str] = Field(None, title="退款原因", description="cancellation_reason")
    备注: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
