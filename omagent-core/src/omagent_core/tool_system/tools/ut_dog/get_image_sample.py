from pathlib import Path
import time
from typing import Any, Dict, Optional, Union

import cv2
import numpy as np
from pydantic import field_validator
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

from ....utils.logger import logging
from ....utils.registry import registry
from ...base import ArgSchema, BaseTool

CURRENT_PATH = Path(__file__).parents[0]

ARGSCHEMA = {
}


@registry.register_tool()
class GetImageSample(BaseTool):
    """Tool for making Unitree Go2 robot to get image sample."""

    class Config:
        """Configuration for this pydantic object."""

        extra = "allow"
        arbitrary_types_allowed = True

    args_schema: ArgSchema = ArgSchema(**ARGSCHEMA)
    description: str = "Control the Unitree Go2 robot to get image sample."
    network_interface_name: Optional[str]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        ChannelFactoryInitialize(0, self.network_interface_name)
        self.video_client = VideoClient()  
        self.video_client.SetTimeout(3.0)
        self.video_client.Init()

    @field_validator("network_interface_name")
    @classmethod
    def network_interface_name_validator(cls, network_interface_name: Union[str, None]) -> Union[str, None]:
        if network_interface_name == None:
            raise ValueError("network interface name is not provided.")
        return network_interface_name

    def _run(
        self,
    ) -> Dict[str, Any]:
        """
        Control the Unitree Go2 robot to get image sample.
        """

        try:
            code, data = self.video_client.GetImageSample()
            if code != 0:
                raise Exception(f"Get image sample failed: {data}")

            image_array = np.frombuffer(bytes(data), np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            cache_data = self.stm(self.workflow_instance_id)["image_cache"]
            if cache_data is None:
                cache_data = {}
            cache_data.update({f"<image_{int(time.time())}>": image})
            self.stm(self.workflow_instance_id)["image_cache"] = cache_data
            return {
                "code": 0,
                "msg": "success"
            }
        except Exception as e:
            logging.error(f"Get image sample failed: {e}")
            return {
                "code": 500,
                "msg": "failed",
            }
