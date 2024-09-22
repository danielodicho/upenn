# content/models.py

from django.db import models

class CodingLesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    chroma_document_id = models.CharField(max_length=255)  # Link to Chroma document
    difficulty = models.CharField(max_length=30)  # e.g., Beginner, Intermediate, Advanced
    created_at = models.DateTimeField(auto_now_add=True)

    total_interactions = models.PositiveIntegerField(default=0)
    common_questions = models.JSONField(default=dict, blank=True, null=True)
    struggle_topics = models.JSONField(default=dict, blank=True, null=True)
    feedback_summary = models.TextField(blank=True, null=True)

    def update_analysis(self):
        self.total_interactions = self.total_interactions.count()

        common_qs = CommonQuestion.objects.filter(lesson=self).order_by('-frequency')[:5]
        self.common_questions = {q.question: q.frequency for q in common_qs}

        struggles = StruggleAnalysis.objects.filter(lesson=self).order_by('-frequency')[:5]
        self.struggle_topics = {s.topic: s.frequency for s in struggles}

        self.feedback_summary = "summary goes here"

        self.save()

    def __str__(self):
        return self.title

class StudentInteraction(models.Model):
    lesson = models.ForeignKey(CodingLesson, related_name='interactions', on_delete=models.CASCADE)
    exercise = models.ForeignKey('CodingExercise', related_name='interactions', on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # add this later, track if the student found the response helpful
    # helpful = models.BooleanField(default=True)

class StruggleAnalysis(models.Model):
    lesson = models.ForeignKey(CodingLesson, related_name='struggles', on_delete=models.CASCADE)
    topic = models.CharField(max_length=255)
    frequency = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.topic} ({self.frequency})"
    

class CommonQuestion(models.Model):
    lesson = models.ForeignKey(CodingLesson, related_name='common_questions', on_delete=models.CASCADE)
    question = models.TextField()
    frequency = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Q: {self.question[:50]}... ({self.frequency})"

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
