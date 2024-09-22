# content/serializers.py

from rest_framework import serializers
from .models import CodingLesson, CodingExercise

class CodingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingExercise
        fields = ['id', 'prompt', 'starter_code', 'solution_code', 'hints', 'created_at']
# content/serializers.py

from rest_framework import serializers
from .models import CodingLesson, CodingExercise

class CodingExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingExercise
        fields = ['id', 'prompt', 'starter_code', 'solution_code', 'hints', 'created_at']

    def validate_prompt(self, value):
        if not value:
            raise serializers.ValidationError("Prompt cannot be empty.")
        return value

class CodingLessonSerializer(serializers.ModelSerializer):
    exercises = CodingExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = CodingLesson
        fields = ['id', 'title', 'description', 'chroma_document_id', 'difficulty', 'created_at', 'exercises']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

class CodingLessonSerializer(serializers.ModelSerializer):
    exercises = CodingExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = CodingLesson
        fields = ['id', 'title', 'description', 'chroma_document_id', 'difficulty', 'created_at', 'exercises']
