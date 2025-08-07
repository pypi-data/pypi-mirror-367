# term-rules

Transparent Easy Rule Model（基于树模型的规则抽取与评估，German Credit 示例）。

> 安装（包名）：`pip install term-rules`  
> 导入（代码包）：`import term`（因为源码目录叫 `term/`）

## 快速开始
```python
from term import Rule
r = Rule("CreditHistory <= 3.5 & Duration > 11.5 & Savings <= 1.5")
mask = r(df)  # True 表示命中该规则
