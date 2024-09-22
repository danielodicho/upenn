# content/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CodingLesson, CodingExercise
from .serializers import CodingLessonSerializer, CodingExerciseSerializer
# from .utils import db  # Use the Chroma DB from utils.py
import aiohttp
import os
from django.core.cache import cache  # For caching
import logging

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "C:/Users/danie/upenn/chroma"

# Initialize Chroma DB with API key from environment variables
embedding_function = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
# Initialize logger
logger = logging.getLogger('content')

class CodingLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing coding lessons.
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
    A ViewSet for viewing coding exercises.
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
                    logger.error(f"API Error: {resp.status} - {text}")
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
            logger.warning("Missing required fields in generate_response request.")
            return Response({'error': 'lesson_id, exercise_id, and user_input are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            lesson = CodingLesson.objects.get(id=lesson_id)
            exercise = CodingExercise.objects.get(id=exercise_id)
        except CodingLesson.DoesNotExist:
            logger.error(f"Lesson with id {lesson_id} not found.")
            return Response({'error': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)
        except CodingExercise.DoesNotExist:
            logger.error(f"Exercise with id {exercise_id} not found.")
            return Response({'error': 'Exercise not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve context from Chroma with caching
        cache_key = f"lesson_{lesson_id}_exercise_{exercise_id}_input_{user_input}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for key: {cache_key}")
            return Response({'response': cached_response, 'cached': True}, status=status.HTTP_200_OK)

        try:
            results = db.similarity_search_with_relevance_scores(exercise.prompt, k=3)
            if not results:
                context_text = "No relevant context found."
                logger.warning(f"No Chroma results for exercise prompt: {exercise.prompt}")
            else:
                context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
                logger.debug(f"Chroma results found: {len(results)} documents.")
        except Exception as e:
            logger.exception("Chroma search failed.")
            return Response({'error': f"Chroma search failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Formulate the prompt
        prompt = f"{exercise.prompt}\n\n{user_input}\n\n{context_text}"
        logger.debug(f"Formulated prompt: {prompt}")

        # Prepare headers for Tune Studio API
        headers = {
            "X-Org-Id": "0266c7a8-a772-47c1-a450-b02275131dc7",
            "Authorization": f"Bearer {os.environ.get('TUNE_STUDIO_API_KEY')}",
            "Content-Type": "application/json"
        }

        try:
            response_text = await self.generate_response_async(prompt, headers)
            logger.info(f"Generated response for exercise_id={exercise_id}: {response_text[:50]}...")
            cache.set(cache_key, response_text, timeout=60*60)  # Cache for 1 hour
        except Exception as e:
            logger.exception("Failed to generate response.")
            return Response({'error': f"Failed to generate response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'response': response_text, 'cached': False}, status=status.HTTP_200_OK)

from django.views import View
from django.http import JsonResponse

class ListChromaDocuments(View):
    def get(self, request):
        documents = db.get()
        docs = []
        print(documents, "hello")
        for doc, meta in zip(documents['documents'], documents['metadatas']):
            docs.append({
                'content': doc[:100],  # First 100 chars
                'source': meta.get('source', 'unknown_source'),
                'page': meta.get('page', 'N/A'),
                'start_index': meta.get('start_index', 'N/A')
            })
        return JsonResponse({'documents': docs})
    
# make an endpoint that receives two strings: input and context, calls the query_data.py file, and returns the response
from rest_framework.decorators import api_view
from query_data import main

@action(detail=False, methods=['post'], url_path='generate-response')
def generate_response(request):

    data = request.data
    input = data.get('input')
    context = data.get('context')
    response = main(input, context)
    return Response({'response': response})