## 简介

- 在控制台中用于彩色打印的包
- 采用的是亮色
- 支持多值打印
- 支持使用十六进制颜色值（如 `"FF00FF"` 或 `"#00FF00"`）打印对应颜色的文字

## 安装

```
pip install --index-url https://pypi.org/simple colorPrintConsole -U
```

## 使用

```python
from colorPrintConsole import ColorPrint, cp

# 推荐用法1：直接用 ColorPrint 类
cp1 = ColorPrint()
cp1.red("This is red.")
cp1.green("This is green.")
cp1.yellow("This is yellow.")
cp1.blue("This is blue.")
cp1.magenta("This is magenta.")
cp1.cyan("This is cyan.")
cp1.red("123", "456", "789")  # 多值打印
cp1.color_hex("FFC0CB", "This is pink.")  # 自定义十六进制颜色值
cp1.color_hex("#800080", "This is purple.")  # 自定义十六进制颜色值

# 推荐用法2：直接用 cp 单例对象
cp.red("This is red.")
cp.green("This is green.")
cp.yellow("This is yellow.")
cp.blue("This is blue.")
cp.magenta("This is magenta.")
cp.cyan("This is cyan.")
cp.color_hex("FFC0CB", "This is pink.")
cp.color_hex("#800080", "This is purple.")
```

## 展示

![效果展示1](https://img-1256814817.cos.ap-beijing.myqcloud.com/images/color1.png)

![效果展示2](https://img-1256814817.cos.ap-beijing.myqcloud.com/images/color2.png)
