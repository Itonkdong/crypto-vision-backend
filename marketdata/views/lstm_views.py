from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from helpers.env_variables import LSTM_SERVICE_URL

class LSTMPredictionView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, symbol):
        """Handle GET requests from the frontend template"""
        service_url = f"{LSTM_SERVICE_URL}/predict"

        # Extract parameters from query string
        lookback = request.query_params.get('lookback', 30)
        epochs = request.query_params.get('epochs', 5)
        
        payload = {
            "crypto": symbol,
            "lookback": int(lookback),
            "epochs": int(epochs)
        }
        
        try:
            # Proxy to microservice
            response = requests.post(service_url, json=payload, timeout=120)
            
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": f"Microservice error: {response.text}"}, 
                    status=response.status_code
                )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "LSTM Service is unavailable"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, symbol=None):
        service_url = f"{LSTM_SERVICE_URL}/predict"

        data = request.data.copy()
        if symbol and "crypto" not in data:
            data["crypto"] = symbol
            
        try:
            response = requests.post(service_url, json=data)
            
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                 return Response(
                    {"error": f"Microservice error: {response.text}"}, 
                    status=response.status_code
                )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "LSTM Service is unavailable"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
