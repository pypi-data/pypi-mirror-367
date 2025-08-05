"""
Mobiska Client Module
====================

This module provides a simplified client interface for the Mobiska Payment Gateway.
"""

from apps.mobiska.client import MobiskaClient

# Re-export the client class
__all__ = ['MobiskaClient']
