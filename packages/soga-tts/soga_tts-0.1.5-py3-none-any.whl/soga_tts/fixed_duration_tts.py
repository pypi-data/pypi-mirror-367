import asyncio
import os
import re
import json
import concurrent.futures
from typing import Optional, Tuple, List

import edge_tts
from moviepy import AudioFileClip
from pydantic import BaseModel

# 提示词模板
VARIANTS_PROMPT_TEMPLATE = """TTS合成任务：基于原始文案生成10个不同长度的版本

原始文案：{original_text} 
(当前{original_length}字符，实际TTS时长{current_actual_duration:.1f}s，目标时长{target_duration:.1f}s)

要求：
1. 必须与原始文案保持相同语种
2. 保持原始文案的核心意思和语调
3. 生成10个版本，字符长度分别为：
   版本1: {target_length_1}字符左右
   版本2: {target_length_2}字符左右  
   版本3: {target_length_3}字符左右
   版本4: {target_length_4}字符左右
   版本5: {target_length_5}字符左右
   版本6: {target_length_6}字符左右
   版本7: {target_length_7}字符左右
   版本8: {target_length_8}字符左右
   版本9: {target_length_9}字符左右
   版本10: {target_length_10}字符左右

通过增减词汇、描述、解释等调整长度，但始终基于原始文案改写。

以json格式输出，录入
```json
[
    {{
        "version": 1,
        "text": "这是第一个个版本",
        "length": 100
    }},
    ...
]
```"""

class SogaTTSResult(BaseModel):
    duration: float = 0
    text: str = ""
    success: bool = True
    path: str = ""

