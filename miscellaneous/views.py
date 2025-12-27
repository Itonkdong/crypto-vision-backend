import os
from pathlib import Path

from django.conf import settings
from django.db import connection
from django.db.models import Count, Max
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from miscellaneous.models import ErrorLog
from miscellaneous.seriazliers import ErrorLogSerializer


class ApiIndexView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        base = request.build_absolute_uri(request.path.rstrip("/") + "/")
        return Response(
            {
                "status": "ok",
                "endpoints": {
                    "health": f"{base}health/",
                    "exchanges": f"{base}exchanges/",
                    "tickers": f"{base}tickers/",
                    "candles": f"{base}candles/<symbol>/",
                    "summary": f"{base}summary/",
                    "alerts": f"{base}alerts/",
                },
            }
        )


class HealthView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):

        db_path = settings.CRYPTO_DB_PATH
        db_exists = os.path.exists(db_path) if db_path else False

        tables = []
        table_exists = False
        db_error = None

        if db_exists:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    table_exists = 'prices' in tables
            except Exception as e:
                db_error = str(e)
                tables = [f"Error: {str(e)}"]
        else:
            db_error = f"Database file not found at: {db_path}"

        payload = {
            "status": "ok" if (db_exists and table_exists) else "error",
            "database": str(db_path),
            "database_exists": db_exists,
            "table_exists": table_exists,
            "tables": tables,
            "error": db_error,
            "database_absolute_path": str(Path(db_path).resolve()) if db_path else None,
        }
        return Response(payload)


class ErrorLogView(APIView):

    def post(self, request):
        print(f"DEBUG: ErrorLogView POST received. User: {request.user}, Auth: {request.auth}")
        print(f"DEBUG: Request data: {request.data}")
        data = request.data.copy()
        if request.user.is_authenticated:
            data['user'] = request.user.id

        serializer = ErrorLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print("DEBUG: Error saved successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(f"DEBUG: Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        error_type = request.query_params.get('type')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = ErrorLog.objects.all()

        if error_type and error_type != 'all':
            queryset = queryset.filter(type=error_type)

        if start_date:
            try:
                from django.utils.dateparse import parse_datetime
                start_dt = parse_datetime(start_date)
                if start_dt:
                    queryset = queryset.filter(timestamp__gte=start_dt)
            except:
                pass

        if end_date:
            try:
                from django.utils.dateparse import parse_datetime
                end_dt = parse_datetime(end_date)
                if end_dt:
                    queryset = queryset.filter(timestamp__lte=end_dt)
            except:
                pass

        aggregated = queryset.values(
            'type', 'endpoint', 'status', 'message'
        ).annotate(
            count=Count('id'),
            last_occurrence=Max('timestamp'),
            error_id=Max('id')
        ).order_by('-last_occurrence')

        results = []
        for item in aggregated:
            error = ErrorLog.objects.filter(
                type=item['type'],
                endpoint=item['endpoint'],
                status=item['status'],
                message=item['message']
            ).order_by('-timestamp').first()

            results.append({
                'id': item['error_id'],
                'type': item['type'],
                'endpoint': item['endpoint'] or '',
                'status': item['status'] or '',
                'message': item['message'],
                'stack_trace': error.stack_trace if error else '',
                'username': error.user.username if error and error.user else None,
                'timestamp': item['last_occurrence'],
                'count': item['count']
            })

        return Response(results)
