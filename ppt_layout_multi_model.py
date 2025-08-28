# ppt_layout_multi_model.py
import argparse
import asyncio
import json
import os
import time
from datetime import datetime

import yaml
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def load_prompt(file_path="prompt.yaml"):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ModelConfigManager:
    """模型配置管理器 - 借鉴Paper2Poster的设计思路"""

    def __init__(self):
        self.model_configs = {
            # OpenAI 系列
            'gpt-4o': {
                'provider': 'openai',
                'model_name': 'gpt-4o',
                'api_key_env': 'OPENAI_API_KEY',
                'base_url_env': 'OPENAI_BASE_URL',
                'base_url_default': 'https://api.openai.com/v1'
            },
            'gpt-4o-mini': {
                'provider': 'openai',
                'model_name': 'gpt-4o-mini',
                'api_key_env': 'OPENAI_API_KEY',
                'base_url_env': 'OPENAI_BASE_URL',
                'base_url_default': 'https://api.openai.com/v1'
            },
            'gpt-4': {
                'provider': 'openai',
                'model_name': 'gpt-4',
                'api_key_env': 'OPENAI_API_KEY',
                'base_url_env': 'OPENAI_BASE_URL',
                'base_url_default': 'https://api.openai.com/v1'
            },

            # 通义千问系列
            'qwen-plus': {
                'provider': 'qwen',
                'model_name': 'qwen-plus',
                'api_key_env': 'QWEN_API_KEY',
                'base_url_env': 'QWEN_BASE_URL',
                'base_url_default': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },
            'qwen-max': {
                'provider': 'qwen',
                'model_name': 'qwen-max',
                'api_key_env': 'QWEN_API_KEY',
                'base_url_env': 'QWEN_BASE_URL',
                'base_url_default': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },
            'qwen-turbo': {
                'provider': 'qwen',
                'model_name': 'qwen-turbo',
                'api_key_env': 'QWEN_API_KEY',
                'base_url_env': 'QWEN_BASE_URL',
                'base_url_default': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            },

            # DeepSeek 系列
            'deepseek-reasoner': {
                'provider': 'deepseek',
                'model_name': 'deepseek-reasoner',
                'api_key_env': 'DEEPSEEK_API_KEY',
                'base_url_env': 'DEEPSEEK_BASE_URL',
                'base_url_default': 'https://api.deepseek.com/v1'
            },
            'deepseek-chat': {
                'provider': 'deepseek',
                'model_name': 'deepseek-chat',
                'api_key_env': 'DEEPSEEK_API_KEY',
                'base_url_env': 'DEEPSEEK_BASE_URL',
                'base_url_default': 'https://api.deepseek.com/v1'
            },

            # 本地模型
            'llama-3.1-8b': {
                'provider': 'local',
                'model_name': 'llama-3.1-8b',
                'api_key_env': 'LOCAL_API_KEY',
                'base_url_env': 'LOCAL_BASE_URL',
                'base_url_default': 'http://localhost:8000/v1'
            }
        }

    def get_config(self, model_name):
        """获取模型配置"""
        if model_name not in self.model_configs:
            raise ValueError(f"不支持的模型: {model_name}")
        return self.model_configs[model_name]

    def get_available_models(self):
        """获取所有可用模型"""
        return list(self.model_configs.keys())

    def create_client(self, model_name):
        """根据模型配置创建客户端"""
        config = self.get_config(model_name)

        api_key = os.getenv(config['api_key_env'])
        base_url = os.getenv(config['base_url_env'],
                             config['base_url_default'])

        if not api_key:
            raise ValueError(f"未设置环境变量: {config['api_key_env']}")

        return OpenAI(
            api_key=api_key,
            base_url=base_url
        )


