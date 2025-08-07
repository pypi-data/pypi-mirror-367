#!/usr/bin/env python3
"""
SOGA TTS 命令行工具

使用示例:
    # 使用本地Ollama (默认)
    python -m soga_tts.cli "Hello world" --duration 5.0
    
    # 使用自定义LLM服务
    python -m soga_tts.cli "Hello world" --duration 5.0 --llm-url "http://localhost:8080/v1" --llm-key "your-key"
    
    # 不使用LLM (仅直接TTS)
    python -m soga_tts.cli "Hello world" --duration 5.0 --no-llm
"""

import argparse
import shutil
import openai
from soga_tts.fixed_duration_tts import soga_tts
from soga_tts.my_tts import raw_text_to_speech_tool


def create_llm_function(base_url: str, api_key: str, model: str = "gemma3:4b"):
    """创建LLM调用函数"""
    try:
        client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        def llm_call(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        return llm_call
    except Exception as e:
        print(f"❌ LLM初始化失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="SOGA TTS - 智能固定时长语音合成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # 必需参数
    parser.add_argument(
        "text",
        help="要转换为语音的文本"
    )
    
    parser.add_argument(
        "--duration",
        type=float,
        required=True,
        help="目标音频时长（秒）"
    )
    
    # LLM配置
    parser.add_argument(
        "--llm-url",
        default="http://localhost:11434/v1",
        help="LLM服务URL (默认: http://localhost:11434/v1)"
    )
    
    parser.add_argument(
        "--llm-key",
        default="ollama",
        help="LLM API密钥 (默认: ollama)"
    )
    
    parser.add_argument(
        "--llm-model",
        default="gemma3:4b",
        help="LLM模型名称 (默认: gemma3:4b)"
    )
    
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="不使用LLM，仅进行直接TTS转换"
    )
    
    # TTS配置
    parser.add_argument(
        "--tolerance",
        type=float,
        default=3.0,
        help="时长误差容忍度百分比 (默认: 3.0)"
    )
    
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=10,
        help="最大优化回合数 (默认: 10)"
    )
    
    parser.add_argument(
        "--no-scaling",
        action="store_true",
        help="禁用最终音频缩放"
    )
    
    # 输出配置
    parser.add_argument(
        "--output",
        help="输出音频文件路径 (可选)"
    )

    args = parser.parse_args()
    
    # 设置LLM函数
    llm_function = None
    if not args.no_llm:
        print(f"🔗 连接LLM服务: {args.llm_url}")
        print(f"📦 使用模型: {args.llm_model}")
        
        llm_function = create_llm_function(
            base_url=args.llm_url,
            api_key=args.llm_key,
            model=args.llm_model
        )
        
        if llm_function is None:
            print("❌ LLM连接失败，将使用直接TTS模式")
    
    # 执行TTS转换
    print(f"\n🎬 开始TTS转换")
    print(f"📝 文本: {args.text}")
    print(f"⏱️ 目标时长: {args.duration}秒")
    print(f"🎯 容差: ±{args.tolerance}%")

    result = soga_tts(
        text=args.text,
        target_duration=args.duration,
        tts_function=raw_text_to_speech_tool,
        llm_function=llm_function,
        tolerance_pct=args.tolerance,
        max_rounds=args.max_rounds,
        force_exact_duration=not args.no_scaling
    )

    # 输出结果
    print(f"\n📋 转换完成")
    print(f"原始文本: {args.text}")
    print(f"最终文本: {result.text}")
    print(result.duration)
    print(f"音频时长: {result.duration:.2f}s" if result.duration else "转换失败")

    if result.success:
        error_pct = abs(result.duration - args.duration) / args.duration * 100
        print(f"时长误差: {error_pct:.2f}%")
        print(f"音频文件: {result.path}")

    # 复制到指定输出路径
    if args.output and result.path:
        shutil.copy2(result.path, args.output)
        print(f"✅ 音频已保存到: {args.output}")



if __name__ == "__main__":
    main()
