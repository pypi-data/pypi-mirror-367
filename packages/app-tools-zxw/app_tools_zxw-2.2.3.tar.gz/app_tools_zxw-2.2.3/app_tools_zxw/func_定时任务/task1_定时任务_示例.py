"""
# File       : task1_定时更新商品.py
# Time       ：2025/6/26 15:04
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：启动时必须首先执行一次
"""
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)


async def get_db_order():
    # sqlalchemy的异步get_db,用于fastapi依赖注入
    ...


class AsyncSession:
    # 从sqlalchemy导入
    pass


class TASK1_更新商品表:
    interval_minutes = 2  # 执行周期(分钟)
    get_db = get_db_order

    @staticmethod
    async def run(db: AsyncSession):
        ...
