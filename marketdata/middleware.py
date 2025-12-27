from django.utils import timezone
from datetime import timedelta


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                try:
                    from datetime import datetime
                    last_activity_time = datetime.fromisoformat(last_activity)
                    if timezone.is_naive(last_activity_time):
                        last_activity_time = timezone.make_aware(last_activity_time)
                    
                    current_time = timezone.now()
                    timeout_duration = timedelta(seconds=request.session.get_expiry_age())
                    
                    if current_time - last_activity_time > timeout_duration:
                        request.session.flush()
                    else:
                        request.session['last_activity'] = current_time.isoformat()
                except (ValueError, TypeError):
                    request.session['last_activity'] = timezone.now().isoformat()
            else:
                request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response