class MultiModelGenerator:
    """多模型PPT布局生成器"""

    def __init__(self):
        self.config_manager = ModelConfigManager()

    async def generate_layout_json(self, content: str, model_name: str) -> str:
        """使用指定模型生成PPT布局JSON"""

        # 获取模型配置并创建客户端
        client = self.config_manager.create_client(model_name)
        config = self.config_manager.get_config(model_name)

        system_prompt = load_prompt()["system prompt"]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请为以下内容生成PPT布局JSON：\n\n{content}"}
        ]

        print(f"�� 正在使用 {model_name} 生成JSON...")
        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model=config['model_name'],
                messages=messages,
                temperature=0.1
            )

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"✅ {model_name} API调用完成，耗时: {elapsed_time:.2f}秒")

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ {model_name} API调用失败: {e}")
            raise


async def main():
    parser = argparse.ArgumentParser(description='多模型PPT布局生成器')
    parser.add_argument('--model', type=str, default='qwen-max',
                        help='要使用的模型名称')
    parser.add_argument('--list-models', action='store_true',
                        help='列出所有可用模型')
    parser.add_argument('--prompt-file', type=str, default='prompt.yaml',
                        help='prompt配置文件路径')

    args = parser.parse_args()

    generator = MultiModelGenerator()

    # 如果用户要求列出模型
    if args.list_models:
        models = generator.config_manager.get_available_models()
        print("📋 可用模型列表:")
        for i, model in enumerate(models, 1):
            config = generator.config_manager.get_config(model)
            print(f"  {i}. {model} ({config['provider']})")
        return

    model_name = args.model

    # 验证模型是否支持
    try:
        generator.config_manager.get_config(model_name)
    except ValueError as e:
        print(f"❌ {e}")
        print("使用 --list-models 查看所有可用模型")
        return

    # 验证prompt文件
    if not os.path.exists(args.prompt_file):
        print(f"❌ 找不到prompt文件: {args.prompt_file}")
        return

    # 记录总开始时间
    total_start_time = time.time()

    # 创建输出文件夹
    timestamp = datetime.now().strftime("%m%d%H")
    output_folder = f"{timestamp}_{model_name}_output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 创建输出文件夹: {output_folder}")

    # 加载所有prompt
    try:
        prompts = load_prompt(args.prompt_file)
    except Exception as e:
        print(f"❌ 加载prompt文件失败: {e}")
        return

    # 遍历所有user prompt
    for i in range(1, 9):
        prompt_key = f"user prompt{i}"

        if prompt_key in prompts:
            content = prompts[prompt_key]
            print(f"\n🔄 正在处理 {prompt_key}...")

            start_time = time.time()
            try:
                json_result = await generator.generate_layout_json(content, model_name)

                # 去除 markdown 代码块包裹
                if json_result.strip().startswith("```"):
                    json_result = json_result.strip()
                    if json_result.startswith("```json"):
                        json_result = json_result[len("```json"):].strip()
                    elif json_result.startswith("```"):
                        json_result = json_result[len("```"):].strip()
                    if json_result.endswith("```"):
                        json_result = json_result[:-3].strip()

                # 尝试解析JSON以确保格式正确
                parsed_json = json.loads(json_result)

                # 计算耗时
                end_time = time.time()
                elapsed_time = end_time - start_time

                # 生成文件名
                filename = f"ppt_layout_{i}_{elapsed_time:.1f}s.json"
                filepath = os.path.join(output_folder, filename)

                # 保存到文件
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(parsed_json, f, ensure_ascii=False, indent=2)

                print(
                    f"✅ {prompt_key} 已保存到: {filepath} (耗时: {elapsed_time:.2f}秒)")

            except json.JSONDecodeError as e:
                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"❌ {prompt_key} JSON格式错误: {e} (耗时: {elapsed_time:.2f}秒)")
                filename = f"ppt_layout_{i}_{elapsed_time:.1f}s_raw.txt"
                filepath = os.path.join(output_folder, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(json_result)
                print(f"原始内容已保存到: {filepath}")

            except Exception as e:
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
