# content/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodingLessonViewSet, CodingExerciseViewSet, ExerciseResponseViewSet

router = DefaultRouter()
router.register(r'lessons', CodingLessonViewSet, basename='lesson')
router.register(r'exercises', CodingExerciseViewSet, basename='exercise')
router.register(r'exercise-responses', ExerciseResponseViewSet, basename='exercise-response')

urlpatterns = [
    path('', include(router.urls)),
]
