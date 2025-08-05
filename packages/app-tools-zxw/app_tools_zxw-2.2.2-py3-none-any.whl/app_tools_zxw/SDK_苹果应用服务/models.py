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
    # 基础交易信息
    transaction_id: str = Field(..., description="交易ID")
    original_transaction_id: str = Field(..., description="原始交易ID")
    product_id: str = Field(..., description="产品ID")
    bundle_id: Optional[str] = Field(None, description="应用包ID")

    # 时间相关字段
    purchase_date: Optional[str] = Field(None, description="购买日期")
    purchase_date_ms: Optional[str] = Field(None, description="购买日期毫秒时间戳")
    original_purchase_date: Optional[str] = Field(None, description="原始购买日期")
    original_purchase_date_ms: Optional[str] = Field(None, description="原始购买日期毫秒时间戳")
    expires_date: Optional[str] = Field(None, description="过期日期")
    expires_date_ms: Optional[str] = Field(None, description="过期日期毫秒时间戳")
    signed_date: Optional[str] = Field(None, description="签名日期")
    signed_date_ms: Optional[str] = Field(None, description="签名日期毫秒时间戳")

    # 订单和订阅相关
    web_order_line_item_id: Optional[str] = Field(None, description="网页订单行项目ID")
    subscription_group_identifier: Optional[str] = Field(None, description="订阅组标识符")
    quantity: Optional[int] = Field(None, description="购买数量")

    # 交易类型和状态
    type: Optional[str] = Field(None, description="交易类型，如 Auto-Renewable Subscription")
    in_app_ownership_type: Optional[str] = Field(None, description="应用内所有权类型，如 PURCHASED")
    transaction_reason: Optional[str] = Field(None, description="交易原因，如 RENEWAL")

    # 环境和地区信息
    environment: Optional[str] = Field(None, description="环境，Sandbox 或 Production")
    storefront: Optional[str] = Field(None, description="店面国家代码")
    storefront_id: Optional[str] = Field(None, description="店面ID")

    # 价格信息
    price: Optional[int] = Field(None, description="价格（以货币最小单位表示，如分）")
    currency: Optional[str] = Field(None, description="货币代码，如 CNY, USD")

    # 其他标识符
    app_transaction_id: Optional[str] = Field(None, description="应用交易ID")

    # 试用期和优惠相关
    is_trial_period: Optional[str] = Field(None, description="是否试用期")
    is_in_intro_offer_period: Optional[str] = Field(None, description="是否在介绍性优惠期")
    is_upgraded: Optional[str] = Field(None, description="是否已升级")
    promotional_offer_id: Optional[str] = Field(None, description="促销优惠ID")
    offer_code_ref_name: Optional[str] = Field(None, description="优惠码引用名称")

    # 取消和退款相关
    cancellation_date: Optional[str] = Field(None, description="取消日期")
    cancellation_date_ms: Optional[str] = Field(None, description="取消日期毫秒时间戳")
    cancellation_reason: Optional[str] = Field(None, description="取消原因")
    revocation_date: Optional[str] = Field(None, description="撤销日期（退款）")
    revocation_date_ms: Optional[str] = Field(None, description="撤销日期毫秒时间戳")
    revocation_reason: Optional[str] = Field(None, description="撤销原因")

    class Config:
        # 允许额外字段，增强兼容性
        extra = "allow"

    @classmethod
    def from_transaction_info(cls, transaction_info: dict) -> "SubscriptionTransactionInfo":
        """从苹果官方交易信息字典创建SubscriptionTransactionInfo对象"""
        return cls(
            # 基础交易信息
            transaction_id=transaction_info.get("transactionId", ""),
            original_transaction_id=transaction_info.get("originalTransactionId", ""),
            product_id=transaction_info.get("productId", ""),
            bundle_id=transaction_info.get("bundleId"),

            # 时间相关字段
            purchase_date=ApplePaymentMapper.format_timestamp(transaction_info.get("purchaseDate")),
            purchase_date_ms=str(transaction_info.get("purchaseDate")) if transaction_info.get("purchaseDate") else None,
            original_purchase_date=ApplePaymentMapper.format_timestamp(transaction_info.get("originalPurchaseDate")),
            original_purchase_date_ms=str(transaction_info.get("originalPurchaseDate")) if transaction_info.get("originalPurchaseDate") else None,
            expires_date=ApplePaymentMapper.format_timestamp(transaction_info.get("expiresDate")),
            expires_date_ms=str(transaction_info.get("expiresDate")) if transaction_info.get("expiresDate") else None,
            signed_date=ApplePaymentMapper.format_timestamp(transaction_info.get("signedDate")),
            signed_date_ms=str(transaction_info.get("signedDate")) if transaction_info.get("signedDate") else None,

            # 订单和订阅相关
            web_order_line_item_id=str(transaction_info.get("webOrderLineItemId")) if transaction_info.get("webOrderLineItemId") is not None else None,
            subscription_group_identifier=transaction_info.get("subscriptionGroupIdentifier"),
            quantity=transaction_info.get("quantity"),

            # 交易类型和状态
            type=transaction_info.get("type"),
            in_app_ownership_type=transaction_info.get("inAppOwnershipType"),
            transaction_reason=transaction_info.get("transactionReason"),

            # 环境和地区信息
            environment=transaction_info.get("environment"),
            storefront=transaction_info.get("storefront"),
            storefront_id=transaction_info.get("storefrontId"),

            # 价格信息
            price=transaction_info.get("price"),
            currency=transaction_info.get("currency"),

            # 其他标识符
            app_transaction_id=transaction_info.get("appTransactionId"),

            # 试用期和优惠相关
            is_trial_period=str(transaction_info.get("isTrialPeriod")) if transaction_info.get("isTrialPeriod") is not None else None,
            is_in_intro_offer_period=str(transaction_info.get("isInIntroOfferPeriod")) if transaction_info.get("isInIntroOfferPeriod") is not None else None,
            is_upgraded=str(transaction_info.get("isUpgraded")) if transaction_info.get("isUpgraded") is not None else None,
            promotional_offer_id=transaction_info.get("promotionalOfferId"),
            offer_code_ref_name=transaction_info.get("offerCodeRefName"),

            # 取消和退款相关
            cancellation_date=ApplePaymentMapper.format_timestamp(transaction_info.get("cancellationDate")),
            cancellation_date_ms=str(transaction_info.get("cancellationDate")) if transaction_info.get("cancellationDate") else None,
            cancellation_reason=ApplePaymentMapper.parse_cancellation_reason(transaction_info.get("cancellationReason")),
            revocation_date=ApplePaymentMapper.format_timestamp(transaction_info.get("revocationDate")),
            revocation_date_ms=str(transaction_info.get("revocationDate")) if transaction_info.get("revocationDate") else None,
            revocation_reason=ApplePaymentMapper.parse_revocation_reason(transaction_info.get("revocationReason"))
        )


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

    @classmethod
    def from_renewal_info(cls, renewal_info: dict) -> "PendingRenewalInfo":
        """从苹果官方续费信息字典创建PendingRenewalInfo对象"""
        return cls(
            auto_renew_product_id=renewal_info.get("autoRenewProductId", ""),
            original_transaction_id=renewal_info.get("originalTransactionId", ""),
            product_id=renewal_info.get("productId", ""),
            auto_renew_status=str(renewal_info.get("autoRenewStatus", "0")),
            is_in_billing_retry_period=str(renewal_info.get("isInBillingRetryPeriod")) if renewal_info.get("isInBillingRetryPeriod") is not None else None,
            price_consent_status=str(renewal_info.get("priceConsentStatus")) if renewal_info.get("priceConsentStatus") is not None else None,
            grace_period_expires_date=ApplePaymentMapper.format_timestamp(renewal_info.get("gracePeriodExpiresDate")),
            grace_period_expires_date_ms=str(renewal_info.get("gracePeriodExpiresDate")) if renewal_info.get("gracePeriodExpiresDate") else None,
            promotional_offer_id=renewal_info.get("promotionalOfferId"),
            offer_code_ref_name=renewal_info.get("offerCodeRefName"),
            expiration_intent=str(renewal_info.get("expirationIntent")) if renewal_info.get("expirationIntent") is not None else None
        )


