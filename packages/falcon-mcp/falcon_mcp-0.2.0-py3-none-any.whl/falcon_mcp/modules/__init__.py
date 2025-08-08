# ruff: noqa: F401
"""
Modules package for Falcon MCP Server
"""

# Import all module classes so they're available for auto-discovery
from .detections import DetectionsModule
from .hosts import HostsModule
from .incidents import IncidentsModule
from .intel import IntelModule
from .sensor_usage import SensorUsageModule
from .spotlight import SpotlightModule
