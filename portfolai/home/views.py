from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import get_stock_quote, get_company_profile, search_stocks, get_market_status, get_stock_candles

# Create your views here (- SK).

def index(request):
    return render(request, 'home/index.html')


def dashboard(request):
    """
    Dashboard page view - serves the admin dashboard
    """
    context = {
        'page_title': 'PortfolAI Dashboard',
        'user': request.user if request.user.is_authenticated else None,
    }
    return render(request, 'home/dashboard.html', context)




@csrf_exempt
@require_http_methods(["GET"])
def api_search_stocks(request):
    """
    API endpoint to search for stocks
    """
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Query parameter is required'}, status=400)
    
    results = search_stocks(query)
    if results is None:
        return JsonResponse({'error': 'Failed to fetch search results'}, status=500)
    
    return JsonResponse(results)


@csrf_exempt
@require_http_methods(["GET"])
def api_stock_quote(request):
    """
    API endpoint to get stock quote
    """
    symbol = request.GET.get('symbol', '')
    if not symbol:
        return JsonResponse({'error': 'Symbol parameter is required'}, status=400)
    
    quote = get_stock_quote(symbol)
    if quote is None:
        return JsonResponse({'error': 'Failed to fetch stock quote'}, status=500)
    
    return JsonResponse(quote)


@csrf_exempt
@require_http_methods(["GET"])
def api_company_profile(request):
    """
    API endpoint to get company profile
    """
    symbol = request.GET.get('symbol', '')
    if not symbol:
        return JsonResponse({'error': 'Symbol parameter is required'}, status=400)
    
    profile = get_company_profile(symbol)
    if profile is None:
        return JsonResponse({'error': 'Failed to fetch company profile'}, status=500)
    
    return JsonResponse(profile)


@csrf_exempt
@require_http_methods(["GET"])
def api_market_status(request):
    """
    API endpoint to get market status
    """
    status = get_market_status()
    if status is None:
        return JsonResponse({'error': 'Failed to fetch market status'}, status=500)
    
    return JsonResponse(status)


@csrf_exempt
@require_http_methods(["GET"])
def api_stock_candles(request):
    """
    API endpoint to get historical stock data (candles)
    """
    symbol = request.GET.get('symbol', '')
    resolution = request.GET.get('resolution', 'D')  # D for daily, 1 for 1 minute, etc.
    count = int(request.GET.get('count', 30))
    
    if not symbol:
        return JsonResponse({'error': 'Symbol parameter is required'}, status=400)
    
    candles = get_stock_candles(symbol, resolution, count)
    if candles is None:
        return JsonResponse({'error': 'Failed to fetch historical data'}, status=500)
    
    return JsonResponse(candles)


