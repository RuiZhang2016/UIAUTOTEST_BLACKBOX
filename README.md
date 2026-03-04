# UI Auto Test

基于 **Playwright + pytest-bdd** 的 Web UI 自动化测试框架。采用 BDD 行为驱动开发模式，通过 Gherkin 语法编写测试场景，结合像素级截图对比进行视觉回归检测，并自动生成 Allure 测试报告。

## 技术栈

| 类别 | 工具 |
|------|------|
| 浏览器自动化 | [Playwright](https://playwright.dev/python/) |
| 测试框架 | [pytest](https://docs.pytest.org/) + [pytest-bdd](https://pytest-bdd.readthedocs.io/) |
| 测试报告 | [Allure Report](https://allurereport.org/) |
| 视觉对比 | [Pillow](https://pillow.readthedocs.io/) |
| 日志 | [colorlog](https://github.com/borntyping/python-colorlog) + 并发安全文件轮转 |

## 项目结构

```
uiautotest/
├── conftest.py               # 全局 fixtures & hooks（页面管理、失败截图、Allure 环境）
├── pytest.ini                # pytest 配置（markers、addopts、feature 路径）
├── requirements.txt          # Python 依赖
├── .env.pre.toml.example     # 环境变量模板
│
├── key/                      # 测试模块
│   ├── features/             #   Gherkin feature 文件
│   │   └── key_pc_main_page.feature
│   └── steps/                #   步骤实现
│       └── test_key_pc_main_page.py
│
├── steps/                    # 公共步骤 & 工具
│   └── common.py             #   截图对比（compare_screenshot）、pytest-bdd 符号导出
│
├── utils/                    # 基础工具
│   ├── bdd_decorator.py      #   @bdd_case 装饰器（Feature 解析 → Allure suite/title）
│   ├── common.py             #   @step_recorder 装饰器 & StepTracker
│   ├── log_utils.py          #   彩色控制台 + 并发安全文件日志
│   └── settings.py           #   项目路径配置
│
└── image/
    └── baseline/             # 截图对比基线图（首次运行自动生成）
```

## 核心功能

### BDD 测试流程

```
Feature 文件（Gherkin）  →  @bdd_case 装饰器  →  Step 函数  →  Allure 报告
```

1. 在 `key/features/` 中用 Gherkin 语法定义测试场景
2. 在 `key/steps/` 中实现对应的 `@when` / `@then` 步骤函数
3. `@bdd_case` 装饰器自动绑定 Feature ↔ Scenario，并注入 Allure 元信息

### 视觉回归检测

- 首次运行时自动保存截图为基线（`image/baseline/`）
- 后续运行将当前截图与基线做像素级对比，超过阈值（默认 5%）则判定失败
- 差异图、基线图、当前截图均自动附加到 Allure 报告

### 失败自动截图

测试失败时自动截取全页截图并附加到 Allure 报告，无需手动配置。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 配置环境变量

```bash
cp .env.pre.toml.example .env.pre.toml
```

编辑 `.env.pre.toml`，填入实际值：

```toml
device=Desktop Chrome
main_url=https://your-app-url.com
account=your_account
password=your_password
```

### 3. 运行测试

```bash
# 运行所有 key_pc 标记的用例
pytest -m key_pc

# 仅运行 P0 优先级用例
pytest -m P0

# 无头模式运行（CI 环境）
pytest -m key_pc --headless
```

### 4. 查看 Allure 报告

```bash
allure serve allure_results
```

## 环境变量

通过 `.env.{ENV}.toml` 文件管理，`ENV` 默认为 `pre`。

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ENV` | 运行环境 | `pre` / `prod` / `test` |
| `device` | 浏览器设备配置 | `Desktop Chrome` |
| `main_url` | 被测系统 URL | `https://example.com` |
| `account` | 登录账号 | — |
| `password` | 登录密码 | — |

> `.env.*.toml` 已加入 `.gitignore`，不会提交到仓库。

## 如何新增测试用例

1. **创建 Feature 文件** — `key/features/your_test.feature`

```gherkin
Feature: your_test

  @P0
  Scenario: your_test
    When open the target page
    Then verify page content
```

2. **实现步骤函数** — `key/steps/test_your_test.py`

```python
from steps.common import *
from utils.bdd_decorator import bdd_case

@pytest.mark.key_pc
@bdd_case("key", "your_test.feature", "your_test")
def test_your_case():
    pass

@when("open the target page")
def open_page(page):
    page.goto(os.getenv("main_url"))

@then("verify page content")
def verify(page):
    screenshot = page.screenshot(type="png", full_page=True)
    diff = compare_screenshot("your_baseline.png", screenshot)
    assert diff <= 0.05
```

3. **运行** — `pytest -m key_pc`，首次运行自动生成基线截图。

## License

MIT
