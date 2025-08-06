"""Core functionality for Meta Ads API MCP package."""

from .server import mcp_server
from .accounts import get_ad_accounts, get_account_info
from .campaigns import get_campaigns, get_campaign_details, create_campaign
from .adsets import get_adsets, get_adset_details, update_adset
from .ads import get_ads, get_ad_details, get_ad_creatives, get_ad_image, update_ad
from .insights import get_insights, debug_image_download
from .authentication import get_login_link
from .server import login_cli, main
from .auth import login
from .ads_library import search_ads_archive
from .budget_schedules import create_budget_schedule

__all__ = [
    'mcp_server',
    'get_ad_accounts',
    'get_account_info',
    'get_campaigns',
    'get_campaign_details',
    'create_campaign',
    'get_adsets',
    'get_adset_details',
    'update_adset',
    'get_ads',
    'get_ad_details',
    'get_ad_creatives',
    'get_ad_image',
    'update_ad',
    'get_insights',
    'debug_image_download',
    'get_login_link',
    'login_cli',
    'login',
    'main',
    'search_ads_archive',
    'create_budget_schedule',
] 