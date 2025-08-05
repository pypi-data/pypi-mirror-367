"""
# File       : 使用示例.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：苹果内购支付验证服务使用示例

## API 使用说明：
1. 通用验证方法：验证购买(收据数据, 交易ID=None)
   - 支持一次性购买和订阅购买
   - 购买类型参数用于日志区分

2. 其他方法：
   - 查询最新交易状态(收据数据)  # 获取最新交易
   - 检查订阅状态(收据数据)      # 详细订阅信息
"""
import asyncio
from app_tools_zxw.废弃_SDK_苹果内购支付 import 苹果内购支付服务
from pems.config_苹果支付 import 共享密钥, recipt, transaction_id, originalTransactionIdentifierIOS


async def 示例_验证购买():
    """验证一次性购买示例"""
    # 初始化服务（使用沙盒环境）
    apple_service = 苹果内购支付服务(
        共享密钥=共享密钥,
        是否沙盒环境=True
    )

    try:
        # 验证一次性购买
        result = await apple_service.验证购买(recipt, transaction_id)

        print(f"验证结果:")
        print(f"  商户订单号: {result.商户订单号}")
        print(f"  支付平台交易号: {result.支付平台交易号}")
        print(f"  产品ID: {result.产品ID}")
        print(f"  交易状态: {result.交易状态}")
        print(f"  支付时间: {result.支付时间}")
        print(f"  验证环境: {result.验证环境}")
        print(f"  是否已退款: {result.是否已退款}")
        # print(result.model_dump())

        # 验证订阅购买
        result = await apple_service.验证购买(recipt, originalTransactionIdentifierIOS)

        print(f"订阅验证结果:")
        print(f"  商户订单号: {result.商户订单号}")
        print(f"  支付平台交易号: {result.支付平台交易号}")
        print(f"  原始交易号: {result.原始交易号}")
        print(f"  产品ID: {result.产品ID}")
        print(f"  交易状态: {result.交易状态}")
        print(f"  支付时间: {result.支付时间}")
        print(f"  过期时间: {result.过期时间}")
        print(f"  是否试用期: {result.是否试用期}")
        print(f"  验证环境: {result.验证环境}")

        # 查询最新交易状态
        result = await apple_service.查询最新交易状态(recipt)

        print(f"最新交易状态:")
        print(f"  交易ID: {result.支付平台交易号}")
        print(f"  产品ID: {result.产品ID}")
        print(f"  交易状态: {result.交易状态}")
        print(f"  支付时间: {result.支付时间}")

    except Exception as e:
        print(f"验证失败: {e}")
        return None


async def 示例_查询最新交易():
    """查询最新交易状态示例"""
    apple_service = 苹果内购支付服务(
        共享密钥=共享密钥,
        是否沙盒环境=True
    )

    # 使用测试数据
    收据数据 = recipt

    try:
        # 查询最新交易状态
        result = await apple_service.查询最新交易状态(收据数据)

        print(f"最新交易状态:")
        print(f"  交易ID: {result.支付平台交易号}")
        print(f"  产品ID: {result.产品ID}")
        print(f"  交易状态: {result.交易状态}")
        print(f"  支付时间: {result.支付时间}")

        return result

    except Exception as e:
        print(f"查询失败: {e}")
        return None


async def 示例_检查订阅状态():
    """检查订阅状态示例"""
    apple_service = 苹果内购支付服务(
        共享密钥=共享密钥,
        是否沙盒环境=True
    )

    # 使用测试数据
    收据数据 = recipt

    try:
        # 检查订阅状态
        订阅信息 = await apple_service.检查订阅状态(收据数据)

        print(f"订阅状态详情:")
        print(f"  环境: {订阅信息.环境}")
        print(f"  最新交易信息数量: {len(订阅信息.最新交易信息)}")
        print(f"  待续费信息数量: {len(订阅信息.待续费信息)}")

        # 显示最新交易信息
        for i, 交易 in enumerate(订阅信息.最新交易信息):
            print(f"  交易 {i + 1}:")
            print(f"    产品ID: {交易.product_id}")
            print(f"    交易ID: {交易.transaction_id}")
            print(f"    过期时间: {交易.expires_date}")
            print(f"    是否试用期: {交易.is_trial_period}")

        return 订阅信息

    except Exception as e:
        print(f"检查订阅状态失败: {e}")
        return None


async def main():
    """主函数，运行所有示例"""
    print("=== 苹果内购支付验证服务使用示例 ===\n")
    print(f"使用测试数据:")
    print(f"  共享密钥: {共享密钥}")
    print(f"  交易ID: {transaction_id}")
    print(f"  原始交易ID: {originalTransactionIdentifierIOS}")
    print(f"  收据数据长度: {len(recipt)} 字符\n")

    print("1. 验证购买:")
    await 示例_验证购买()
    print("\n" + "=" * 50 + "\n")

    print("2. 查询最新交易:")
    await 示例_查询最新交易()
    print("\n" + "=" * 50 + "\n")

    print("3. 检查订阅状态:")
    await 示例_检查订阅状态()


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
