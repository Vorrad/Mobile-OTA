# uptane.services.timeserver

# def get_time(nonces):

time格式为
time_attestation = {
    'time': clock,
    'nonces': nonces
  }


## def get_signed_time_der(nonces):

与 get_signed_time 相同，但将生成的 Python 字典转换为 ASN.1 表示，将其编码为 DER（可分辨编码规则），将签名替换为数据“签名”部分的 DER 编码散列上的签名（ 时间和随机数）。

uptane.formats

uptane.common

使用这些库进行签名和格式转化