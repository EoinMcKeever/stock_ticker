import yfinance as yf
from fastapi import HTTPException, status, Depends


# Helper function to validate ticker
async def validate_ticker(symbol: str) -> dict:
    """
    Validate ticker exists and get its information.
    Returns dict with: name, type, exchange, currency
    Raises HTTPException if ticker is invalid.
    """
    symbol = symbol.upper()

    try:
        # Try to fetch ticker data from yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Check if we got valid data
        if not info or 'symbol' not in info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker {symbol} not found or is invalid"
            )

        # Determine if it's stock or crypto
        quote_type = info.get('quoteType', '').lower()

        if quote_type == 'cryptocurrency':
            ticker_type = 'crypto'
        elif quote_type in ['equity', 'etf']:
            ticker_type = 'stock'
        else:
            # Fallback: check if symbol ends with common crypto suffixes
            if symbol.endswith('-USD') or symbol.endswith('USD'):
                ticker_type = 'crypto'
            else:
                ticker_type = 'stock'

        # Get the long name or short name
        name = info.get('longName') or info.get('shortName') or symbol

        return {
            'name': name,
            'type': ticker_type,
            'exchange': info.get('exchange', 'Unknown'),
            'currency': info.get('currency', 'USD')
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unable to validate ticker {symbol}: {str(e)}"
        )
