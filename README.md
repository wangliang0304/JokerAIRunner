### 人生苦短，我用python。
分享开源这个工具的初衷（详见下面文章链接）：

https://mp.weixin.qq.com/s/tdZ5_VcKjCItgTgD7lfUPA

- AI驱动的自动化。
- 配置即编程，配置即自动化。
- 简便，却不简单。
- 开源不易，纯粹！送给毕业季的朋友。

如果你在一个规模不大的公司，如果你认为python是最高效的语言，如果同时你还在积极探索AI在测试自动化的应用，
那么恭喜，你找到了一个适合你的自动化测试框架。

⭐ 每一个Star都是对创作者的鼓励，也是让更多人发现并受益于[JokerAIRunner]的机会 
⭐ 今天你的支持，就是我们明天前进的动力

- api用例demo
```python
class TestAgentStatusTest(HttpRunner):
    config = Config("step name").base_url("${ENV(base_url_C)}")

    teststeps = [
        Step(
            RunRequest("代理状态").setup_hook('${setup_hooks_request($request)}')
            .get(
                "/api/online-agent-product/agent/status"
            )
            .with_params(**{"categoryId": "10"})
            .with_headers(
                **{
                    "content-type": "application/json",
                    "user-agent": "PalmPay/5.7.0&604181603 (Android 13)",
                }
            )
            .validate()
            .assert_equal("status_code", 200, "assert response status code")
            .assert_equal("body.respCode", "00000000", "assert response body respCode")
            .assert_equal("body.respMsg", "success", "assert response body respMsg")
            .assert_equal("body.status", True, "assert response body status")
        )
    ]

if __name__ == "__main__":
    TestAgentStatusTest().test_start()
```

- UI用例demo
```yaml
web:
  url: https://www.joker.pw

tasks:
  - name: 点击第一个卡片
    flow:
      - ai: 点击第一个卡片的按钮："立即使用"
      - sleep: 3000
      - aiAssert: 第一个的卡片页面正常打开
```

### 兼容接口和AI驱动UI自动化的allure统一报告预览

- 成功的UI用例
![img_2.png](img/img_2.png)
- 失败的UI用例
![img_1.png](img/img_1.png)

### 核心理念

- 简便易用；
- 约定大于配置，配置大于编程；
- 不重复造轮子，复用兼容优秀项目。（兼容httprunner和midscene）

### 项目结构

```
autopalmpay/
├── .env                    # 环境变量配置文件
├── .debugtalk_gen.py       # HttpRunner生成的函数注册文件
├── debugtalk.py            # 自定义函数和钩子函数
├── pytest.ini              # Pytest配置文件
├── run_pytest.py           # 主运行脚本，生成Allure报告
├── common/                 # 公共功能模块
├── config/                 # 配置文件目录
├── testcases/              # 测试用例目录
│   ├── conftest.py         # Pytest配置和钩子函数
│   ├── api/                # API测试用例
│   └── UI/                 # UI测试用例
├── util/                   # 工具类
├── allure_result/          # Allure测试结果目录
├── allure_report/          # Allure报告目录
└── midscene_run/           # MidScene运行目录
    └── report/             # MidScene报告目录
```

### 执行命令

进入项目根目录下执行命令，完全兼容pytest的语法：

- 运行所有用例：

```python
python - m pytest .\testcases
```

- 运行接口用例

```python
python - m pytest .\testcases\api
```

- 运行UI用例

```python
python - m pytest .\testcases\UI
```

兼容UI自动化的展示界面运行：
```python
# Run in headed mode
pytest testcases/UI --midscene-headed

# Keep window open after test
pytest testcases/UI --midscene-keep-window

# Both options together
pytest testcases/UI --midscene-headed --midscene-keep-window
```


### 感谢项目
- [HttpRunner](https://github.com/httprunner/httprunner)
- [MidScene](https://github.com/web-infra-dev/midscene)

### 联系作者
- 微信公众号：jokerceshi666
<div style="width: 150px">

![微信二维码](img/joker_wx.PNG)
</div>
