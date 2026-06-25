"""
Generator — LLM 回答生成器

使用 OpenAI 兼容 API 进行生成，支持流式输出。
"""

from openai import OpenAI
from typing import Generator


SYSTEM_PROMPT = """你是一个基于文档的智能问答助手。请根据提供的文档内容回答用户问题。

规则：
1. 如果文档中包含答案，请准确引用并注明来源
2. 如果文档中不包含答案，请明确告知用户"文档中未找到相关信息"
3. 回答要简洁、准确，避免编造
4. 如果涉及多个来源，请综合回答"""


class Generator:
    """LLM 生成器"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-3.5-turbo",
    ):
        self.model = model
        self.client = OpenAI(
            api_key=api_key or "sk-placeholder",
            base_url=base_url,
        )

    def generate(self, query: str, context: str) -> str:
        """同步生成回答"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"【文档内容】\n{context}\n\n【用户问题】\n{query}"},
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""

    def generate_stream(self, query: str, context: str) -> Generator[str, None, None]:
        """流式生成回答"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"【文档内容】\n{context}\n\n【用户问题】\n{query}"},
        ]

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
