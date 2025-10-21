from django.db import models

# Create your models here.

class Subscribe(models.Model):
    title = models.CharField(max_length=200)
    nums_of_exams = models.IntegerField()
    nums_of_students = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title