# ppt_layout_generator.py
import asyncio
import json
import os
import time

import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def load_prompt(file_path="prompt.yaml"):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class DirectJSONGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )

    async def generate_layout_json(self, content: str) -> str:
        """直接生成PPT布局JSON，不调用工具"""

        system_prompt = load_prompt()["system prompt"]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下内容生成PPT布局JSON：\n\n{content}"}
        ]

        print("🔄 正在调用API生成JSON...")
        start_time = time.time()

        response = self.client.chat.completions.create(
            model="deepseek-reasoner",
            # model="qwen-vl-max",
            messages=messages,
            temperature=0.1
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"✅ API调用完成，耗时: {elapsed_time:.2f}秒")

        return response.choices[0].message.content


async def main():
    generator = DirectJSONGenerator()

    # 记录总开始时间
    total_start_time = time.time()

    # 创建输出文件夹
    import os
    from datetime import datetime

    # 生成带时间戳的文件夹名
    timestamp = datetime.now().strftime("%m%d%H")
    output_folder = f"{timestamp}_output"

    # 如果文件夹不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 创建输出文件夹: {output_folder}")

    # 加载所有prompt
    prompts = load_prompt()

    # 遍历所有user prompt
    for i in range(1, 9):  # 从user prompt1到user prompt8
        prompt_key = f"user prompt{i}"

        if prompt_key in prompts:
            content = prompts[prompt_key]
            print(f"\n🔄 正在处理 {prompt_key}...")

            # 记录开始时间
            start_time = time.time()

            try:
                # 生成JSON
                json_result = await generator.generate_layout_json(content)

                # 尝试解析JSON以确保格式正确
                parsed_json = json.loads(json_result)

                # 计算耗时
                end_time = time.time()
                elapsed_time = end_time - start_time

                # 生成文件名（包含耗时）
                filename = f"ppt_layout_{i}_{elapsed_time:.1f}s.json"
                filepath = os.path.join(output_folder, filename)

                # 保存到文件，格式化输出
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, ensure_ascii=False, indent=2)

                print(
                    f"✅ {prompt_key} 已保存到: {filepath} (耗时: {elapsed_time:.2f}秒)")

            except json.JSONDecodeError as e:
                # 计算耗时
                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"❌ {prompt_key} JSON格式错误: {e} (耗时: {elapsed_time:.2f}秒)")
                # 保存原始文本作为备用
                filename = f"ppt_layout_{i}_{elapsed_time:.1f}s_raw.txt"
                filepath = os.path.join(output_folder, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(json_result)
                print(f"原始内容已保存到: {filepath}")

            except Exception as e:
                # 计算耗时
                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"❌ {prompt_key} 处理失败: {e} (耗时: {elapsed_time:.2f}秒)")

        else:
            print(f"⚠️ 未找到 {prompt_key}")

    # 计算总耗时
    total_end_time = time.time()
    total_elapsed_time = total_end_time - total_start_time

    print(f"\n🎉 所有处理完成！文件保存在: {output_folder}/")
    print(f"⏱️ 总耗时: {total_elapsed_time:.2f}秒")

if __name__ == "__main__":
    asyncio.run(main())
