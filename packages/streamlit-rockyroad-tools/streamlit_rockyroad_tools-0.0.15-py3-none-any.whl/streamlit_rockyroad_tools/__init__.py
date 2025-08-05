"""
Streamlit RockyRoad Tools - A collection of Streamlit components

This package provides various custom Streamlit components that can be easily
imported and used in your Streamlit applications.

Available components:
- st_notification_banner: A notification banner component with message and learn more link
- st_folder_navigator: A folder navigation component with breadcrumb-style layout
"""

# Import all components to make them available at package level
from .st_notification_banner import st_notification_banner
from .st_folder_navigator import st_folder_navigator
from .st_notifications import st_info, st_success, st_warning, st_error

# Define what gets imported with "from streamlit_rockyroad_tools import *"
__all__ = [
    "st_notification_banner", 
    "st_folder_navigator",
    "st_info",
    "st_success",
    "st_warning",
    "st_error",
]

# Package metadata
__version__ = '0.0.2'
__author__ = 'Your Name'
__description__ = 'A collection of Streamlit components'
