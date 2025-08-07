"""
# File       : sdk_内购优惠管理.py
# Time       ：2025/1/28
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购促销优惠管理服务
"""
import os
import time
import uuid
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW, ErrorCode
from app_tools_zxw.Funcs.fastapi_logger import setup_logger
from pydantic import BaseModel, Field

try:
    from appstoreserverlibrary.promotional_offer import PromotionalOfferSignatureCreator
except ImportError:
    raise ImportError(
        "苹果官方库 app-store-server-library 未安装。"
        "请运行: pip install 'app-store-server-library[async]==1.9.0'"
    )

logger = setup_logger(__name__)


class Model促销优惠签名请求(BaseModel):
    """促销优惠签名请求参数"""
    product_id: str = Field(..., description="产品ID")
    subscription_offer_id: str = Field(..., description="订阅优惠ID")
    application_username: Optional[str] = Field(None, description="应用用户名")
    nonce: Optional[UUID] = Field(None, description="随机数，如果不提供将自动生成")
    timestamp: Optional[int] = Field(None, description="时间戳（毫秒），如果不提供将使用当前时间")


class Model促销优惠签名结果(BaseModel):
    """Model促销优惠签名结果"""
    product_id: str = Field(..., description="产品ID")
    subscription_offer_id: str = Field(..., description="订阅优惠ID")
    application_username: Optional[str] = Field(None, description="应用用户名")
    nonce: UUID = Field(..., description="随机数")
    timestamp: int = Field(..., description="时间戳（毫秒）")
    signature: str = Field(..., description="签名")
    created_at: str = Field(..., description="创建时间")
    key_identifier: str = Field(..., description="密钥ID")


class 苹果内购优惠管理服务:
    """苹果内购促销优惠管理服务"""

    def __init__(
            self,
            私钥文件路径: str,
            密钥ID: str,
            应用包ID: str
    ):
        """
        初始化苹果内购促销优惠管理服务

        :param 私钥文件路径: 从 App Store Connect 下载的私钥文件路径（.p8 文件）
        :param 密钥ID: App Store Connect 中的密钥 ID
        :param 应用包ID: 应用的 Bundle ID
        """
        self.私钥文件路径 = 私钥文件路径
        self.密钥ID = 密钥ID
        self.应用包ID = 应用包ID

        # 检查私钥文件是否存在
        if not os.path.exists(私钥文件路径):
            raise FileNotFoundError(f"私钥文件不存在: {私钥文件路径}")

        # 读取私钥内容
        with open(私钥文件路径, 'rb') as f:
            self.私钥内容 = f.read()

        # 初始化促销优惠签名创建器
        self._初始化签名创建器()

        logger.info(f"苹果内购促销优惠管理服务初始化完成，Bundle ID: {应用包ID}")

    def _初始化签名创建器(self):
        """初始化促销优惠签名创建器"""
        try:
            self.signature_creator = PromotionalOfferSignatureCreator(
                signing_key=self.私钥内容,
                key_id=self.密钥ID,
                bundle_id=self.应用包ID
            )
            logger.info("促销优惠签名创建器初始化成功")
        except Exception as e:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.系统错误,
                http_status_code=500,
                detail=f"初始化促销优惠签名创建器失败: {str(e)}"
            )

    def 生成促销优惠签名(
            self,
            product_id: str,
            subscription_offer_id: str,
            application_username: Optional[str] = None,
            nonce: Optional[UUID] = None,
            timestamp: Optional[int] = None
    ) -> Model促销优惠签名结果:
        """
        生成促销优惠签名

        :param product_id: 产品ID
        :param subscription_offer_id: 订阅优惠ID
        :param application_username: 应用用户名（可选）
        :param nonce: UUID随机数（可选，如果不提供将自动生成）
        :param timestamp: 时间戳毫秒（可选，如果不提供将使用当前时间）
        :return: Model促销优惠签名结果
        """
        logger.info(f"开始生成促销优惠签名，产品ID: {product_id}, 优惠ID: {subscription_offer_id}")

        try:
            # 生成随机数（如果未提供）
            if nonce is None:
                nonce = uuid.uuid4()

            # 生成时间戳（如果未提供）
            if timestamp is None:
                timestamp = round(time.time())

            # 创建签名
            signature = self.signature_creator.create_signature(
                product_identifier=product_id,
                subscription_offer_id=subscription_offer_id,
                application_username=application_username,
                nonce=nonce,
                timestamp=timestamp
            )

            # 构建结果
            result = Model促销优惠签名结果(
                product_id=product_id,
                subscription_offer_id=subscription_offer_id,
                application_username=application_username,
                nonce=nonce,
                timestamp=timestamp,
                signature=signature,
                created_at=datetime.now().isoformat(),
                key_identifier=self.密钥ID
            )

            logger.info(f"促销优惠签名生成成功，产品ID: {product_id}")
            return result

        except Exception as e:
            logger.error(f"生成促销优惠签名失败: {str(e)}")
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.苹果内购验证失败,
                http_status_code=400,
                detail=f"生成促销优惠签名失败: {str(e)}"
            )

    def 批量生成促销优惠签名(
            self,
            requests: List[Model促销优惠签名请求]
    ) -> List[Model促销优惠签名结果]:
        """
        批量生成促销优惠签名

        :param requests: 促销优惠签名请求列表
        :return: 促销优惠签名结果列表
        """
        logger.info(f"开始批量生成促销优惠签名，数量: {len(requests)}")

        results = []
        for request in requests:
            try:
                result = self.生成促销优惠签名(
                    product_id=request.product_id,
                    subscription_offer_id=request.subscription_offer_id,
                    application_username=request.application_username,
                    nonce=request.nonce,
                    timestamp=request.timestamp
                )
                results.append(result)
            except Exception as e:
                logger.error(f"批量处理中生成签名失败: {str(e)}")
                # 继续处理其他请求，不中断整个批量操作
                continue

        logger.info(f"批量生成促销优惠签名完成，成功数量: {len(results)}")
        return results

    def 验证签名参数(
            self,
            product_id: str,
            subscription_offer_id: str,
            application_username: Optional[str] = None
    ) -> bool:
        """
        验证签名参数是否有效

        :param product_id: 产品ID
        :param subscription_offer_id: 订阅优惠ID
        :param application_username: 应用用户名
        :return: 参数是否有效
        """
        try:
            # 基本参数验证
            if not product_id or not isinstance(product_id, str):
                return False

            if not subscription_offer_id or not isinstance(subscription_offer_id, str):
                return False

            if application_username is not None and not isinstance(application_username, str):
                return False

            # 更多验证逻辑可以在这里添加
            return True

        except Exception as e:
            logger.error(f"验证签名参数失败: {str(e)}")
            return False

    def 获取签名配置信息(self) -> dict:
        """
        获取当前签名配置信息

        :return: 配置信息字典
        """
        return {
            "bundle_id": self.应用包ID,
            "key_id": self.密钥ID,
            "private_key_path": self.私钥文件路径,
            "service_name": "苹果内购促销优惠管理服务",
            "initialized_at": datetime.now().isoformat()
        }
