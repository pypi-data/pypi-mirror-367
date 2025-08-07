# SOGA TTS - 固定时长语音合成

生成指定时长的语音文件，支持智能文本优化和精确时长控制。

## 安装

```bash
# 从PyPI安装（推荐）
pip install soga-tts

# 或开发模式安装
pip install -e .
```

## 基本使用

### 命令行（最简单）

```bash
# 基本用法 - 生成5秒语音
soga_tts "Hello world" --duration 5.0

# 不使用LLM（更快）
soga_tts "Hello world" --duration 5.0 --no-llm
```

### Python API

```python
from soga_tts import soga_tts

# 最简单的用法
text, audio_path, duration = soga_tts("Hello world", 5.0)
print(f"音频文件: {audio_path}")
```

## 高级用法

### 异常处理

```python
from soga_tts import soga_tts
from soga_tts.fixed_duration_tts import TTSPrecisionError

try:
    text, audio_path, duration = soga_tts("Hello", 10.0, tolerance_pct=5.0)
except TTSPrecisionError as e:
    print(f"精度不够: {e.error_pct:.1f}% (要求: 5.0%)")
```

### 自定义LLM服务

```bash
# 使用OpenAI
soga_tts "Hello" --duration 5.0 \
  --llm-url "https://api.openai.com/v1" \
  --llm-key "your-key" \
  --llm-model "gpt-3.5-turbo"

# 使用Ollama（默认）
soga_tts "Hello" --duration 5.0
```

### 参数调整

```python
soga_tts(
    text="Hello world",
    target_duration=10.0,
    tolerance_pct=3.0,      # 误差容忍度
    max_rounds=5,           # 最大优化回合
    force_exact_duration=True  # 音频缩放
)
```

## 常见问题

### 1. Ollama连接失败
```bash
# 启动Ollama服务
ollama serve

# 检查服务状态
curl http://localhost:11434/api/tags
```

### 2. 精度不够怎么办？
- 使用更宽松的容差：`--tolerance 10.0`
- 增加优化回合数：`--max-rounds 20`
- 启用音频缩放（默认开启）

### 3. 速度太慢？
- 使用 `--no-llm` 跳过文本优化
- 减少回合数：`--max-rounds 3`
- 使用本地Ollama而不是远程API

## 发布到PyPI

### 超简单发布（3步走）

```bash
# 1. 构建包
uv build

# 2. 发布到PyPI  
uv publish

# 3. 完成！
```

### 首次发布
1. 注册PyPI账号：https://pypi.org/account/register/
2. 运行上面3个命令
3. 输入PyPI用户名和密码

发布后全世界用户都可以：`pip install soga-tts` 🚀
