---
title: 加密算法还原
weight: 3
---

# 加密算法还原

逆向中最幸福的事：识别出网站用的是**标准算法**——直接用现成库复现即可。本章覆盖爬虫中最常见的四大类：摘要算法、对称加密、非对称加密、国密。

先用三个生活类比把三类加密的本质分清，后面见到密文才知道往哪个方向判断：

| 类别 | 类比 | 特点 | 典型用途 |
| ---- | ---- | ---- | -------- |
| 摘要算法（哈希） | **指纹**：人人都有，但无法从指纹还原出人 | 单向、不可逆、输出定长 | 签名、密码校验 |
| 对称加密 | **同一把钥匙开锁也关门**：加密解密用同一个密钥 | 可逆，密钥双方都要有 | 大数据量加密 |
| 非对称加密 | **信箱**：投递口（公钥）人人可见，取信钥匙（私钥）只有收件人有 | 可逆，公私钥成对 | 登录密码加密、数字签名 |

判断口诀：**能解密还原的是加密，不能还原的是哈希**。

::: danger 声明
本章内容仅供学习交流使用，严禁用于商业用途和非法用途。
:::

## 一、摘要算法（哈希）

特点：**单向加密不可逆**、输出**固定长度**（通常为 16 进制字符串）、明文有细微差异密文完全不同。常见：`MD5、SHA 系列、HMAC`。

### 1. MD5

128 位，通常表示为 32 个十六进制字符。

```javascript
// Node：npm install crypto-js
var CryptoJS = require('crypto-js');
console.log(CryptoJS.MD5('I love python!').toString());
```

```python
import hashlib

md5 = hashlib.md5()
md5.update('I love python!'.encode('utf-8'))
print(md5.hexdigest())
```

### 2. SHA 系列

比 MD5 更安全，密文更长：SHA-1（40 位）、SHA-224（56）、SHA-256（64）、SHA-384（96）、SHA-512（128）。**看到 40 位密文先猜 SHA-1，64 位先猜 SHA-256**，最终以断点调试为准。

```javascript
CryptoJS.SHA1(text).toString();
```

```python
import hashlib
print(hashlib.sha1(b'I love python!').hexdigest())
```

### 3. HMAC（带密钥的哈希）

要求通信双方共享密钥 key，是对「哈希 + 密钥」的组合：

```javascript
CryptoJS.HmacMD5(text, key).toString();
// CryptoJS.HmacSHA256(text, key).toString();
```

```python
import hmac

md5 = hmac.new(b'secret', 'I love python!'.encode(), digestmod='MD5')
print(md5.hexdigest())
```

### 4. 实战套路

抓包找到签名参数（如 `sign`、`code`）→ XHR 断点/关键字定位 → 分析拼接规则（往往是「参数 + 时间戳 + 盐值」再哈希）→ 用 Python 复现。例如某站签名规则 `md5(时间戳 + "9527" + 时间戳前 6 位)`：

```python
import hashlib
import time

n = str(int(time.time() * 1000))
value = n + '9527' + n[0:6]
print(hashlib.md5(value.encode()).hexdigest())
```

## 二、对称加密

加密与解密使用**同一个密钥**。常见：`DES`（56 位密钥，已渐弃用）、`AES`（128/192/256 位，主流）、`RC4`。

### 1. 分组工作模式

分组加密需要先把明文切成固定长度的块，模式决定块与块之间的关系：

| 模式 | 全称 | 特点 |
| ---- | ---- | ---- |
| **ECB** | 电子密码本 | 每块独立加密，最简单；相同明文块得到相同密文，安全性弱 |
| **CBC** | 密文分组链接 | 每块加密前与前一块密文异或，需要初始化向量 IV；**使用最多** |
| CFB | 密文反馈 | 流式加密，前一分组加密结果参与下一分组 |
| OFB | 输出反馈 | 与 CFB 类似，用密码序列自身迭代 |
| CTR | 计数器 | 对累加计数器加密生成密码流 |

解密侧：ECB/CBC 需要真正的解密运算；CFB/OFB/CTR 解密与加密过程相同（只是异或方向）。

**Padding 填充**：明文长度不是块大小整数倍时需填充，常见 `Pkcs7 / Pkcs5 / ZeroPadding / NoPadding`。语言间结果不一致多半是 padding 或编码差异。

### 2. JavaScript 实现（crypto-js）

```javascript
var CryptoJS = require('crypto-js');

var key = CryptoJS.enc.Utf8.parse('6f726c64f2c2057c');   // 密钥
var iv  = CryptoJS.enc.Utf8.parse('0123456789ABCDEF');    // 偏移量（CBC 需要）

var encrypted = CryptoJS.DES.encrypt(
    CryptoJS.enc.Utf8.parse('I love Python!'),
    key, { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
);
console.log(encrypted.toString());        // Base64 密文
```

把 `DES` 换成 `AES`、`mode` 换成 `mode.ECB` 即可切换算法与模式——**逆向时进函数看这几个属性就知道用了什么组合**。

### 3. Python 实现

```bash
pip install pycryptodome
```

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

key = b'0123456789ABCDEF'                 # 16 字节 = AES-128
iv  = b'0123456789ABCDEF'

def aes_encrypt(text):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = pad(text.encode(), AES.block_size)
    return base64.b64encode(cipher.encrypt(data)).decode()

def aes_decrypt(b64text):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    data = base64.b64decode(b64text)
    return unpad(cipher.decrypt(data), AES.block_size).decode()
