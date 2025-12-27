from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from helpers.env_variables import SENTIMENT_ANALYSIS_SERVICE_URL


class SentimentOnChainAnalysisView(APIView):
    """
    Proxy to Sentiment Microservice
    """

    def post(self, request, symbol):
        symbol = symbol.upper()
        SERVICE_URL = f"{SENTIMENT_ANALYSIS_SERVICE_URL}/analyze"

        try:
            response = requests.post(SERVICE_URL, json={"symbol": symbol}, timeout=60)

            if response.status_code == 200:
                return Response(response.json())
            else:
                return Response(
                    {"error": f"Sentiment service error: {response.text}"},
                    status=response.status_code
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
