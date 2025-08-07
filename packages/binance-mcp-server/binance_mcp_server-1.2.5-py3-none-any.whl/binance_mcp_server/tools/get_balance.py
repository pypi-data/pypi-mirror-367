import logging
from typing import Dict, Any
from binance.exceptions import BinanceAPIException, BinanceRequestException
from binance_mcp_server.utils import (
    get_binance_client, 
    create_error_response, 
    create_success_response,
    rate_limited,
    binance_rate_limiter,
)


logger = logging.getLogger(__name__)


@rate_limited(binance_rate_limiter)
def get_balance() -> Dict[str, Any]:
    """
    Get the current account balance for all assets on Binance.
    
    This function retrieves the balances of all assets in the user's Binance account,
    including available and locked amounts.
    
    Returns:
        Dict containing:
        - success (bool): Whether the request was successful
        - data (dict): Response data with asset balances
        - timestamp (int): Unix timestamp of the response
        - error (dict, optional): Error details if request failed
        
    Examples:
        result = get_balance()
        if result["success"]:
            balances = result["data"]
            print(f"Available USDT: {balances['USDT']['free']}")
    """
    logger.info("Fetching account balance")
    
    try:
        client = get_binance_client()
        
        account_info = client.get_account()
        
        balances = {
            asset["asset"]: {
                "free": float(asset["free"]),
                "locked": float(asset["locked"])
            }
            for asset in account_info["balances"]
            if float(asset["free"]) > 0 or float(asset["locked"]) > 0
        }
        
        logger.info("Successfully fetched account balances")
        
        return create_success_response(
            data=balances
        )

    except (BinanceAPIException, BinanceRequestException) as e:
        logger.error(f"Error fetching account assets: {str(e)}")
        return create_error_response("binance_api_error", f"Error fetching account assets: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in get_account_assets tool: {str(e)}")
        return create_error_response("tool_error", f"Tool execution failed: {str(e)}")