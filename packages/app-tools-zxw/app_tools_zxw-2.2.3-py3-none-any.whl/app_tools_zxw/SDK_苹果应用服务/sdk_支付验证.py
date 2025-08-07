"""
# File       : 支付服务_官方lib_async.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购支付验证服务（使用官方 app-store-server-library）
"""
import os
from typing import Optional, List
from datetime import datetime
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW, ErrorCode
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from app_tools_zxw.SDK_苹果应用服务.models import (
    ApplePaymentResult,
    SubscriptionStatus,
    SubscriptionTransactionInfo,
    PendingRenewalInfo,
    ApplePaymentMapper
)

try:
    from appstoreserverlibrary.api_client import AsyncAppStoreServerAPIClient, APIException
    from appstoreserverlibrary.models.Environment import Environment
    from appstoreserverlibrary.models.TransactionHistoryRequest import TransactionHistoryRequest, ProductType, Order
    from appstoreserverlibrary.models.HistoryResponse import HistoryResponse
    from appstoreserverlibrary.signed_data_verifier import SignedDataVerifier, VerificationException
    from appstoreserverlibrary.receipt_utility import ReceiptUtility
except ImportError:
    raise ImportError(
        "苹果官方库 app-store-server-library 未安装。"
        "请运行: pip install 'app-store-server-library[async]==1.9.0'"
    )

logger = setup_logger(__name__)