class SubscriptionStatus(BaseModel):
    """订阅状态详细信息"""
    环境: str = Field(..., description="验证环境，Sandbox或Production")
    最新收据: Optional[str] = Field(None, description="最新收据数据")
    最新交易信息: List[SubscriptionTransactionInfo] = Field(default_factory=list, description="最新交易信息列表")
    待续费信息: List[PendingRenewalInfo] = Field(default_factory=list, description="待续费信息列表")

    # 便于理解的订阅状态字段
    是否有效订阅: bool = Field(False, description="当前是否有有效订阅")
    订阅状态: str = Field("unknown", description="订阅状态：active/expired/cancelled/trial/grace_period/billing_retry")
    过期时间: Optional[str] = Field(None, description="订阅过期时间")
    自动续费状态: bool = Field(False, description="是否开启自动续费")
    是否试用期: bool = Field(False, description="是否在试用期")
    是否宽限期: bool = Field(False, description="是否在宽限期")
    是否计费重试期: bool = Field(False, description="是否在计费重试期")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApplePaymentResult(BaseModel):
    """苹果支付结果"""
    商户订单号: str = Field(..., title="商户订单号", description="transaction_id")
    支付平台交易号: str = Field(..., title="支付平台交易号", description="Apple transaction_id")
    原始交易号: str = Field(..., title="原始交易号", description="original_transaction_id")
    产品ID: str = Field(..., title="产品ID", description="product_id")
    交易金额: Optional[float] = Field(None, title="交易金额", description="amount，从 price 字段转换")
    交易状态: OrderStatus
    支付时间: str = Field(..., title="支付时间", description="purchase_date")
    过期时间: Optional[str] = Field(None, title="过期时间", description="expires_date，仅订阅")
    支付方式: PaymentMethod = PaymentMethod.APPLE_PAY
    验证环境: str = Field(..., title="验证环境", description="Sandbox或Production")

    # 新增字段，对应官方返回值
    应用包ID: Optional[str] = Field(None, title="应用包ID", description="bundle_id")
    交易类型: Optional[str] = Field(None, title="交易类型", description="type，如 Auto-Renewable Subscription")
    交易原因: Optional[str] = Field(None, title="交易原因", description="transaction_reason，如 RENEWAL")
    购买数量: Optional[int] = Field(None, title="购买数量", description="quantity")
    货币代码: Optional[str] = Field(None, title="货币代码", description="currency，如 CNY, USD")
    原始价格: Optional[int] = Field(None, title="原始价格", description="price，以货币最小单位表示")
    店面代码: Optional[str] = Field(None, title="店面代码", description="storefront，国家代码")
    应用交易ID: Optional[str] = Field(None, title="应用交易ID", description="app_transaction_id")

    # 试用期和优惠相关
    是否试用期: Optional[bool] = Field(None, title="是否试用期", description="is_trial_period")
    是否介绍性优惠期: Optional[bool] = Field(None, title="是否介绍性优惠期", description="is_in_intro_offer_period")

    # 退款相关
    是否已退款: bool = Field(False, title="是否已退款", description="是否已申请退款")
    退款时间: Optional[str] = Field(None, title="退款时间", description="revocation_date")
    退款原因: Optional[str] = Field(None, title="退款原因", description="revocation_reason")

    备注: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_transaction_info(cls, transaction_info: dict, is_sandbox: bool = True) -> "ApplePaymentResult":
        """从苹果官方交易信息字典创建ApplePaymentResult对象"""
        # 解析交易状态
        交易状态 = ApplePaymentMapper.parse_transaction_status(transaction_info)

        # 检查退款信息
        是否已退款 = bool(transaction_info.get("revocationDate"))
        退款时间 = ApplePaymentMapper.format_timestamp(transaction_info.get("revocationDate"))
        退款原因 = ApplePaymentMapper.parse_revocation_reason(transaction_info.get("revocationReason"))

        # 处理价格信息
        原始价格 = transaction_info.get("price")
        交易金额 = ApplePaymentMapper.convert_price(原始价格, transaction_info.get("currency", "USD"))

        return cls(
            商户订单号=transaction_info.get("transactionId", ""),
            支付平台交易号=transaction_info.get("transactionId", ""),
            原始交易号=transaction_info.get("originalTransactionId", ""),
            产品ID=transaction_info.get("productId", ""),
            交易金额=交易金额,
            交易状态=交易状态,
            支付时间=ApplePaymentMapper.format_timestamp(transaction_info.get("purchaseDate")),
            过期时间=ApplePaymentMapper.format_timestamp(transaction_info.get("expiresDate")),
            验证环境=transaction_info.get("environment", "Sandbox" if is_sandbox else "Production"),

            # 新增的字段映射
            应用包ID=transaction_info.get("bundleId"),
            交易类型=transaction_info.get("type"),
            交易原因=transaction_info.get("transactionReason"),
            购买数量=transaction_info.get("quantity"),
            货币代码=transaction_info.get("currency"),
            原始价格=原始价格,
            店面代码=transaction_info.get("storefront"),
            应用交易ID=transaction_info.get("appTransactionId"),

            # 试用期和优惠相关
            是否试用期=transaction_info.get("isTrialPeriod") == "true" if transaction_info.get("isTrialPeriod") is not None else None,
            是否介绍性优惠期=transaction_info.get("isInIntroOfferPeriod") == "true" if transaction_info.get("isInIntroOfferPeriod") is not None else None,

            # 退款相关
            是否已退款=是否已退款,
            退款时间=退款时间,
            退款原因=退款原因
        )


