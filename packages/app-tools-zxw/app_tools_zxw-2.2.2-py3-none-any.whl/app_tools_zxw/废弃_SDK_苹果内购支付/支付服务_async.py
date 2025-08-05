"""
# File       : 支付服务_async.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购支付验证服务
"""
import httpx
from uuid import uuid4
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW, ErrorCode
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from app_tools_zxw.废弃_SDK_苹果内购支付.models import *

logger = setup_logger(__name__)


class 苹果内购支付服务:
    """苹果内购支付验证服务"""

    def __init__(self, 共享密钥: str, 是否沙盒环境: bool = True):
        """
        初始化苹果内购支付服务
        :param 共享密钥: 苹果内购共享密钥
        :param 是否沙盒环境: 是否使用沙盒环境
        """
        self.共享密钥 = 共享密钥
        self.是否沙盒环境 = 是否沙盒环境

        # 苹果验证服务器地址
        self.生产环境验证地址 = "https://buy.itunes.apple.com/verifyReceipt"
        self.沙盒环境验证地址 = "https://sandbox.itunes.apple.com/verifyReceipt"

        # 错误码映射
        self.错误码映射 = {
            0: "验证成功",
            21000: "App Store无法读取提供的JSON数据",
            21002: "收据数据格式错误",
            21003: "收据无法验证",
            21004: "共享密钥不匹配",
            21005: "收据服务器当前不可用",
            21006: "收据有效但订阅已过期",
            21007: "收据为测试环境但发送到生产环境验证",
            21008: "收据为生产环境但发送到测试环境验证"
        }

        logger.info(f"苹果内购支付服务初始化完成，环境：{'沙盒' if 是否沙盒环境 else '生产'}")

    @staticmethod
    def 生成订单号() -> str:
        """生成商户订单号"""
        原始订单号 = str(uuid4())
        return hashlib.md5(原始订单号.encode('utf-8')).hexdigest()

    async def _发送验证请求(self, 收据数据: str) -> dict:
        """
        向苹果服务器发送验证请求
        :param 收据数据: base64编码的收据数据
        :return: 验证响应
        """
        验证地址 = self.沙盒环境验证地址 if self.是否沙盒环境 else self.生产环境验证地址

        请求数据 = {
            "receipt-data": 收据数据,
            "password": self.共享密钥,
            "exclude-old-transactions": True
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    验证地址,
                    json=请求数据,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.网络超时,
                http_status_code=408,
                detail="苹果验证服务器响应超时"
            )
        except httpx.HTTPError as e:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.网络请求失败,
                http_status_code=400,
                detail=f"请求苹果验证服务器失败: {str(e)}"
            )
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.系统错误,
                http_status_code=500,
                detail=f"苹果内购验证异常: {str(e)}"
            )

    async def _处理验证响应(self, 响应数据: dict, 收据数据: str, 目标交易ID: str = None) -> ApplePaymentResult:
        """
        处理苹果服务器的验证响应
        :param 响应数据: 苹果服务器返回的数据
        :param 目标交易ID: 要验证的特定交易ID
        :return: 标准化的支付结果
        """
        状态码 = 响应数据.get("status")

        # 检查验证状态
        if 状态码 != 0:
            错误信息 = self.错误码映射.get(状态码, f"未知错误码: {状态码}")

            # 如果是环境错误，自动切换重试
            if 状态码 == 21007:  # 测试收据发到生产环境
                logger.info("检测到测试收据，切换到沙盒环境重试")
                old_env = self.是否沙盒环境
                self.是否沙盒环境 = True
                if old_env != self.是否沙盒环境:  # 避免无限递归
                    新响应数据 = await self._发送验证请求(收据数据)
                    return await self._处理验证响应(新响应数据, 收据数据, 目标交易ID)
            elif 状态码 == 21008:  # 生产收据发到测试环境
                logger.info("检测到生产收据，切换到生产环境重试")
                old_env = self.是否沙盒环境
                self.是否沙盒环境 = False
                if old_env != self.是否沙盒环境:  # 避免无限递归
                    新响应数据 = await self._发送验证请求(收据数据)
                    return await self._处理验证响应(新响应数据, 收据数据, 目标交易ID)

            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果内购验证失败: {错误信息}"
            )

        收据信息 = 响应数据.get("receipt", {})
        环境 = 响应数据.get("environment", "Unknown")

        # 获取交易信息列表
        交易列表 = []

        # 处理订阅类型的最新交易信息
        if "latest_receipt_info" in 响应数据:
            交易列表.extend(响应数据["latest_receipt_info"])

        # 处理一次性购买的交易信息
        if "receipt" in 响应数据 and "in_app" in 响应数据["receipt"]:
            交易列表.extend(响应数据["receipt"]["in_app"])

        # 如果指定了目标交易ID，查找匹配的交易
        目标交易 = None
        if 目标交易ID:
            for 交易 in 交易列表:
                if 交易.get("transaction_id") == 目标交易ID:
                    目标交易 = 交易
                    break

            if not 目标交易:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.交易不存在,
                    http_status_code=404,
                    detail=f"未找到交易ID为 {目标交易ID} 的交易记录"
                )
        else:
            # 如果没有指定交易ID，使用最新的交易
            if 交易列表:
                目标交易 = 交易列表[-1]  # 取最后一个（最新的）交易
            else:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.交易不存在,
                    http_status_code=404,
                    detail="收据中未找到任何交易记录"
                )

        # 解析交易状态
        交易状态 = self._解析交易状态(目标交易, 响应数据)

        # 检查退款状态
        是否已退款 = "cancellation_date" in 目标交易
        退款时间 = 目标交易.get("cancellation_date")
        退款原因 = self._解析退款原因(目标交易.get("cancellation_reason"))

        # 构建结果
        return ApplePaymentResult(
            商户订单号=目标交易.get("transaction_id", ""),  # 使用苹果交易ID作为商户订单号
            支付平台交易号=目标交易.get("transaction_id", ""),
            原始交易号=目标交易.get("original_transaction_id", ""),
            产品ID=目标交易.get("product_id", ""),
            商品数量=目标交易.get("quantity"),
            交易金额=目标交易.get("price"),
            交易状态=交易状态,
            支付时间=self._格式化时间(目标交易.get("purchase_date")),
            支付时间戳=目标交易.get("purchase_date_ms"),
            支付时间PST=self._格式化时间(目标交易.get("purchase_date_pst")),
            原始购买时间=self._格式化时间(目标交易.get("original_purchase_date")),
            原始购买时间戳=目标交易.get("original_purchase_date_ms"),
            原始购买时间PST=self._格式化时间(目标交易.get("original_purchase_date_pst")),
            过期时间=self._格式化时间(目标交易.get("expires_date")),
            过期时间戳=目标交易.get("expires_date_ms"),
            过期时间PST=self._格式化时间(目标交易.get("expires_date_pst")),
            网页订单行项目ID=目标交易.get("web_order_line_item_id"),
            验证环境=环境,
            是否试用期=目标交易.get("is_trial_period") == "true",
            是否介绍性优惠期=目标交易.get("is_in_intro_offer_period") == "true",
            是否已退款=是否已退款,
            退款时间=self._格式化时间(退款时间) if 退款时间 else None,
            退款原因=退款原因
        )

    def _解析交易状态(self, 交易信息: dict, 完整响应: dict) -> OrderStatus:
        """解析交易状态"""
        # 检查是否已退款
        if "cancellation_date" in 交易信息:
            return OrderStatus.CANCELLED

        # 检查订阅是否过期
        if "expires_date_ms" in 交易信息:
            过期时间戳 = int(交易信息["expires_date_ms"]) / 1000
            当前时间戳 = datetime.now().timestamp()

            if 当前时间戳 > 过期时间戳:
                return OrderStatus.FINISHED  # 订阅已过期
            else:
                return OrderStatus.PAID  # 订阅有效

        # 一次性购买认为是已支付
        return OrderStatus.PAID

    def _解析退款原因(self, 退款原因码: str) -> Optional[str]:
        """解析退款原因"""
        if not 退款原因码:
            return None

        退款原因映射 = {
            "0": "其他原因",
            "1": "应用问题"
        }
        return 退款原因映射.get(退款原因码, f"未知原因: {退款原因码}")

    def _格式化时间(self, 时间字符串: str) -> Optional[datetime]:
        """格式化苹果返回的时间字符串，转换成带时区信息的datetime对象"""
        if not 时间字符串:
            return None

        try:
            # 苹果返回的时间格式主要有以下几种:
            # 1. '2023-12-20 10:30:00 Etc/GMT'
            # 2. '2023-12-20T10:30:00Z'
            # 3. '2023-12-20T10:30:00.000Z'
            # 4. '2023-12-20 10:30:00 America/Los_Angeles'

            # 处理 Etc/GMT 格式 (UTC时间)
            if " Etc/GMT" in 时间字符串:
                时间部分 = 时间字符串.replace(" Etc/GMT", "").strip()
                dt = datetime.strptime(时间部分, "%Y-%m-%d %H:%M:%S")
                return dt.replace(tzinfo=timezone.utc)

            # 处理ISO格式 (Z结尾表示UTC)
            elif 时间字符串.endswith('Z'):
                # 移除Z并解析
                时间部分 = 时间字符串[:-1]
                if '.' in 时间部分:
                    # 带毫秒的格式
                    dt = datetime.fromisoformat(时间部分)
                else:
                    # 不带毫秒的格式
                    dt = datetime.fromisoformat(时间部分)
                return dt.replace(tzinfo=timezone.utc)

            # 处理其他时区格式 (如 America/Los_Angeles)
            elif " America/" in 时间字符串:
                # 苹果PST/PDT时间，通常是太平洋时区
                时间部分 = 时间字符串.split(" ")[0] + " " + 时间字符串.split(" ")[1]
                dt = datetime.strptime(时间部分, "%Y-%m-%d %H:%M:%S")
                # 太平洋时区 (PST: UTC-8, PDT: UTC-7)
                # 这里简化处理为PST (UTC-8)
                pst_tz = timezone(timedelta(hours=-8))
                return dt.replace(tzinfo=pst_tz)

            # 处理标准ISO格式 (带时区信息)
            elif 'T' in 时间字符串 and ('+' in 时间字符串 or '-' in 时间字符串[-6:]):
                return datetime.fromisoformat(时间字符串)

            # 处理纯时间字符串 (无时区信息，默认为UTC)
            else:
                # 尝试常见格式
                时间格式列表 = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S.%f"
                ]

                for 格式 in 时间格式列表:
                    try:
                        dt = datetime.strptime(时间字符串, 格式)
                        return dt.replace(tzinfo=timezone.utc)  # 默认设为UTC
                    except ValueError:
                        continue

                # 如果所有格式都不匹配，尝试fromisoformat
                dt = datetime.fromisoformat(时间字符串)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt

        except Exception as e:
            logger.warning(f"时间格式化失败，原始字符串: {时间字符串}, 错误: {str(e)}")
            return None

    def _分析订阅状态(self, 交易信息列表: List[SubscriptionTransactionInfo],
                      续费信息列表: List[PendingRenewalInfo]) -> dict:
        """
        分析订阅状态
        :param 交易信息列表: 交易信息列表
        :param 续费信息列表: 续费信息列表
        :return: 订阅状态分析结果
        """
        # 默认状态
        状态分析 = {
            "是否有效订阅": False,
            "订阅状态": "unknown",
            "过期时间": None,
            "自动续费状态": False,
            "是否试用期": False,
            "是否宽限期": False,
            "是否计费重试期": False
        }

        if not 交易信息列表:
            return 状态分析

        # 获取最新的交易信息
        最新交易 = 交易信息列表[-1] if 交易信息列表 else None
        最新续费信息 = 续费信息列表[-1] if 续费信息列表 else None

        if not 最新交易:
            return 状态分析

        当前时间戳 = datetime.now().timestamp()

        # 检查是否已退款/取消
        if 最新交易.cancellation_date:
            状态分析["订阅状态"] = "cancelled"
            状态分析["过期时间"] = self._格式化时间(最新交易.cancellation_date)
            return 状态分析

        # 检查过期时间
        过期时间戳 = None
        if 最新交易.expires_date_ms:
            过期时间戳 = int(最新交易.expires_date_ms) / 1000
            状态分析["过期时间"] = self._格式化时间(最新交易.expires_date)

        # 检查试用期
        if 最新交易.is_trial_period == "true":
            状态分析["是否试用期"] = True

        # 分析续费信息
        if 最新续费信息:
            # 自动续费状态
            状态分析["自动续费状态"] = 最新续费信息.auto_renew_status == "1"

            # 检查宽限期
            if 最新续费信息.grace_period_expires_date_ms:
                宽限期过期时间戳 = int(最新续费信息.grace_period_expires_date_ms) / 1000
                状态分析["是否宽限期"] = 当前时间戳 <= 宽限期过期时间戳

            # 检查计费重试期
            状态分析["是否计费重试期"] = 最新续费信息.is_in_billing_retry_period == "1"

        # 确定订阅状态
        if 过期时间戳:
            if 当前时间戳 <= 过期时间戳:
                # 订阅有效
                状态分析["是否有效订阅"] = True
                if 状态分析["是否试用期"]:
                    状态分析["订阅状态"] = "trial"
                else:
                    状态分析["订阅状态"] = "active"
            else:
                # 订阅已过期
                if 状态分析["是否宽限期"]:
                    状态分析["订阅状态"] = "grace_period"
                    状态分析["是否有效订阅"] = True  # 宽限期内仍可使用
                elif 状态分析["是否计费重试期"]:
                    状态分析["订阅状态"] = "billing_retry"
                    状态分析["是否有效订阅"] = True  # 计费重试期内仍可使用
                else:
                    状态分析["订阅状态"] = "expired"
        else:
            # 没有过期时间的情况（一般不应该发生在订阅中）
            状态分析["订阅状态"] = "unknown"

        return 状态分析

    async def _发送验证并处理(self, 收据数据: str, 目标交易ID: str = None) -> ApplePaymentResult:
        """发送验证请求并处理响应的内部方法"""
        响应数据 = await self._发送验证请求(收据数据)
        return await self._处理验证响应(响应数据, 收据数据, 目标交易ID)

    async def 验证购买(self, 收据数据: str, 交易ID: str = None) -> ApplePaymentResult:
        """
        通用的购买验证方法，支持一次性购买和订阅购买
        :param 收据数据: base64编码的收据数据
        :param 交易ID: 要验证的交易ID（一次性购买）或原始交易ID（订阅购买），可选
        :return: 验证结果
        """
        logger.info(f"开始验证，交易ID: {交易ID}")

        try:
            result = await self._发送验证并处理(收据数据, 交易ID)
            logger.info(f"验证成功，交易ID: {交易ID}, 状态: {result.交易状态}")
            return result
        except Exception as e:
            logger.error(f"验证失败，交易ID: {交易ID}, 错误: {str(e)}")
            raise

    async def 查询最新交易状态(self, 收据数据: str) -> ApplePaymentResult:
        """
        查询收据中最新的交易状态
        :param 收据数据: base64编码的收据数据
        :return: 最新交易的验证结果
        """
        logger.info("开始查询最新交易状态")

        try:
            result = await self._发送验证并处理(收据数据)
            logger.info(f"最新交易状态查询成功，交易ID: {result.支付平台交易号}, 状态: {result.交易状态}")
            return result
        except Exception as e:
            logger.error(f"最新交易状态查询失败，错误: {str(e)}")
            raise

    async def 检查订阅状态(self, 收据数据: str) -> SubscriptionStatus:
        """
        检查订阅状态（返回详细的订阅信息）
        :param 收据数据: base64编码的收据数据
        :return: 详细的订阅状态信息
        """
        logger.info("开始检查订阅状态")

        try:
            响应数据 = await self._发送验证请求(收据数据)

            if 响应数据.get("status") != 0:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.苹果内购验证失败,
                    http_status_code=400,
                    detail=f"订阅状态检查失败: {self.错误码映射.get(响应数据.get('status'), '未知错误')}"
                )

            # 提取基础信息
            环境 = 响应数据.get("environment", "Unknown")
            最新收据 = 响应数据.get("latest_receipt")
            交易信息列表 = 响应数据.get("latest_receipt_info", [])
            续费信息列表 = 响应数据.get("pending_renewal_info", [])

            # 转换为pydantic模型，添加错误处理确保兼容性
            交易信息模型列表 = []
            for 交易 in 交易信息列表:
                try:
                    交易信息模型列表.append(SubscriptionTransactionInfo(**交易))
                except Exception as e:
                    logger.warning(f"解析交易信息失败，跳过该条记录: {e}")
                    continue

            续费信息模型列表 = []
            for 续费 in 续费信息列表:
                try:
                    续费信息模型列表.append(PendingRenewalInfo(**续费))
                except Exception as e:
                    logger.warning(f"解析续费信息失败，跳过该条记录: {e}")
                    continue

            # 分析订阅状态
            订阅状态分析 = self._分析订阅状态(交易信息模型列表, 续费信息模型列表)

            # 构建订阅状态对象
            订阅状态 = SubscriptionStatus(
                环境=环境,
                最新收据=最新收据,
                最新交易信息=交易信息模型列表,
                待续费信息=续费信息模型列表,
                **订阅状态分析
            )

            logger.info(f"订阅状态检查成功，状态: {订阅状态.订阅状态}")
            return 订阅状态

        except Exception as e:
            logger.error(f"订阅状态检查失败，错误: {str(e)}")
            raise
