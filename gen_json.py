# direct_json_generator.py
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
            messages=messages,
            temperature=0.1
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"✅ API调用完成，耗时: {elapsed_time:.2f}秒")

        return response.choices[0].message.content


async def main():
    generator = DirectJSONGenerator()

    content = """我们的项目目标是开发一套面向中小企业的智能库存管理系统，帮助客户实现库存可视化、自动补货与预测分析。项目分为四个阶段：需求调研、系统开发、试点测试、正式上线。当前已完成前两个阶段，系统功能包括实时库存监控、预警机制、自动生成采购单等。下一步将进入试点阶段，选择3家客户进行测试并收集反馈。"""

    json_result = await generator.generate_layout_json(content)
    print("\n📄 生成的JSON内容:")
    print(json_result)

    # 保存JSON到文件
    try:
        # 尝试解析JSON以确保格式正确
        parsed_json = json.loads(json_result)

        # 保存到文件，格式化输出
        with open("ppt_layout.json", "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=2)

        print(f"\n✅ JSON已保存到: ppt_layout.json")
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON格式错误，无法保存: {e}")
        # 保存原始文本作为备用
        with open("ppt_layout_raw.txt", "w", encoding="utf-8") as f:
            f.write(json_result)
        print(f"原始内容已保存到: ppt_layout_raw.txt")

if __name__ == "__main__":
    asyncio.run(main())
