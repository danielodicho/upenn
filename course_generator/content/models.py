# content/models.py

from django.db import models

class CodingLesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    chroma_document_id = models.CharField(max_length=255)  # Link to Chroma document
    difficulty = models.CharField(max_length=5)  # e.g., Beginner, Intermediate, Advanced
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CodingExercise(models.Model):
    lesson = models.ForeignKey(CodingLesson, related_name='exercises', on_delete=models.CASCADE)
    prompt = models.TextField()
    starter_code = models.TextField()
    solution_code = models.TextField()
    hints = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exercise for {self.lesson.title}"

class ExerciseResponse(models.Model):
    exercise = models.ForeignKey(CodingExercise, related_name='responses', on_delete=models.CASCADE)
    user_input = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.exercise.id} at {self.created_at}"
