"""
OpenAI协议实现
"""

import os
import hashlib
from typing import Optional
import openai
from .base import Protocol, ProviderConfig
from ..models import SogaResult
from ..decorators import register_protocol


@register_protocol("openai")
class OpenAIProtocol(Protocol):
    """OpenAI协议实现"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        使用OpenAI进行文本到文本转换
        
        Args:
            prompt: 输入文本
            model: 模型名称，默认使用配置中的默认模型
            temperature: 温度参数，默认0.7
            max_tokens: 最大token数，默认1000
            
        Returns:
            生成的文本
        """
        if model is None:
            model = self.config.default_models.get("text_to_text", "gpt-4o")
            
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> SogaResult:
        """
        使用OpenAI进行文本到图像转换，并保存到文件
        
        Args:
            prompt: 输入文本
            model: 模型名称，默认使用配置中的默认模型
            size: 图像尺寸，默认1024x1024
            quality: 图像质量，默认standard
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的图像文件路径
        """
        if model is None:
            model = self.config.default_models.get("text_to_image", "dall-e-3")
            
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )

        image_url = response.data[0].url
        save_path = self.download(image_url, save_path)
        return SogaResult(save_path=save_path, download_url=response.url)