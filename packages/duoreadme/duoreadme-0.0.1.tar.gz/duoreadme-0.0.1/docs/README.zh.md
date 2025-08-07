# DuoReadme - 多语言 README 生成工具

DuoReadme 是一个强大的命令行工具，可以自动将项目代码和 README 翻译成多种语言，并生成标准化的多语言文档。

## 功能

- **多语言支持**：支持包括中文、英文、日文、韩文、法语、德语、西班牙语、意大利语、葡萄牙语、俄语等在内的100多种语言。完整语言列表请参见 [ISO 语言代码](./LANGUAGE.md)。
- **智能解析**：自动解析项目结构和代码内容。
- **批量处理**：一键生成所有语言的 README 文档。
- **腾讯云集成**：与腾讯云智能平台集成。
- **标准配置**：使用通用项目标准，将英文 README.md 放在根目录下，其他语言 README.md 文件放在 docs 目录中。

## 安装

```bash
pip install duoreadme
```

## 使用方法

### 基本用法

```bash
# 查看所有可用命令
duoreadme --help

# 生成多语言 README（自动应用 .gitignore 过滤）
duoreadme gen

# 指定项目路径生成
duoreadme gen --project-path ./myproject

# 指定要翻译的语言
duoreadme gen --languages "zh-Hans,en,ja,ko,fr"

# 纯文本翻译 README 文件
duoreadme trans --languages "zh-Hans,en,ja"
```

### 可用命令

#### gen - 生成多语言 README
```bash
# 使用默认设置生成多语言 README
duoreadme gen

# 指定项目路径
duoreadme gen --project-path ./myproject

# 指定要翻译的语言
duoreadme gen --languages "zh-Hans,en,ja,ko,fr"

# 显示详细输出
duoreadme gen --verbose

# 启用调试模式（显示详细日志）
duoreadme gen --debug
```

#### trans - 纯文本翻译
```bash
# 使用默认设置翻译 README 文件
duoreadme trans

# 指定项目路径
duoreadme trans --project-path ./myproject

# 指定要翻译的语言
duoreadme trans --languages "zh-Hans,en,ja,ko,fr"

# 显示详细输出
duoreadme trans --verbose

# 启用调试模式（显示详细日志）
duoreadme trans --debug
```

**关于 trans 命令**

`trans` 命令是一个纯文本翻译功能，它从项目根目录读取 README 文件并将其翻译成多种语言。与处理整个项目结构的 `gen` 命令不同，`trans` 专注于翻译 README 内容。

- 从项目根目录读取 README.md 文件
- 将内容翻译成指定语言
- 使用与 `gen` 相同的解析和生成逻辑生成多语言 README 文件
- 不在 API 请求中包含 `code_text` 参数（纯文本翻译）
- 支持与 `gen` 命令相同的选项以保持一致性

**关于 .gitignore 支持**

翻译器会自动检测项目根目录下的 `.gitignore` 文件并过滤掉忽略的文件和目录。这样可以确保只翻译项目中真正重要的源代码文件，避免临时文件、构建产物、依赖包等。

- 如果项目有 `.gitignore` 文件，它将自动应用过滤规则。
- 如果没有 `.gitignore` 文件，它将读取所有文本文件。
- 支持标准 `.gitignore` 语法（通配符、目录模式等）。
- 优先读取 `README.md` 文件，然后读取其他源代码文件。

**🔍 整体代码阅读逻辑**

DuoReadme 采用智能项目内容阅读策略，以确保翻译的内容既全面又准确：

#### 1. 文件扫描策略
```
项目根目录
├── README.md （优先读取）
├── .gitignore （用于过滤）
├── src/ （源代码目录）
├── lib/ （库文件目录）
├── docs/ （文档目录）
└── 其他配置文件
```

#### 2. 阅读优先级
1. **README.md** - 主要项目文档，优先读取和压缩处理
2. **源代码文件** - 按重要性读取
3. **配置文件** - 项目配置文件
4. **文档文件** - 其他文档说明

#### 3. 内容处理工作流程

##### 3.1 文件过滤
- 自动应用 `.gitignore` 规则
- 过滤二进制文件、临时文件、构建产物
- 只处理文本文件（.md, .py, .js, .java, .cpp 等）

##### 3.2 内容压缩
- **README.md**：压缩到 3000 字符，保留核心内容
- **源代码文件**：智能选择重要文件，每个文件压缩到 2000 字符
- **总内容限制**：每次翻译不超过 15KB，长内容自动分批处理

##### 3.3 智能选择
- 优先选择包含主要逻辑的文件
- 跳过测试文件、示例文件、临时文件
- 保留关键函数定义、类定义、注释

#### 4. 批量处理机制
当项目内容超过 15KB 时，系统自动分批处理：

```
内容分析 → 文件分组 → 分批翻译 → 结果合并
```

- **文件分组**：按文件类型和重要性分组
- **分批翻译**：每次处理 15KB 的内容
- **结果合并**：智能合并多个批次的结果

#### 5. 支持的文件类型
- **文档文件**：.md, .txt, .rst
- **源代码**：.py, .js, .java, .cpp, .c, .go, .rs
- **配置文件**：.yaml, .yml, .json, .toml
- **其他文本**：.sql, .sh, .bat

#### 6. 内容优化
- 自动去除重复内容
- 保留关键结构信息
- 智能压缩长文本，保持可读性
- 优先保留注释和文档字符串

#### config - 显示配置信息
```bash
# 显示当前内置配置
duoreadme config

# 启用调试模式查看详细配置信息
duoreadme config --debug
```

#### set - 更新内置配置（仅限开发/构建）
```bash
# 应用新的配置到内置配置（仅限开发/构建）
duoreadme set my_config.yaml
```

#### export - 导出内置配置
```bash
# 导出当前内置配置
duoreadme export -o exported_config.yaml
```

#### 全局选项

```bash
# 显示版本信息
duoreadme --version

# 显示帮助信息
duoreadme --help
```

#### 编程接口

```python
from src.core.translator import Translator
from src.core.parser import Parser

# 创建翻译器
translator = Translator()

# 翻译项目内容
result = translator.translate_project("./sample_project")

# 解析多语言内容
parser = Parser()
readme_dict = parser.parse_multilingual_content(result)
```

## 配置

#### 环境变量

```bash
# 腾讯云配置
export TENCENTCLOUD_SECRET_ID="your_secret_id"
export TENCENTCLOUD_SECRET_KEY="your_secret_key"
# 应用程序配置
export DUOREADME_BOT_APP_KEY="your_bot_app_key"
```

#### 配置文件（仅限开发/构建）

您可以检查 [config.yaml.example](./config.yaml.example) 文件以获取配置文件。

## 日志

DuoReadme 提供了一个完整的日志系统，帮助您了解翻译过程的细节：

#### 日志级别

- **DEBUG**：详细的调试信息（仅在调试模式下显示）
- **INFO**：一般信息（默认显示）
- **WARNING**：警告信息
- **ERROR**：错误信息
- **CRITICAL**：严重错误信息

#### 使用方法

##### 调试模式
```bash
# 显示所有级别的日志，包括详细的调试信息
duoreadme gen --debug
```

##### 调试信息包括
- 配置文件加载过程
- 文件扫描和过滤细节
- 翻译请求的详细信息
- 内容压缩和批量处理过程
- 文件生成和保存步骤
- 错误和异常的详细信息

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_translator.py
```

要求：为每种语言生成完整的翻译，保持原始格式和结构。