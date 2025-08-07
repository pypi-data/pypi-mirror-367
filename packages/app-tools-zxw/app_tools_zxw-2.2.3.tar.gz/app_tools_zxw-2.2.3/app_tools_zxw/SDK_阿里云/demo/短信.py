#!/usr/bin/env python
#coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

userID = 'sms@见阿里.onaliyun.com'
accessKeyId = '见阿里云短信服务'
accessSecret = '见阿里云短信服务'
#
client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')

request.add_query_param('RegionId', "cn-hangzhou")
request.add_query_param('PhoneNumbers', "15050560028")
request.add_query_param('SignName', "景募")
request.add_query_param('TemplateCode', "SMS_168725021")
request.add_query_param('TemplateParam', "{\"code\":1234}")

response = client.do_action_with_exception(request)
# python2:  print(response)
print(str(response, encoding = 'utf-8'))
