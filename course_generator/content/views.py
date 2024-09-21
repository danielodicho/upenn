# content/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CodingLesson, CodingExercise
from .serializers import CodingLessonSerializer, CodingExerciseSerializer
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import requests
from django.conf import settings
import asyncio
import openai
import aiohttp
import os
from dotenv import load_dotenv
# content/views.py

from .utils import db

load_dotenv()


CHROMA_PATH = "chroma"
openai.api_key="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"
# Initialize Chroma DB once
embedding_function = OpenAIEmbeddings(openai_api_key="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")
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

class CodingLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing coding lessons.
    """
    queryset = CodingLesson.objects.all().order_by('-created_at')
    serializer_class = CodingLessonSerializer

    @action(detail=True, methods=['get'])
    def exercises(self, request, pk=None):
        lesson = self.get_object()
        exercises = lesson.exercises.all()
        serializer = CodingExerciseSerializer(exercises, many=True)
        return Response(serializer.data)

class CodingExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing coding exercises.
    """
    queryset = CodingExercise.objects.all().order_by('-created_at')
    serializer_class = CodingExerciseSerializer

class ExerciseResponseViewSet(viewsets.ViewSet):
    """
    A ViewSet for generating responses to coding exercises.
    """

    async def generate_response_async(self, prompt, headers):
        url = "https://proxy.tune.app/chat/completions"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a coding tutor."},
                {"role": "user", "content": prompt}
            ],
            "model": "openai/gpt-4o-mini",
            "max_tokens": 300,
            "temperature": 0.7,
            "top_p": 1,
            "n": 1,
            "presence_penalty": 0.5,
            "frequency_penalty": 0.5,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"API Error: {resp.status} - {text}")
                data = await resp.json()
                return data['choices'][0]['message']['content']

    @action(detail=False, methods=['post'], url_path='generate-response')
    async def generate_response(self, request):
        """
        Generate a response for a given exercise based on user input.
        """
        data = request.data
        lesson_id = data.get('lesson_id')
        exercise_id = data.get('exercise_id')
        user_input = data.get('user_input')

        if not all([lesson_id, exercise_id, user_input]):
            return Response({'error': 'lesson_id, exercise_id, and user_input are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = CodingLesson.objects.get(id=lesson_id)
            exercise = CodingExercise.objects.get(id=exercise_id)
        except CodingLesson.DoesNotExist:
            return Response({'error': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CodingExercise.DoesNotExist:
            return Response({'error': 'Exercise not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve context from Chroma
        try:
            results = db.similarity_search_with_relevance_scores(exercise.prompt, k=3)
            if not results:
                context_text = "No relevant context found."
            else:
                context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        except Exception as e:
            return Response({'error': f"Chroma search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Formulate the prompt
        prompt = f"{exercise.prompt}\n\n{user_input}\n\n{context_text}"

        # Prepare headers for Tune Studio API
        headers = {
            "X-Org-Id": "0266c7a8-a772-47c1-a450-b02275131dc7",
            "Authorization": f"Bearer {os.environ.get('TUNE_STUDIO_API_KEY')}",
            "Content-Type": "application/json"
        }

        try:
            response_text = await self.generate_response_async(prompt, headers)
        except Exception as e:
            return Response({'error': f"Failed to generate response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Optionally, log the response or save it to a model
        return Response({'response': response_text}, status=status.HTTP_200_OK)
