from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import field_validator
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitree_sdk2py.go2.sport.sport_client import (
    SportClient,
    PathPoint,
    SPORT_PATH_POINT_SIZE,
)

from ....utils.logger import logging
from ....utils.registry import registry
from ...base import ArgSchema, BaseTool

CURRENT_PATH = Path(__file__).parents[0]

ARGSCHEMA = {
    "vx": {
        "type": "float",
        "description": "The distance moved in the x-axis direction per call, measured in meters (m). A positive value indicates movement forward, while a negative value indicates movement backward.",
        "required": False,
    },
    "vy": {
        "type": "float",
        "description": "The distance moved in the y-axis direction per call, measured in meters (m). A positive value indicates movement to the left, while a negative value indicates movement to the right.",
        "required": False,
    },
    "vyaw": {
        "type": "float",
        "description": "The angle rotated around the z-axis per call, measured in radians (rad). A positive value indicates clockwise rotation, while a negative value indicates counterclockwise rotation.",
        "required": False,
    },
}


@registry.register_tool()
class Move(BaseTool):
    """Tool for making Unitree Go2 robot move."""

    class Config:
        """Configuration for this pydantic object."""

        extra = "allow"
        arbitrary_types_allowed = True

    args_schema: ArgSchema = ArgSchema(**ARGSCHEMA)
    description: str = "Control the Go2 to move."
    network_interface_name: Optional[str]

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        ChannelFactoryInitialize(0, self.network_interface_name)
        self.sport_client = SportClient()  
        self.sport_client.SetTimeout(10.0)
        self.sport_client.Init()

    @field_validator("network_interface_name")
    @classmethod
    def network_interface_name_validator(cls, network_interface_name: Union[str, None]) -> Union[str, None]:
        if network_interface_name == None:
            raise ValueError("network interface name is not provided.")
        return network_interface_name

    def _run(
        self,
        vx: float = 0,
        vy: float = 0,
        vyaw: float = 0
    ) -> Dict[str, Any]:
        """
        Control the Go2 to move.
        """

        try:
            # self.sport_client.BalanceStand()
            self.sport_client.Move(vx, vy, vyaw)
            return {
                "code": 0,
                "msg": "success",
            }
        except Exception as e:
            logging.error(f"Move failed: {e}")
            return {
                "code": 500,
                "msg": "failed",
            }