class ApplePaymentMapper:
    """苹果支付数据映射器 - 统一管理映射逻辑"""

    @staticmethod
    def format_timestamp(timestamp: Optional[str]) -> Optional[str]:
        """格式化时间戳为可读字符串"""
        if not timestamp:
            return None

        try:
            timestamp_ms = int(timestamp)
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return str(timestamp)

    @staticmethod
    def convert_price(price: Optional[int], currency: str = "USD") -> Optional[float]:
        """将价格从最小单位转换为标准货币单位"""
        if price is None:
            return None

        # 大部分货币都是除以100，日元、韩元等例外
        if currency.upper() in ["JPY", "KRW", "VND", "CLP"]:
            return float(price)
        elif currency.upper() == "CNY":
            return float(price) / 1000
        else:
            return float(price) / 100

    @staticmethod
    def parse_transaction_status(transaction_info: dict) -> OrderStatus:
        """解析交易状态"""
        # 检查退款状态
        if transaction_info.get("revocationDate"):
            return OrderStatus.CANCELLED

        # 检查订阅过期状态
        expires_date = transaction_info.get("expiresDate")
        if expires_date:
            try:
                过期时间戳 = int(expires_date) / 1000
                当前时间戳 = datetime.now().timestamp()

                if 当前时间戳 > 过期时间戳:
                    return OrderStatus.FINISHED  # 订阅已过期
                else:
                    return OrderStatus.PAID  # 订阅有效
            except (ValueError, TypeError):
                pass

        # 一次性购买或有效订阅
        return OrderStatus.PAID

    @staticmethod
    def parse_revocation_reason(reason_code: Optional[str]) -> Optional[str]:
        """解析退款原因"""
        if not reason_code:
            return None

        reason_mapping = {
            "1": "应用问题",
            "0": "其他原因"
        }
        return reason_mapping.get(str(reason_code), f"未知原因: {reason_code}")

    @staticmethod
    def parse_cancellation_reason(reason_code: Optional[str]) -> Optional[str]:
        """解析取消原因"""
        if not reason_code:
            return None

        # 可以根据需要扩展取消原因映射
        return f"取消原因: {reason_code}"

    @staticmethod
    def analyze_subscription_status(
        transactions: List[SubscriptionTransactionInfo],
        renewals: List[PendingRenewalInfo]
    ) -> dict:
        """分析订阅状态"""
        result = {
            "是否有效订阅": False,
            "订阅状态": "unknown",
            "过期时间": None,
            "自动续费状态": False,
            "是否试用期": False,
            "是否宽限期": False,
            "是否计费重试期": False
        }

        # 从最新交易信息中获取状态
        if transactions:
            latest_transaction = transactions[0]  # 假设第一个是最新的

            # 检查过期时间
            if latest_transaction.expires_date_ms:
                try:
                    过期时间戳 = int(latest_transaction.expires_date_ms) / 1000
                    result["过期时间"] = latest_transaction.expires_date
                    当前时间戳 = datetime.now().timestamp()

                    if 当前时间戳 < 过期时间戳:
                        result["是否有效订阅"] = True
                        result["订阅状态"] = "active"
                    else:
                        result["订阅状态"] = "expired"
                except (ValueError, TypeError):
                    pass

            # 检查是否试用期
            if latest_transaction.is_trial_period == "true":
                result["是否试用期"] = True
                if result["是否有效订阅"]:
                    result["订阅状态"] = "trial"

            # 检查取消状态
            if latest_transaction.cancellation_date:
                result["订阅状态"] = "cancelled"
                result["是否有效订阅"] = False

        # 从续费信息中获取自动续费状态
        if renewals:
            renewal_info = renewals[0]  # 假设第一个是最新的
            result["自动续费状态"] = renewal_info.auto_renew_status == "1"

            # 检查宽限期
            if renewal_info.grace_period_expires_date_ms:
                try:
                    宽限期过期时间戳 = int(renewal_info.grace_period_expires_date_ms) / 1000
                    当前时间戳 = datetime.now().timestamp()
                    if 当前时间戳 < 宽限期过期时间戳:
                        result["是否宽限期"] = True
                        if result["订阅状态"] == "expired":
                            result["订阅状态"] = "grace_period"
                except (ValueError, TypeError):
                    pass

            # 检查计费重试期
            if renewal_info.is_in_billing_retry_period == "1":
                result["是否计费重试期"] = True
                if result["订阅状态"] == "expired":
                    result["订阅状态"] = "billing_retry"

        return result
