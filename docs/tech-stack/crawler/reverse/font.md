---
title: 字体反爬
weight: 7
---

# 字体反爬

## 一、原理

字体反爬的本质是利用前端技术「**显示与源码不一致**」：

- 页面上数字/文字显示正常
- 但源码里抓到的是乱码、问号或 `&#xe621;` 这类私有编码

技术根基是 CSS3 的 `@font-face` 规则：开发者可以把自定义字体文件放在 Web 服务器上，CSS 中引用后，用户浏览器访问页面时会自动下载该字体。**浏览器渲染时用自定义字体的「字形」替换标准字形**——比如让编码 `0xe621` 画出来的样子是「5」。

由于替换发生在渲染层，所以：

- ✅ 人眼看页面完全正常
- ❌ 爬虫拿到的源码是原始编码
- ❌ 甚至 Selenium 拿到的 `page_source` 也是乱的（它拿的是源码而非视觉结果）

## 二、字体文件基础

| 格式 | 说明 |
| ---- | ---- |
| TTF | Windows 传统字体标准，macOS 也支持 |
| OTF | 开放字体格式，支持完整 Unicode |
| WOFF | **网页专用格式**（woff/woff2），本质是压缩的 TTF/OTF，网页反爬最常见 |
| EOT | 早期 IE 使用，已淘汰 |
| TTC | 字体集合，一个文件含多个字体 |

字体文件内部以「表」组织数据：

| 表 | 作用 |
| ---- | ---- |
| `cmap` | **字符编码 → 字形名** 的映射（反爬核心） |
| `glyf` | 字形的轮廓坐标数据 |
| `head` / `hhea` / `hmtx` | 字体标题、水平标题与指标 |
| `loca` / `maxp` / `name` / `post` | 索引、上限、命名等信息 |

## 三、定位与解析字体文件

### 1. 确认字体加密

特征：网页显示正常，源码里对应位置是 `&#xe621;` 或乱码。典型站点如实习僧。

### 2. 找到字体文件 URL

在 DevTools 元素面板全局搜索 `@font-face`，找到 `src: url(...)` 指向的字体文件地址，直接下载（有的需要自己补上 `.woff` 后缀）：

```css
@font-face {
    font-family: myFont;
    src: url(https://www.example.com/xxx.woff);
}
```

### 3. 查看映射关系

- **在线工具**：font.qqe2.com，把字体文件拖进去即可看到每个编码对应的字形
- **fontTools 解析**（程序化处理）：

```bash
pip install fontTools
```

```python
from fontTools.ttLib import TTFont

# 加载字体文件
font = TTFont('file.woff')
font.saveXML('file.xml')        # 导出 XML，查看字形轮廓、字符映射等

# 编码 → 字形名 映射（cmap 表）
print(font.getBestCmap())
# 例如：{0xe621: 'uniE621', 0x4e94: 'uni4E94', ...}

# 查看某个字形的轮廓坐标
glyf = font['glyf']
print(glyf['uni4E94'].coordinates)
```

### 4. 建立映射表

在线预览每个字形长什么样（哪个编码画的是「5」、哪个是「9」），人工标注一次得到基准映射表：

```python
mapping = {
    '&#xe621;': '5',
    '&#xe622;': '9',
    ...
}
```

把响应文本里的编码替换成真实字符，再走正常的解析流程。

## 四、实战：实习僧字体反爬

完整流程：请求页面 → 提取并下载字体文件 → 解析 cmap 建映射 → 替换文本 → XPath 解析。