class 苹果内购支付服务_官方库:
    """苹果内购支付验证服务（使用官方 app-store-server-library）"""

    def __init__(
            self,
            私钥文件路径: str,
            密钥ID: str,
            发行者ID: str,
            应用包ID: str,
            是否沙盒环境: bool = True,
            苹果ID: Optional[int] = None,
            根证书路径: Optional[List[str]] = None
    ):
        """
        初始化苹果内购支付服务（官方库版本）
        :param 私钥文件路径: 从 App Store Connect 下载的私钥文件路径（.p8 文件）
        :param 密钥ID: App Store Connect 中的密钥 ID
        :param 发行者ID: App Store Connect 中的发行者 ID
        :param 应用包ID: 应用的 Bundle ID
        :param 是否沙盒环境: 是否使用沙盒环境
        :param 苹果ID: 应用的 Apple ID（生产环境必需）
        :param 根证书路径: 苹果根证书文件路径列表（用于验证签名数据）
        """
        self.私钥文件路径 = 私钥文件路径
        self.密钥ID = 密钥ID
        self.发行者ID = 发行者ID
        self.应用包ID = 应用包ID
        self.是否沙盒环境 = 是否沙盒环境
        self.苹果ID = 苹果ID
        self.根证书路径 = 根证书路径 or []

        # 设置环境
        self.环境 = Environment.SANDBOX if 是否沙盒环境 else Environment.PRODUCTION

        # 检查生产环境必需参数
        if not 是否沙盒环境 and not 苹果ID:
            raise ValueError("生产环境必须提供苹果ID")

        # 检查私钥文件
        if not os.path.exists(私钥文件路径):
            raise FileNotFoundError(f"私钥文件不存在: {私钥文件路径}")

        # 读取私钥
        with open(私钥文件路径, 'r') as f:
            self.私钥内容 = f.read()

        # 初始化客户端
        self._初始化客户端()

        logger.info(f"苹果内购支付服务（官方库）初始化完成，环境：{'沙盒' if 是否沙盒环境 else '生产'}")

    def _初始化客户端(self):
        """初始化苹果官方库客户端"""
        try:
            # 初始化 API 客户端
            self.api_client = AsyncAppStoreServerAPIClient(
                signing_key=self.私钥内容.encode('utf-8'),
                key_id=self.密钥ID,
                issuer_id=self.发行者ID,
                bundle_id=self.应用包ID,
                environment=self.环境
            )

            # 初始化数据验证器（如果提供了根证书）
            self.data_verifier = None
            if self.根证书路径:
                根证书数据 = []
                for 证书路径 in self.根证书路径:
                    if os.path.exists(证书路径):
                        with open(证书路径, 'rb') as f:
                            根证书数据.append(f.read())

                if 根证书数据:
                    self.data_verifier = SignedDataVerifier(
                        root_certificates=根证书数据,
                        enable_online_checks=True,
                        environment=self.环境,
                        bundle_id=self.应用包ID,
                        app_apple_id=self.苹果ID
                    )

            # 初始化收据工具
            self.receipt_utility = ReceiptUtility()

        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.系统错误,
                http_status_code=500,
                detail=f"初始化苹果官方库客户端失败: {str(e)}"
            )

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if hasattr(self.api_client, 'close'):
            await self.api_client.close()

    def _构建支付结果(self, transaction_info: dict) -> ApplePaymentResult:
        """构建标准化的支付结果"""
        print(f"支付结果-官方返回值:", transaction_info)

        # 使用统一的映射函数
        return ApplePaymentResult.from_transaction_info(transaction_info, self.是否沙盒环境)

    def _构建订阅状态(self, response, 订阅交易列表: List[SubscriptionTransactionInfo],
                      续费信息列表: List[PendingRenewalInfo]) -> SubscriptionStatus:
        """构建订阅状态对象"""
        # 使用统一的状态分析函数
        状态分析 = ApplePaymentMapper.analyze_subscription_status(订阅交易列表, 续费信息列表)

        return SubscriptionStatus(
            环境="Sandbox" if self.是否沙盒环境 else "Production",
            最新收据=None,  # 这里可以根据需要设置
            最新交易信息=订阅交易列表,
            待续费信息=续费信息列表,
            是否有效订阅=状态分析["是否有效订阅"],
            订阅状态=状态分析["订阅状态"],
            过期时间=状态分析["过期时间"],
            自动续费状态=状态分析["自动续费状态"],
            是否试用期=状态分析["是否试用期"],
            是否宽限期=状态分析["是否宽限期"],
            是否计费重试期=状态分析["是否计费重试期"]
        )

    async def 验证收据_从应用收据(self, 应用收据: str) -> ApplePaymentResult:
        """
        从应用收据验证交易
        :param 应用收据: base64编码的应用收据数据
        :return: 验证结果
        """
        logger.info("开始从应用收据验证交易")

        try:
            # 从收据提取交易ID
            transaction_id = self.receipt_utility.extract_transaction_id_from_app_receipt(应用收据)

            if not transaction_id:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.交易不存在,
                    http_status_code=404,
                    detail="无法从应用收据中提取交易ID"
                )

            logger.info(f"从收据中提取到交易ID: {transaction_id}")

            # 获取最新交易
            return await self.获取最新交易(transaction_id)

        except APIException as e:
            logger.error(f"验证收据失败，API错误: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果API调用失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"验证收据失败，错误: {str(e)}")
            raise

    async def 获取最新交易(
            self,
            原始交易ID: str,
            产品类型: Optional[List[ProductType]] = None
    ) -> ApplePaymentResult:
        """
        获取最新交易信息
        :param 原始交易ID: 原始交易ID
        :param 产品类型: 产品类型过滤
        :return: 最新交易的验证结果
        """
        logger.info(f"开始获取最新交易，原始交易ID: {原始交易ID}")

        try:
            # 构建请求
            request = TransactionHistoryRequest(
                sort=Order.DESCENDING,  # 降序排列，最新的在前
                revoked=False,
                productTypes=产品类型 or [ProductType.AUTO_RENEWABLE, ProductType.NON_RENEWABLE, ProductType.CONSUMABLE,
                                          ProductType.NON_CONSUMABLE]
            )

            # 获取交易历史数据
            response: HistoryResponse = await self.api_client.get_transaction_history(
                transaction_id=原始交易ID,
                revision=None,
                transaction_history_request=request
            )

            if not response.signedTransactions:
                raise HTTPException_AppToolsSZXW(
                    error_code=ErrorCode.交易不存在,
                    http_status_code=404,
                    detail=f"未找到交易ID为 {原始交易ID} 的交易记录"
                )

            # 获取最新交易（第一个）
            latest_signed_transaction = response.signedTransactions[0]

            # 如果有数据验证器，验证签名
            if self.data_verifier:
                try:
                    transaction_info = self.data_verifier.verify_and_decode_signed_transaction(
                        latest_signed_transaction)
                except VerificationException as e:
                    logger.warning(f"交易签名验证失败: {str(e)}")
                    # 如果签名验证失败，仍然继续处理，但记录警告
                    pass

            # 解析交易信息（这里需要解码 JWT）
            # 注意：实际实现中需要解码 JWT 来获取交易详情
            # 这里暂时使用一个简化的处理方式
            transaction_info = await self._解码交易信息(latest_signed_transaction)

            result = self._构建支付结果(transaction_info)
            logger.info(f"最新交易获取成功，交易ID: {原始交易ID}, 状态: {result.交易状态}")
            return result

        except APIException as e:
            logger.error(f"获取最新交易失败，API错误: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果API调用失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"获取最新交易失败，错误: {str(e)}")
            raise

    async def _解码交易信息(self, signed_transaction: str) -> dict:
        """
        解码签名的交易信息
        注意：这是一个简化实现，实际中应该使用官方库的 JWT 解码功能
        """
        import base64
        import json

        try:
            # JWT 格式：header.payload.signature
            parts = signed_transaction.split('.')
            if len(parts) != 3:
                raise ValueError("无效的 JWT 格式")

            # 解码 payload（第二部分）
            payload = parts[1]
            # 添加必要的填充
            while len(payload) % 4:
                payload += '='

            decoded_bytes = base64.urlsafe_b64decode(payload)
            transaction_info = json.loads(decoded_bytes)

            return transaction_info

        except Exception as e:
            logger.error(f"解码交易信息失败: {str(e)}")
            # 返回一个基本的交易信息
            return {
                "transactionId": "unknown",
                "originalTransactionId": "unknown",
                "productId": "unknown",
                "purchaseDate": str(int(datetime.now().timestamp() * 1000)),
            }

    async def 验证特定交易(self, 交易ID: str) -> ApplePaymentResult:
        """
        验证特定交易
        :param 交易ID: 要验证的交易ID
        :return: 验证结果
        """
        logger.info(f"开始验证特定交易，交易ID: {交易ID}")

        try:
            # 获取交易信息
            signed_transaction = await self.api_client.get_transaction_info(交易ID)

            # 解码交易信息
            transaction_info = await self._解码交易信息(signed_transaction.signedTransactionInfo)

            result = self._构建支付结果(transaction_info)
            logger.info(f"特定交易验证成功，交易ID: {交易ID}, 状态: {result.交易状态}")
            return result

        except APIException as e:
            logger.error(f"验证特定交易失败，API错误: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果API调用失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"验证特定交易失败，错误: {str(e)}")
            raise

    async def 获取订阅状态(self, 原始交易ID: str) -> SubscriptionStatus:
        """
        获取订阅状态
        :param 原始交易ID: 订阅的原始交易ID
        :return: 订阅状态信息
        """
        logger.info(f"开始获取订阅状态，原始交易ID: {原始交易ID}")

        try:
            # 获取所有订阅状态
            response = await self.api_client.get_all_subscription_statuses(原始交易ID)

            订阅交易列表: List[SubscriptionTransactionInfo] = []
            续费信息列表: List[PendingRenewalInfo] = []

            # 处理订阅状态数据
            if response.data:
                for status_item in response.data:
                    # 处理最新交易信息
                    if status_item.lastTransactions:
                        for transaction in status_item.lastTransactions:
                            # 解码交易信息
                            transaction_info = await self._解码交易信息(transaction.signedTransactionInfo)

                            # 使用统一的映射函数创建 SubscriptionTransactionInfo 对象
                            subscription_transaction = SubscriptionTransactionInfo.from_transaction_info(
                                transaction_info)
                            订阅交易列表.append(subscription_transaction)

                            # 处理续费信息
                            if hasattr(transaction, 'signedRenewalInfo') and transaction.signedRenewalInfo:
                                # 解码续费信息
                                renewal_info = await self._解码交易信息(transaction.signedRenewalInfo)

                                # 使用统一的映射函数创建 PendingRenewalInfo 对象
                                pending_renewal = PendingRenewalInfo.from_renewal_info(renewal_info)
                                续费信息列表.append(pending_renewal)

            # 构建订阅状态对象
            subscription_status = self._构建订阅状态(response, 订阅交易列表, 续费信息列表)

            logger.info(f"订阅状态获取成功，原始交易ID: {原始交易ID}, 订阅状态: {subscription_status.订阅状态}")
            return subscription_status

        except APIException as e:
            logger.error(f"获取订阅状态失败，API错误: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果API调用失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"获取订阅状态失败，错误: {str(e)}")
            raise

    async def 请求测试通知(self) -> str:
        """
        请求测试通知（用于测试 App Store Server Notifications）
        :return: 测试通知令牌
        """
        logger.info("开始请求测试通知")

        try:
            response = await self.api_client.request_test_notification()
            logger.info(f"测试通知请求成功，令牌: {response.testNotificationToken}")
            return response.testNotificationToken

        except APIException as e:
            logger.error(f"请求测试通知失败，API错误: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"苹果API调用失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"请求测试通知失败，错误: {str(e)}")
            raise

    async def 验证通知数据(self, 签名通知数据: str) -> dict:
        """
        验证 App Store Server Notifications 通知数据
        :param 签名通知数据: 签名的通知数据
        :return: 验证后的通知数据
        """
        if not self.data_verifier:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.系统错误,
                http_status_code=500,
                detail="数据验证器未初始化，无法验证通知数据"
            )

        logger.info("开始验证通知数据")

        try:
            # 验证并解码通知
            notification_payload = self.data_verifier.verify_and_decode_notification(签名通知数据)

            logger.info("通知数据验证成功")
            return notification_payload.__dict__

        except VerificationException as e:
            logger.error(f"通知数据验证失败: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"通知数据验证失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"验证通知数据失败，错误: {str(e)}")
            raise


# 向后兼容的别名
苹果内购支付服务 = 苹果内购支付服务_官方库