class SogaTTS:
    """智能TTS生成器，能够生成指定时长的语音"""

    def __init__(self, tts_function, llm_function):
        self.tts_function = tts_function if tts_function is not None else self.default_tts_by_edge_tts
        self.llm_function = llm_function
        print("✅ SogaTTS 初始化完成")

    def default_tts_by_edge_tts(self, text: str) -> str:
        """Generates speech from text using the edge-tts library and saves it to a file.

        Args:
            text: The text to generate speech from.

        Returns:
            A string representing the path to the generated audio file.
        """
        # Create a placeholder file name
        safe_text = "".join(c for c in text if c.isalnum() or c in " _-").rstrip()
        file_name = f"audio_for_{safe_text[:50]}.mp3"
        file_path = os.path.join("/tmp", file_name)

        async def _generate():
            communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
            await communicate.save(file_path)

        # Run the async function
        # A new event loop is created for each call to avoid issues with running asyncio in a sync context.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(_generate())

        return file_path

    def get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        with AudioFileClip(audio_path) as clip:
            return clip.duration

    def generate_text_variants(self, original_text: str, target_duration: float,
                               current_actual_duration: float, round_num: int) -> List[str]:
        """使用LLM生成不同长度的文本变体"""
        original_length = len(original_text)
        ratio_needed = target_duration / current_actual_duration
        max_multiplier = ratio_needed * 2  # 快速收敛，乘以2

        print(f"🔧 第{round_num}回合：基于原文生成线性变体 (1x到{max_multiplier:.1f}x)")

        # 计算10个线性分布的长度倍数
        multipliers = [1.0 + i * (max_multiplier - 1.0) / 9 for i in range(10)]
        target_lengths = [int(original_length * m) for m in multipliers]

        # 使用您的提示词模板
        prompt = VARIANTS_PROMPT_TEMPLATE.format(
            original_text=original_text,
            original_length=original_length,
            current_actual_duration=current_actual_duration,
            target_duration=target_duration,
            **{f'target_length_{i + 1}': length for i, length in enumerate(target_lengths)}
        )

        response = self.llm_function(prompt)
        print(f"   📝 LLM响应: {response[:100]}...")  # 打印前100个字符

        return self._extract_texts_from_response(response)

    def _extract_texts_from_response(self, response: str) -> List[str]:
        """从LLM响应中提取文本列表"""
        json_content = re.search(r'```json(.*?)```', response, re.DOTALL)
        if not json_content:
            print("   ❌ 未找到JSON内容")
            return []

        json_string = json_content.group(1).strip()
        try:
            variants = json.loads(json_string)
            if isinstance(variants, list):
                texts = [v['text'] for v in variants if 'text' in v]
                print(f"   ✅ 成功提取{len(texts)}个文本变体")
                return texts
        except json.JSONDecodeError:
            print("   ❌ JSON解析失败")
            return []

    def find_best_variant(self, texts: List[str], target_duration: float) -> SogaTTSResult:
        """并行生成音频并找到最接近目标时长的版本"""
        print(f"   🎵 并行生成{len(texts)}个音频变体...")

        def process_variant(variant):
            try:
                audio_path = self.tts_function(variant)
                audio_duration = self.get_audio_duration(audio_path)
                print(f"      📊 变体时长: {audio_duration:.2f}s (目标: {target_duration:.2f}s)")
                return SogaTTSResult(
                    text=variant,
                    path=audio_path,
                    duration=audio_duration,
                    success=True
                )
            except Exception as e:
                print(f"      ❌ 变体生成失败: {e}")
                return SogaTTSResult(
                    text=variant,
                    success=False
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(process_variant, texts))

        # 过滤失败的结果
        successful_results = [r for r in results if r.success]
        if not successful_results:
            print("   ❌ 所有变体生成失败")
            return SogaTTSResult(success=False)

        # 选择最接近目标时长的版本
        best = min(successful_results, key=lambda x: abs(x.duration - target_duration))
        error = abs(best.duration - target_duration)
        print(f"   🎯 选择最佳变体: {best.duration:.2f}s (误差: {error:.2f}s)")

        return best

    def adjust_audio_speed(self, audio_path: str, target_duration: float) -> SogaTTSResult:
        """调整音频速度以匹配目标时长"""
        print(f"   ⚡ 调整音频速度至精确时长: {target_duration:.2f}s")
        try:
            with AudioFileClip(audio_path) as clip:
                adjusted_clip = clip.with_speed_scaled(final_duration=target_duration)
                adjusted_clip.write_audiofile(audio_path)
            return SogaTTSResult(
                path=audio_path,
                duration=target_duration,
                success=True
            )
        except Exception as e:
            print(f"   ❌ 音频速度调整失败: {e}")
            return SogaTTSResult(success=False)

    def generate(self, text: str, target_duration: float, tolerance_pct: float = 3.0,
                 max_rounds: int = 10, force_exact_duration: bool = True) -> SogaTTSResult:
        """
        生成指定时长的TTS音频

        Returns:
            SogaTTSResult: 包含生成结果的所有信息
        """
        print(f"🚀 开始TTS生成: 目标时长{target_duration:.1f}s, 容错{tolerance_pct}%")

        current_text = text
        all_results = []

        # 首次生成获取基线
        print("📍 生成初始基线...")
        try:
            audio_path = self.tts_function(current_text)
            current_duration = self.get_audio_duration(audio_path)
            baseline_result = SogaTTSResult(
                text=current_text,
                path=audio_path,
                duration=current_duration,
                success=True
            )
            all_results.append(baseline_result)
            print(f"   基线时长: {current_duration:.2f}s")

            # 检查基线是否已经满足精度要求
            baseline_error_pct = abs(current_duration - target_duration) / target_duration * 100
            print(f"📊 基线误差: {baseline_error_pct:.1f}% (容错线: {tolerance_pct}%)")

            if baseline_error_pct <= tolerance_pct:
                print(f"✅ 基线已满足精度要求，无需优化")
                # 如果需要精确时长，仍然调整音频速度
                if force_exact_duration:
                    adjusted_result = self.adjust_audio_speed(baseline_result.path, target_duration)
                    if adjusted_result.success:
                        baseline_result.duration = target_duration
                        print(f"🎯 最终时长: {target_duration:.2f}s (精确匹配)")
                    else:
                        print("⚠️ 音频速度调整失败，返回未调整版本")
                return baseline_result

        except Exception as e:
            print(f"❌ 基线生成失败: {e}")
            return SogaTTSResult(text=text, success=False)

        # 迭代优化
        for round_num in range(1, max_rounds + 1):
            # 生成变体并选择最佳
            variants = self.generate_text_variants(current_text, target_duration, current_duration, round_num)
            if not variants:
                print("❌ 未能生成文本变体，停止优化")
                break

            best_variant = self.find_best_variant(variants, target_duration)
            if not best_variant.success:
                print("❌ 未能生成有效的音频变体，停止优化")
                break

            current_text = best_variant.text
            current_duration = best_variant.duration
            all_results.append(best_variant)

            # 检查是否已满足精度要求
            error_pct = abs(current_duration - target_duration) / target_duration * 100
            print(f"📊 当前误差: {error_pct:.1f}% (容错线: {tolerance_pct}%)")

            if error_pct <= tolerance_pct:
                print(f"✅ 已达到精度要求，停止优化")
                break

        # 选择最佳结果
        best_result = min(all_results, key=lambda x: abs(x.duration - target_duration))
        print(f"🏆 最佳结果: {best_result.duration:.2f}s (误差: {abs(best_result.duration - target_duration):.2f}s)")

        # 如果需要精确时长，调整音频速度
        if force_exact_duration:
            adjusted_result = self.adjust_audio_speed(best_result.path, target_duration)
            if adjusted_result.success:
                # 更新最佳结果的属性
                best_result.duration = target_duration
                print(f"🎯 最终时长: {target_duration:.2f}s (精确匹配)")
            else:
                print("⚠️ 音频速度调整失败，返回未调整版本")

        return best_result

def soga_tts(text: str, target_duration: float=None, tts_function=None, llm_function=None,
             tolerance_pct: float = 3.0, max_rounds: int = 10,
             force_exact_duration: bool = True) -> SogaTTSResult:
    """
    Soga TTS主入口函数

    Args:
        text: 要转换的文本
        target_duration: 目标时长（秒）
        tts_function: TTS函数
        llm_function: LLM函数
        tolerance_pct: 容错百分比（默认3%）
        max_rounds: 最大优化轮数（默认10）
        force_exact_duration: 是否强制精确时长（默认True）

    Returns:
        SogaTTSResult: 包含生成结果的所有信息
    """
    generator = SogaTTS(tts_function, llm_function)
    return generator.generate(text, target_duration, tolerance_pct, max_rounds, force_exact_duration)