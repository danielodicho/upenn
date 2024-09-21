from django.db import models

# Create your models here.
# In content/models.py
from django.db import models

class CodingLesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    chroma_document_id = models.CharField(max_length=255)  # Link to Chroma document
    difficulty = models.CharField(max_length=5) # choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')]
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
