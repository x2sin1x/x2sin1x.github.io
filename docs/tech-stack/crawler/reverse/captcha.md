---
title: 验证码
weight: 10
---

# 验证码

## 一、验证码简介

验证码的目的是区分「人」与「机器」。对爬虫而言，重点是**识别滑块缺口、测出拖动距离**，并还原验证接口的加密协议。

### 1. 滑块验证码的原理

1. 后台从图库随机取一张图，在随机 `(x, y)` 坐标按宽高抠出一块区域
2. 用二维数组保存抠图区域的像素坐标，对原图该区域做阴影/缺口处理
3. 得到两张图（**抠下的方块图** + **带缺口阴影的原图**）和缺口 y 坐标，连同 `token`（验证码唯一标识，后台缓存）一起下发给前端
4. 用户滑动方块后，前端把移动后的 **x 坐标 + token + 轨迹**提交
5. 后台根据 token 取出原始 x 坐标对比，在阈值内则验证通过

### 2. 突破的三种方式

| 方式 | 说明 |
| ---- | ---- |
| 机器学习识别缺口 | 需要标注与训练，成本高 |
| **像素对比 / OCR 识别** | 完整图与缺口图对比定位，ddddocr 开箱即用（主流） |
| 打码平台 | 花钱人工/AI 识别，稳定省事 |

## 二、常见验证码平台

| 平台 | 特点 |
| ---- | ---- |
| 网易易盾 | 滑块、点选，协议分析练手首选 |
| 极验（geetest） | 滑块、点选、图标，版本多 |
| 顶象 / 同盾 / 数美 | 风控一体，轨迹与环境检测强 |
| 腾讯 TCaptcha / 阿里 | 大厂系 |
| VAPTCHA | 手势验证 |
| AJ 验证码 | 开源，只有滑块与点选两种，**无轨迹校验，最简单** |
| reCAPTCHA / hCaptcha / FunCaptcha | 国际三剑客，专业打码平台（如 YesCaptcha）处理 |

自研验证码（小公司）最简单，直接分析接口即可。

## 三、滑块识别：ddddocr

```bash
pip install ddddocr
```

```python
import requests
import ddddocr

# 1. 下载滑块图与背景图（URL 从验证码接口的响应里提取）
res = requests.get('https://necaptcha.nosdn.127.net/xxx.jpg')
open('full.png', 'wb').write(res.content)        # 完整背景图

res = requests.get('https://necaptcha.nosdn.127.net/yyy.png')
open('bg.png', 'wb').write(res.content)          # 滑块图

# 2. slide_match 匹配缺口位置
det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
with open('bg.png', 'rb') as f:
    target = f.read()
with open('full.png', 'rb') as f:
    background = f.read()

res = det.slide_match(target, background)
print(res)      # {'target': [x, y, w, h]} → x 即滑动距离
```

## 四、文字点选识别

点选类验证码要求按语序点击图中文字，需要返回每个字的坐标，通常交给打码平台（云码 jfbym、超级鹰等）：

```python
import base64
import json
import requests

class YdmVerify:
    _custom_url = 'http://api.jfbym.com/api/YmServer/customApi'
    _token = '你的 token'
    _headers = {'Content-Type': 'application/json'}

    def click_verify(self, image, extra=None, verify_type='30103'):
        payload = {
            'image': base64.b64encode(image).decode(),
            'extra': 'click',
            'token': self._token,
            'type': verify_type,
        }
        resp = requests.post(self._custom_url, headers=self._headers,
                             data=json.dumps(payload))
        return resp.json()['data']['data']    # 返回坐标列表
```

## 五、协议分析实战：网易易盾滑块

以易盾为例走完整流程。两个关键接口：

- `GET https://c.dun.163.com/api/v3/get` —— 获取验证码图片与 token
- `GET https://c.dun.163.com/api/v3/check` —— 提交轨迹验证，核心加密参数 `data`

### 1. get 接口：cb 参数

`get` 接口的 `cb` 参数由 JS 环境指纹加密生成（自定义字节变换 + CRC32 + 自定义 Base64 字符表），需要整体扣代码到本地执行：

