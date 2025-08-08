# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .provisioning_status import ProvisioningStatus
from .load_balancer_operating_status import LoadBalancerOperatingStatus

__all__ = ["Member"]


class Member(BaseModel):
    id: str
    """Member ID must be provided if an existing member is being updated"""

    address: str
    """Member IP address"""

    admin_state_up: bool
    """Administrative state of the resource.

    When set to true, the resource is enabled and operational. When set to false,
    the resource is disabled and will not process traffic. When null is passed, the
    value is skipped and defaults to true.
    """

    backup: bool
    """
    Set to true if the member is a backup member, to which traffic will be sent
    exclusively when all non-backup members will be unreachable. It allows to
    realize ACTIVE-BACKUP load balancing without thinking about VRRP and VIP
    configuration. Default is false
    """

    operating_status: LoadBalancerOperatingStatus
    """Member operating status of the entity"""

    protocol_port: int
    """Member IP port"""

    provisioning_status: ProvisioningStatus
    """Pool member lifecycle status"""

    subnet_id: Optional[str] = None
    """`subnet_id` in which `address` is present."""

    weight: int
    """Member weight. Valid values are 0 < `weight` <= 256."""

    monitor_address: Optional[str] = None
    """An alternate IP address used for health monitoring of a backend member.

    Default is null which monitors the member address.
    """

    monitor_port: Optional[int] = None
    """An alternate protocol port used for health monitoring of a backend member.

    Default is null which monitors the member `protocol_port`.
    """
