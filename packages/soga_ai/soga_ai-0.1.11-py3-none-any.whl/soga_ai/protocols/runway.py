"""
Runway协议实现
"""

import os
import hashlib
from typing import Optional
from runwayapi import (
    login,
    get_user_team_id,
    get_min_session_id,
    get_sessions,
    create_session,
    get_asset_group_id,
    generate_image,
    generate_video_for_gen3a,
    generate_video_for_gen4,
    get_video_task_detail,
    get_image_task_detail,
    upload_image,
    is_can_generate_image,
    is_can_generate_video,
    delete_other_task
)

from .base import Protocol, ProviderConfig
from ..decorators import register_protocol
from ..models import SogaResult


@register_protocol("runway")
class RunwayProtocol(Protocol):
    """Runway协议实现"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._team_id = None
        self._session_id = None

    def _get_team_id_and_session_id(self) -> tuple :
        token = self.config.api_key
        if not token:
            raise ValueError("RUNWAY_TOKEN not found in environment variables.")

        if self._team_id is None or self._session_id is None:
            self._team_id = get_user_team_id(token)
            self._session_id = create_session(token, self._team_id)

        return self._team_id, self._session_id

    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> SogaResult:
        """
        使用Runway进行文本到图像转换，并保存到文件

        Args:
            prompt: 输入文本
            model: 模型名称，默认使用配置中的默认模型
            size: 图像尺寸，默认1024x1024
            quality: 图像质量，默认standard
            save_path: 保存路径，如果不指定则使用默认路径

        Returns:
            保存的图像文件路径
        """

        token = self.config.api_key
        if not token:
            raise ValueError("RUNWAY_TOKEN not found in environment variables.")

        team_id, session_id = self._get_team_id_and_session_id()

        task_id = generate_image(
            token=self.config.api_key,
            team_id=team_id,
            session_id=session_id,
            prompt=prompt,
            num_images=1
        )

        images = get_image_task_detail(token, team_id, task_id)

        image_url = images[0]

        self.download(image_url, save_path)

        return SogaResult(save_path=save_path, download_url=image_url)

    def image_to_video(self,  prompt: str, image_path:str, second:int = 5, model: Optional[str] = None,
                      save_path: Optional[str] = None) -> SogaResult:

        token = self.config.api_key
        if not token:
            raise ValueError("RUNWAY_TOKEN not found in environment variables.")

        team_id, session_id = self._get_team_id_and_session_id()

        task_id:str = ""

        if image_path.startswith("http"):
            image_url = image_path
        else:
            image_url = upload_image(self.config.api_key, image_path)

        if "gen3a_turbo" == model:
            task_id = generate_video_for_gen3a(
                token=self.config.api_key,
                team_id=team_id,
                session_id=session_id,
                image_url=image_url,
                prompt=prompt,
                second=second
            )
        elif "gen4_turbo" == model:
            task_id = generate_video_for_gen4(
                token=self.config.api_key,
                team_id=team_id,
                session_id=session_id,
                image_url=image_url,
                prompt=prompt,
                second=second
            )

        if task_id == "":
            raise ValueError("task_id not found.")

        video_url = get_video_task_detail(token, team_id, task_id)

        self.download(video_url, save_path)
        return SogaResult(save_path=save_path, image_url=video_url)