```

### 4. AES / DES 特征识别

- 密文是标准 Base64 / 16 进制
- 断点进入加密函数后看到 `mode`、`padding`、`iv` 字样基本可以确认
- 密钥通常来自：写死在 JS 里、接口下发、或由其他参数派生——**先确认密钥来源再复现**

::: tip
不同语言/库对同一算法的实现可能有细微差异（如 padding 默认值），逆向时优先用 **Node 跑网站同款 crypto-js**，而不是强行用 Python 复刻。
:::

## 三、非对称加密

使用一对密钥：**公钥加密、私钥解密**（或反过来用于签名）。私钥只保存在接收方，不在网络上传输。计算复杂、速度慢，通常只加密短内容（如登录密码）。常见：`RSA、DSA`。

### 1. JS 侧特征

- 搜索关键字 `new JSEncrypt()`、`setPublicKey`、`setPrivateKey`、`encrypt`
- 一般使用 JSEncrypt 库：`new JSEncrypt()` → `setPublicKey(公钥)` → `encrypt(明文)`
- 公钥是一段 Base64 长字符串，抓包或 JS 里直接可见

密文长度有对应关系（可辅助判断是否 RSA）：

| 公钥长度 | 明文长度上限 | 密文长度 |
| -------- | ------------ | -------- |
| 128 | 1~53 | 88 |
| 216 | 1~117 | 172 |
| 392 | 1~245 | 344 |

### 2. 复现方式

**方式一：用 jsencrypt 库原样复现（推荐，与网站一致）**

```javascript
// npm install jsencrypt
var JSEncrypt = require('jsencrypt');

function encrypt(pwd) {
    var publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GN...';   // 从 JS 里扣出的公钥
    var enc = new JSEncrypt();
    enc.setPublicKey(publicKey);
    return enc.encrypt(pwd);
}
console.log(encrypt('12345'));
```

**方式二：Python rsa / pycryptodome**

```python
import rsa
import base64

def rsa_encrypt(public_key_pem, text):
    pub = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_pem.encode())
    return base64.b64encode(rsa.encrypt(text.encode(), pub))

# 或 pycryptodome：
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

key = RSA.import_key(public_key_pem)
cipher = PKCS1_v1_5.new(key)
print(base64.b64encode(cipher.encrypt(b'12345')))
```

::: warning
RSA 有 pkcs1 / pkcs8、PKCS1_v1_5 / OAEP 等多种填充格式，Python 侧结果对不上时优先换用 Node + jsencrypt 原样跑。
:::

## 四、国密 SM 系列

国家密码管理局发布的商用密码算法，部分网站（尤其政务、医疗类）会使用：

| 算法 | 类别 | 说明 |
| ---- | ---- | ---- |
| SM2 | 非对称（ECC 椭圆曲线） | 256 位强度超过 RSA-2048，用于替换 RSA |
| SM3 | 散列 | 安全性与效率与 SHA-256 相当 |
| SM4 | 对称分组 | 128 位密钥/分组，32 轮迭代，替换 DES/AES |
| SM9 | 标识加密 | 强度等同 3072 位 RSA |
| ZUC | 序列密码 | 4G 移动通信 |

### 1. JavaScript（sm-crypto 库）

```javascript
// npm install sm-crypto
const sm2 = require('sm-crypto').sm2;
const sm3 = require('sm-crypto').sm3;
const sm4 = require('sm-crypto').sm4;

// SM2：cipherMode 1 = C1C3C2（新标准），0 = C1C2C3
let keypair = sm2.generateKeyPairHex();
let encData = sm2.doEncrypt(msg, keypair.publicKey, 1);
let decData = sm2.doDecrypt(encData, keypair.privateKey, 1);

// SM3
console.log(sm3('Hello, SM3!'));

// SM4
let ct = sm4.encrypt('Hello, SM4!', key, { mode: 'ecb' });
let pt = sm4.decrypt(ct, key, { mode: 'ecb' });
```

### 2. Python（gmssl 库）

```bash
pip install gmssl
```

```python
from gmssl import sm2, sm3, sm4, func

# SM2
sm2_crypt = sm2.CryptSM2(public_key=public_key_hex, private_key=private_key_hex)
enc = sm2_crypt.encrypt(b'data')

# SM3（入参是字节列表）
print(sm3.sm3_hash(func.bytes_to_list(b'123')))

# SM4
c = sm4.CryptSM4()
c.set_key(key, sm4.SM4_ENCRYPT)
ct = c.crypt_ecb(func.bytes_to_list(b'Hello, SM4!'))
```

::: tip
SM2 密文由 C1（随机椭圆曲线点）、C2（密文）、C3（SM3 摘要）组成，新旧标准的排列顺序不同（C1C2C3 / C1C3C2）；Python gmssl 与网站结果不一致时先检查顺序与是否带 `04` 前缀。
:::

## 五、算法识别速查表

| 线索 | 判断 |
| ---- | ---- |
| 32 位 hex | MD5（或 MD5 后截取） |
| 40 / 64 / 128 位 hex | SHA-1 / SHA-256 / SHA-512 |
| 标准 Base64，且 JS 里出现 `setPublicKey` | RSA |
| Base64，JS 里出现 `mode`、`iv`、`Pkcs7` | AES/DES（看进函数后的算法名） |
| JS 里出现 `sm2` / `sm4` / `doEncrypt` | 国密 |
| 每次请求密钥变化 | 密钥可能由接口下发或时间戳派生，先抓包看前置请求 |

## 六、小结

- 摘要算法直接 `hashlib`/`hmac` 复现，重点还原**拼接顺序与盐值**
- 对称加密确认四要素：**算法（AES/DES）、模式（ECB/CBC）、密钥、IV/Padding**
- 非对称加密扣出公钥，用 jsencrypt 原样跑最稳
- 优先识别标准算法 → 库复现；识别不出再走「扣代码 / 补环境」（后续章节）
