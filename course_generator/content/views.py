from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_view(request):
    # This view simply returns a JSON response for testing purposes
    if request.method == 'GET':
        return JsonResponse({'message': 'Django is working!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
