---
inHomePost: false
title: Python 处理 json 数据
---

# Python 处理 json 数据

读写 `json` 文件主要用到 `json` 库中的 `dump` 和 `load` 方法，而解析 `json` 字符串主要用到 `json` 库中的 `dumps` 和 `loads` 方法。二者极易弄混淆。


```python
import json
```

## 读写 json 文件

`json` 库中的 `load` 方法和 `dump` 方法架起了沟通 `json` 文件（本质上是文本文件）和 **Python** 字典数据类型的桥梁。

示例文件`./src/settings.json`的内容：


```python
!cat ./src/settings.json
```

    {
        "editor.acceptSuggestionOnEnter": "off",
        "editor.fontFamily": "Consolas-with-Yahei",
        "editor.fontSize": 20,
        "markdownlint.config": {
            "MD025": {
                "front_matter_title": ""
            }
        }
    }

读取文件，**Python**将文件的文本内容转化为字典：


```python
f = open('./src/settings.json', 'r')
json_reader = json.load(f)
f.close()

type(json_reader), json_reader
```


    (dict,
     {'editor.acceptSuggestionOnEnter': 'off',
      'editor.fontFamily': 'Consolas-with-Yahei',
      'editor.fontSize': 20,
      'markdownlint.config': {'MD025': {'front_matter_title': ''}}})

键值对的索引：


```python
json_reader['markdownlint.config']['MD025']
```


    {'front_matter_title': ''}

要想修改 `json` 文件，只需要对解析后的 **Python** 字典做类似操作即可：


```python
json_reader['markdownlint.config']['MD025'] = {'formatter': 'Atom', 'index': [1, 3, 5, 7, 9]}
json_reader
```


    {'editor.acceptSuggestionOnEnter': 'off',
     'editor.fontFamily': 'Consolas-with-Yahei',
     'editor.fontSize': 20,
     'markdownlint.config': {'MD025': {'formatter': 'Atom',
       'index': [1, 3, 5, 7, 9]}}}

写入 `json` 文件的内容通常也是 **Python** 字典数据类型：


```python
with open('./out/settings_new.json', 'w') as f:
    json_writer = json.dump(json_reader, f)
```

写入文件的内容：


```python
!cat ./out/settings_new.json
```

    {"editor.acceptSuggestionOnEnter": "off", "editor.fontFamily": "Consolas-with-Yahei", "editor.fontSize": 20, "markdownlint.config": {"MD025": {"formatter": "Atom", "index": [1, 3, 5, 7, 9]}}}

可以让 `json` 字符串格式化写入文件：


```python
with open('./out/settings_new.json', 'w') as f:
    json_writer = json.dump(json_reader, f, sort_keys=True, indent=4, separators=(',', ': '))
```

此时文件的内容就格式化了，非常美观：


```python
!cat ./out/settings_new.json
```

    {
        "editor.acceptSuggestionOnEnter": "off",
        "editor.fontFamily": "Consolas-with-Yahei",
        "editor.fontSize": 20,
        "markdownlint.config": {
            "MD025": {
                "formatter": "Atom",
                "index": [
                    1,
                    3,
                    5,
                    7,
                    9
                ]
            }
        }
    }

## 解析 json 字符串

`json` 库中的 `loads` 方法和 `dumps` 方法架起了沟通 `json` 字符串（本质上是 **Python** 字符流）和 **Pyhon** 字典数据类型的桥梁。


```python
data = {
    'id_list': [1, 2, 3, 4],
    'address': 'Beijing'
}
json_data = json.dumps(data)

type(json_data), json_data
```


    (str, '{"id_list": [1, 2, 3, 4], "address": "Beijing"}')

`dict` 编码为 `json` 后，**Python** 解释器认为它就和字符串一样了。

同理，可以用 `loads` 方法将 `json` 格式的字符串转化为 **Python** 字典数据类型。


```python
string = '{"username": "root", "password": "123456"}'
dict_data = json.loads(string)

type(dict_data), dict_data
```


    (dict, {'username': 'root', 'password': '123456'})
