"""
# File       : api_IAP优惠券管理.py
# Time       ：2025/7/29 15:24
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from svc_order_zxw.interface.interface_苹果内购_优惠券 import get_IAP优惠卷, Model促销优惠签名结果
from svc_order_zxw.apis.api_支付_苹果内购.api_IAP订单管理 import router

router.add_api_route(
    path="/promotion/create",
    endpoint=get_IAP优惠卷,
    methods=["POST"],
    tags=["IAP优惠券管理"],
    response_model=Model促销优惠签名结果
)
