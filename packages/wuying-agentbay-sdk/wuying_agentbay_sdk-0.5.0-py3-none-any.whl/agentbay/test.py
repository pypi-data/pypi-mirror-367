from aliyunsdkcore import client
from aliyunsdkcore.request import CommonRequest
import json
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

OSS_URL = "oss-for-codespace-test.oss-cn-hangzhou.aliyuncs.com"

endpoint = 'http://oss-cn-hangzhou.aliyuncs.com' # Suppose that your bucket is in the Hangzhou region.

bucket_name = 'oss-for-codespace-test'

access_key_id = 'LTAI5tFarNry48KJUFD2w1jk'
access_key_secret = '3apEJ0jiauXnHOh21MY33va6RX6SNE'
role_arn = "acs:ram::1024783832803838:role/ossaccess"
def ger_url():
# 从环境变量中获取访问凭证。运行本代码示例之前，请确保已设置环境变量OSS_ACCESS_KEY_ID和OSS_ACCESS_KEY_SECRET。

    auth = oss2.Auth(access_key_id, access_key_secret)
    # 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
    endpoint = "https://oss-cn-hangzhou.aliyuncs.com"

    # 填写Endpoint对应的Region信息，例如cn-hangzhou。注意，v4签名下，必须填写该参数
    region = "cn-hangzhou"

    # yourBucketName填写存储空间名称。
    bucket = oss2.Bucket(auth, endpoint, "oss-for-codespace-test", region=region)

    # 填写Object完整路径，例如exampledir/exampleobject.txt。Object完整路径中不能包含Bucket名称。
    object_name = 'test-object.txt'

    # 生成上传文件的预签名URL，有效时间为60秒。
    # 生成预签名URL时，OSS默认会对Object完整路径中的正斜线（/）进行转义，从而导致生成的预签名URL无法直接使用。
    # 设置slash_safe为True，OSS不会对Object完整路径中的正斜线（/）进行转义，此时生成的预签名URL可以直接使用。
    url = bucket.sign_url('PUT', object_name, 60, slash_safe=True)
    print('预签名URL的地址为：', url)

def get_sts_token():
    # 从环境变量中获取步骤1.1生成的RAM用户的访问密钥（AccessKey ID和AccessKey Secret）。
    # 从环境变量中获取步骤1.3生成的RAM角色的RamRoleArn。
    # access_key_id = cfg.CONF.access_key_id
    # access_key_secret = cfg.CONF.access_key_secret
    # 创建权限策略。
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')

    request = CommonRequest(product="Sts", version='2015-04-01', action_name='AssumeRole')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.add_query_param('RoleArn', role_arn)
    # 指定自定义角色会话名称，用来区分不同的令牌，例如填写为sessiontest。
    request.add_query_param('RoleSessionName', 'sessiontest')
    # 指定STS临时访问凭证过期时间为3600秒。
    request.add_query_param('DurationSeconds', '3600')
    request.set_accept_format('JSON')

    body = clt.do_action_with_exception(request)

    # 使用RAM用户的AccessKey ID和AccessKey Secret向STS申请临时访问凭证。
    token = json.loads(oss2.to_unicode(body))
    # 打印STS返回的临时访问密钥（AccessKey ID和AccessKey Secret）、安全令牌（SecurityToken）以及临时访问凭证过期时间（Expiration）。
    print('AccessKeyId:' + token['Credentials']['AccessKeyId'])
    print('AccessKeySecret:' + token['Credentials']['AccessKeySecret'])
    print('SecurityToken:' + token['Credentials']['SecurityToken'])
    print('Expiration:' + token['Credentials']['Expiration'])
    return token

if __name__ == "__main__":
    # 直接调用函数
    print("开始获取STS Token...")
    try:
        token = get_sts_token()
        print("STS Token获取成功!")
    except Exception as e:
        print(f"获取STS Token失败: {e}")
    print("开始获取STS url...")
    try:
        url = ger_url()
        print("STS url获取成功!")
    except Exception as e:
        print(f"获取STS url失败: {e}")
