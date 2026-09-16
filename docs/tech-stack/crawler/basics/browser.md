---
title: Selenium 浏览器自动化
weight: 6
---

# Selenium 浏览器自动化

Selenium 是自动化测试工具，能驱动浏览器执行打开网页、点击、输入等动作，并获取**浏览器渲染后**的页面源码，做到「所见即所爬」。对于 JS 动态渲染、接口加密难以还原的页面，让浏览器把动态数据变成静态 HTML 再提取，是绕过反爬的兜底方案。

## 一、环境准备

```bash
pip install selenium
```

1. 安装 Chrome 浏览器；
2. 安装与浏览器版本匹配的 ChromeDriver 驱动（放入环境变量目录）；
3. Selenium 4.6+ 支持自动下载驱动（Selenium Manager），老版本需手动下载。

::: warning
驱动版本必须与浏览器版本对应，否则无法启动；可通过关闭系统服务的浏览器自动更新来锁定版本。
:::

## 二、基本使用

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

browser = webdriver.Chrome()          # 也支持 Firefox / Edge
browser.get('https://www.baidu.com/')

# 定位搜索框并输入
browser.find_element(By.NAME, 'wd').send_keys('selenium')
# 定位「百度一下」按钮并点击
browser.find_element(By.ID, 'su').click()

print(browser.page_source)            # 渲染后的页面源码
print(browser.get_cookies())          # Cookie
print(browser.current_url)            # 当前 URL
browser.get_screenshot_as_file('1.png')   # 截图

time.sleep(5)
browser.quit()
```

## 三、初始化配置 Options

```python
from selenium import webdriver

options = webdriver.ChromeOptions()
# 无头模式（后台运行，服务器上必备）
options.add_argument('--headless')
# 不加载图片，加快速度
prefs = {'profile.managed_default_content_settings.images': 2}
options.add_experimental_option('prefs', prefs)
# 自定义 UA
options.add_argument('user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)...')
# 去掉「Chrome 正受到自动软件控制」的提示条
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# 设置代理
# options.add_argument('--proxy-server=http://58.20.184.187:9091')

browser = webdriver.Chrome(options=options)
browser.maximize_window()             # 最大化
browser.set_window_size(480, 800)     # 模拟移动端尺寸
```

## 四、节点定位

Selenium 4 统一使用 `find_element(By.X, value)` 定位单个节点、`find_elements` 定位一组节点（返回列表）：

```python
from selenium.webdriver.common.by import By

browser.find_element(By.ID, 'kw')                      # id
browser.find_element(By.NAME, 'wd')                    # name
browser.find_element(By.CSS_SELECTOR, 'input.s_ipt')   # CSS 选择器
browser.find_element(By.XPATH, '//input[@id="kw"]')    # XPath
browser.find_element(By.CLASS_NAME, 's_ipt')           # class
browser.find_element(By.LINK_TEXT, '新闻')              # 链接文本

lis = browser.find_elements(By.CSS_SELECTOR, '#NewsListContainer li')   # 一组节点
```

## 五、节点交互与动作链

### 1. 常用交互

```python
from selenium.webdriver.common.keys import Keys

input_ = browser.find_element(By.ID, 'kw')
input_.send_keys('iPhone')       # 输入
time.sleep(1)
input_.clear()                   # 清空
input_.send_keys('iPad')
input_.send_keys(Keys.ENTER)     # 模拟回车
browser.find_element(By.ID, 'su').click()   # 点击
```

### 2. 动作链（拖拽等）

```python
from selenium.webdriver import ActionChains

actions = ActionChains(browser)
actions.drag_and_drop(source_element, target_element)   # 从 source 拖到 target
actions.perform()                                       # 执行动作
```

### 3. 用 JS 实现页面滚动

Selenium API 没有提供下拉进度条，但可以借 `execute_script` 执行任意 JS：

```python
import random, time

# 模拟人工慢慢下拉（触发懒加载）
for i in range(1, 9):
    time.sleep(random.randint(100, 300) / 1000)
    browser.execute_script(f'window.scrollTo(0, {i * 700})')

# 滚动到底部
browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
```

### 4. 获取节点信息

```python
for img in browser.find_elements(By.XPATH, '//ul[@class="clearfix"]/li/a/img'):
    print(img.get_attribute('src'))     # 取属性
    print(img.text)                     # 取文本
```

## 六、切换 iframe

iframe（内联框架）相当于页面中的「**套娃**」：主文档是一层世界，iframe 是嵌在里面的另一个独立世界，有自己完整的 HTML 结构，两层 DOM 互相隔离。Selenium 默认只在父级 Frame 里操作，**iframe 里的节点必须先切换进去才能定位**——直接 `find_element` 只会报 `NoSuchElementException`，这是新手最常踩的坑（定位半天找不到元素，先检查是不是在 iframe 里）：

```python
browser.get('https://www.douban.com/')
login_iframe = browser.find_element(By.XPATH, '//div[@class="login"]/iframe')
browser.switch_to.frame(login_iframe)     # 切入 iframe