```python
import re
import requests
from lxml import etree
from fontTools.ttLib import TTFont

class SXS:
    def __init__(self):
        self.url = 'https://www.shixiseng.com/interns?keyword=IT&city=%E5%85%A8%E5%9B%BD'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

    def get_data(self):
        res = requests.get(self.url, headers=self.headers)
        # 1. 正则提取 @font-face 里的字体 URL
        ttf = 'https://www.shixiseng.com' + re.findall(
            r'">@font-face {    font-family: myFont;    src: url\((.*?)\);}', res.text)[0]
        # 2. 下载字体文件
        with open('file.woff', 'wb') as f:
            f.write(requests.get(ttf).content)
        # 3. 保存页面源码（后面替换用）
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(res.text)

    def get_font_data(self):
        """构建 &#x编码 → 真实字符 的映射表"""
        font_dict = {}
        for k, v in TTFont('file.woff').getBestCmap().items():
            if v[3:]:
                # 字形名 uniE621 → \ue621 → 对应字符
                content = '\\u00' + v[3:] if len(v[3:]) == 2 else '\\u' + v[3:]
                real_content = content.encode('utf-8').decode('unicode_escape')
                k_hex = hex(k).replace('0x', '&#x')    # 网页里是 &#x 开头
                font_dict[k_hex] = real_content
        return font_dict

    def parse_data(self, font_dict):
        with open('index.html', encoding='utf-8') as f:
            data = f.read()
        # 4. 逐个替换编码
        for k, v in font_dict.items():
            data = data.replace(k, v)
        # 5. 替换完成后正常解析
        html = etree.HTML(data)
        for i in html.xpath('//div[@class="clearfix intern-detail"]'):
            comp = i.xpath('./div/p/a[@class="title ellipsis"]/text()')[0]
            price = i.xpath('.//span[@class="day font"]/text()')[0]
            title = i.xpath('.//div[@class="f-l intern-detail__job"]/p/a[1]/text()')[0]
            print(comp, price, title)

    def main(self):
        self.get_data()
        font_dict = self.get_font_data()
        self.parse_data(font_dict)


if __name__ == '__main__':
    SXS().main()
```

## 五、进阶：动态字体映射

静态映射表只能对付**固定字体**的网站。进阶网站会**动态生成字体**：每次请求返回不同的字体文件，同一个编码这次画「5」、下次可能画「8」，映射表直接失效。

### 应对思路：字形坐标比对

思路：预先人工标注一套**基准字体**（每个字符的 `glyf` 坐标已知），每次请求时下载新字体，把它的字形坐标与基准库比对，**坐标几乎一致的即为同一字符**：

```python
def recognize(font_path, base_mapping):
    """base_mapping: {字符: 坐标元组}"""
    font = TTFont(font_path)
    result = {}
    for code, name in font.getBestCmap().items():
        if not name.startswith('uni'):
            continue
        coords = tuple(font['glyf'][name].coordinates) if name in font['glyf'] else None
        if coords is None:
            continue
        for char, base_coords in base_mapping.items():
            # 坐标允许少量误差
            if close_enough(coords, base_coords):
                result[hex(code).replace('0x', '&#x')] = char
                break
    return result
```

要点：

- 比对时可以忽略整体平移（有的网站会给字形加随机偏移），比较**相对坐标或归一化后的坐标**
- 也可以用 OCR 思路：把字形渲染成图片，用 `ddddocr` 识别——适合懒得建坐标库的情况
- 猫眼票房（piaofang.maoyan.com/dashboard）是经典的动态字体练习站

## 六、其他变体

- **CSS 伪元素反爬**：部分字符藏在 `::before { content: ... }` 里，需要解析 CSS
- **拼接反爬**：数字被拆成多个 span，通过 CSS `background-position` 拼图显示，需要按背景偏移还原
- **SVG 反爬**：字符用 SVG 路径渲染，`<use xlink:href>` 引用 path，需解析 SVG 映射

它们与字体反爬同理：**渲染结果 ≠ 源码**，找到「显示值 ↔ 源码值」的映射关系即可破解。

## 七、小结

| 类型 | 破解方式 |
| ---- | -------- |
| 静态字体 | 下载 woff → fontTools 读 cmap → 人工标注一次建立固定映射表 |
| 动态字体 | 下载 woff → 与基准字体比对 `glyf` 坐标（或渲染成图 OCR） |
| CSS/SVG 变体 | 解析 CSS content / SVG path 映射 |

记住核心公式：**字体反爬 = 源码编码 + 字体文件 → 真实字符**，一切工作都围绕建立这个映射展开。