```python
import time
import requests
import execjs

cb = execjs.compile(open('易盾.js', encoding='utf8').read()).call('get_cb')

params = {
    'referer': 'https://dun.163.com/trial/jigsaw',
    'id': '07e2387ab53a4d6f930b8d9a9be71bdf',
    # fp 是环境指纹串 + 毫秒时间戳
    'fp': 'EKPkw0M6...' + str(int(time.time() * 1000)),
    'https': 'true', 'type': '2', 'version': '2.28.0',
    'dpr': '1.25', 'dev': '1', 'cb': cb, 'width': '320',
    'runEnv': '10', 'lang': 'zh-CN', ...
}
response = requests.get('https://c.dun.163.com/api/v3/get',
                        headers=headers, params=params)
# 响应是 JSONP：__JSONP_xxx({...})，手动剥离取 JSON
text = response.text
json_data = json.loads(text[text.index('(') + 1:text.rindex(')')])

token = json_data['data']['token']
slider_url = json_data['data']['front'][0]      # 滑块图
background_url = json_data['data']['bg'][0]     # 背景图
```

### 2. check 接口：data 参数

`data` 由三部分加密数据组成（JS 里扣出的逻辑，均依赖 token）：

```javascript
function get_data(guiji, token, slider_x) {
    // 1. 轨迹逐点加密：_f8(token, 坐标)
    guiji_list = get_guiji(guiji, token)
    // 2. 轨迹采样 50 个点
    Z = window._y.sample(guiji_list, 50)
    // 3. 终点 x 换算百分比后加密
    H = window._f8(token, parseInt(`${slider_x}px`, 10) / 320 * 100 + '')
    // 4. 二维轨迹数组的全量特征
    f0 = window._G(window._y.unique2DArray(guiji, 2))
    return JSON.stringify({
        d: window._ff(Z.join(':')),                        // 采样轨迹
        m: '',
        p: H,                                              // 滑动终点（百分比）
        f: window._ff(window._f8(token, f0.join(','))),    // 全量轨迹特征
        ext: window._ff(window._f8(token, '1,' + guiji_list.length)),
    })
}
```

可见除了缺口位置，**轨迹本身**也参与校验——匀速直线滑动会被判定为机器。

### 3. 轨迹生成

真实滑动轨迹 = 贝塞尔曲线 + 随机抖动 + 先快后慢的加速度曲线。可自写贝塞尔轨迹发生器，或使用现成 `cBezier` 等库生成 `[(x1,y1,t1), (x2,y2,t2), ...]` 数组。

### 4. Python 串联全流程

```python
import random
import time
import ddddocr
import requests
import execjs
from cBezier import bezierTrajectory

class YD:
    def dddd_ocr(self, slider_bytes, background_bytes):
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        res = det.slide_match(slider_bytes, background_bytes)
        return res['target'][0]                    # 缺口 x

    def run(self):
        for i in range(10):
            # ① 获取图片与 token
            slider_bytes, background_bytes = self.get_image()
            # ② 识别缺口距离
            slider_x = self.dddd_ocr(slider_bytes, background_bytes)
            # ③ 生成拟人轨迹
            guiji = bezierTrajectory().generate_gj(slider_x + 10)
            time.sleep(2)
            # ④ 加密轨迹并提交 check
            self.check(guiji, slider_x + 10)
```

### 5. 补环境与调试

验证码 JS 同样有环境检测，Node 侧按标准流程补：

```javascript
window = global;
navigator = { userAgent: 'Mozilla/5.0 ...' };
document = {
    createElement: function (args) {
        if (args === 'div') {
            return { getAttribute: function () {}, addEventListener: function () {} };
        }
    },
    getElementById: function () {},
};
location = { href: 'https://dun.163.com/trial/jigsaw', host: 'dun.163.com', ... };
setTimeout = function () {};
setInterval = function () {};
// 再挂 Proxy 吐环境，按日志补齐
```

## 六、其他类型的思路

| 类型 | 思路 |
| ---- | ---- |
| 图形算术（4+3=?） | OCR / ddddocr 分类模型识别 |
| 点选语序题 | 打码平台返回坐标 + 保留点击顺序 |
| 空间推理（3D 旋转） | 打码平台或专用模型 |
| reCAPTCHA v2/v3 | YesCaptcha 等专业平台，或 cookie 复用方案 |
| AJ（开源） | 无轨迹校验，识别缺口 + 直接提交即可 |

## 七、小结

验证码逆向公式：**图片识别（缺口/点选） + 轨迹生成 + 协议参数加密**。

- 图片识别：ddddocr 优先，复杂类型上打码平台
- 轨迹：贝塞尔曲线 + 随机抖动，模拟人的加减速
- 协议：抓 get/check 接口 → Hook/断点定位加密参数（data、cb 等）→ 扣代码 + 补环境 → Python 串联
- 高强度平台（数美、顶象）还会校验环境指纹与鼠标行为熵，届时结合补环境与 RPC 手段