browser.find_element(By.ID, 'username').send_keys('account')
browser.switch_to.default_content()       # 切回主文档
```

## 七、延时等待

`get()` 只等页面框架加载完，Ajax 数据可能还没到。等待有三种方式，务必分清：

| 方式 | 写法 | 问题/特点 |
| ---- | ---- | -------- |
| 强制等待 | `time.sleep(3)` | 死等固定秒数：等短了没加载出来，等长了浪费时间 |
| 隐式等待 | `browser.implicitly_wait(10)` | 全局生效：找节点最多等 10 秒，但无法针对特定条件 |
| **显式等待** | `WebDriverWait` + 条件 | 针对某个节点等到「满足条件」为止，最可靠（推荐） |

显式等待指定节点与条件，在规定时间内条件满足就立刻返回，超时才抛异常：

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

browser.get('https://www.baidu.com/')
wait = WebDriverWait(browser, 10)     # 最长等 10 秒
input_ = wait.until(EC.presence_of_element_located((By.ID, 'kw')))        # 节点加载出
button = wait.until(EC.element_to_be_clickable((By.ID, 'su')))            # 可点击
```

常用等待条件：`presence_of_element_located`（节点加载出）、`visibility_of_element_located`（可见）、`element_to_be_clickable`（可点击）、`frame_to_be_available_and_switch_to_it`（iframe 加载并切入）、`alert_is_present`（弹窗出现）等。

## 八、选项卡管理与异常处理

```python
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException

browser = webdriver.Chrome()
browser.get('https://www.baidu.com')

# 新开并切换选项卡
browser.execute_script('window.open()')
print(browser.window_handles)                          # 所有选项卡句柄
browser.switch_to.window(browser.window_handles[1])    # 切到第二个
browser.get('https://pic.netbian.com')
browser.switch_to.window(browser.window_handles[0])    # 切回第一个

# 异常捕获
try:
    browser.find_element(By.ID, 'not_exist')
except NoSuchElementException:
    print('节点未找到')
except TimeoutException:
    print('加载超时')
finally:
    browser.quit()
```

## 九、绕过检测

部分网站能通过 `navigator.webdriver` 等特征识别 Selenium（可用 bot.sannysoft.com 自测），处理方式：

```python
options = webdriver.ChromeOptions()
# 方式一：禁用自动化特征
options.add_argument('--disable-blink-features=AutomationControlled')
browser = webdriver.Chrome(options=options)

# 方式二：注入 stealth.min.js 隐藏浏览器特征
with open('stealth.min.js') as f:
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                            {'source': f.read()})
```

## 十、实战：采集唯品会商品

流程：搜索关键词 → 模拟下拉触发加载 → 提取商品列表 → 翻页 → 入库。

```python
import time
import random
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WeiPin:
    def __init__(self):
        self.col = MongoClient()['spiders']['weipinhui']
        options = webdriver.ChromeOptions()
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)

    def base(self):
        self.browser.get('https://www.vip.com/')
        wait = WebDriverWait(self.browser, 10)
        box = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//input[@class="c-search-input J-search-input"]')))
        box.send_keys('口红')
        time.sleep(random.randint(3000, 3400) / 1000)          # 随机延迟拟人化
        self.browser.find_element(By.XPATH, '//a[contains(@class,"c-search-button")]').click()
        time.sleep(random.randint(1000, 1400) / 1000)

    def drop_down(self):
        for x in range(1, 10):
            self.browser.execute_script(f'document.documentElement.scrollTop={x * 1000}')
            time.sleep(random.randint(500, 800) / 1000)

    def spider(self):
        self.drop_down()
        nodes = self.browser.find_elements(
            By.XPATH, '//section[@id="J_searchCatList"]/div[contains(@class,"c-goods-item")]')
        for node in nodes:
            item = {
                'title': node.find_element(By.XPATH, './/div[2]/div[2]').text,
                'price': node.find_element(By.XPATH, './/div[contains(@class,"sale-price")]').text,
            }
            print(item)
            self.col.insert_one(item)
        self.page_next()

    def page_next(self):
        try:
            self.browser.find_element(By.XPATH, '//*[@id="J_nextPage_link"]').click()
            self.spider()                       # 递归翻页
        except Exception:
            self.browser.quit()

if __name__ == '__main__':
    w = WeiPin()
    w.base()
    w.spider()
```

## 十一、小结与扩展

- Selenium 适合：动态渲染页面、需要登录交互、接口复杂难以直接还原的场景
- 代价是速度慢、资源占用高，能用接口就优先用接口
- 关键技巧：显式等待 + 拟人化延迟 + JS 滚动触发懒加载 + iframe 切换
- 现代替代品 **Playwright** 支持 Chrome/Firefox/WebKit、自动等待、拦截网络请求（`page.on('response')` 可直接拿到加密前的接口数据），新项目值得关注
