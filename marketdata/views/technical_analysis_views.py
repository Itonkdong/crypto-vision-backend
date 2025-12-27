from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests
from helpers.env_variables import TECHNICAL_ANALYSIS_SERVICE_URL

class TechnicalAnalysisView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, symbol):
        timeframe = request.GET.get('timeframe', '1d')
        all_timeframes = request.GET.get('all', 'false').lower() == 'true'
        
        # Microservice URL
        SERVICE_URL = f"{TECHNICAL_ANALYSIS_SERVICE_URL}/analyze"

        try:
            if all_timeframes:
                # Need to implement multiple timeframes logic in microservice or client
                # For now, let's keep it simple or expand microservice. 
                # Implementing simple loop here for MVP
                timeframes = ['1d', '1w', '1m']
                results = {}
                for tf in timeframes:
                     try:
                        resp = requests.post(SERVICE_URL, json={"symbol": symbol.upper(), "timeframe": tf})
                        if resp.status_code == 200:
                            results[tf] = resp.json()
                        else:
                             results[tf] = {'error': f'Microservice error: {resp.text}'}
                     except:
                         results[tf] = {'error': 'Service unavailable'}
                return Response(results, status=status.HTTP_200_OK)

            else:
                if timeframe not in ['1d', '1w', '1m']:
                    return Response(
                        {'error': 'Invalid timeframe. Must be 1d, 1w, or 1m'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Call Microservice
                payload = {
                    "symbol": symbol.upper(),
                    "timeframe": timeframe
                }
                response = requests.post(SERVICE_URL, json=payload)
                
                if response.status_code == 200:
                    return Response(response.json(), status=status.HTTP_200_OK)
                elif response.status_code == 404:
                     return Response(
                        {'error': f'Insufficient data for symbol {symbol} with timeframe {timeframe}'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                else:
                    return Response(
                        {"error": f"Microservice error: {response.text}"}, 
                        status=response.status_code
                    )

        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "Technical Analysis Service is unavailable"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
