from django.db import models

class Expense(models.Model):
    school = models.ForeignKey('school.School', on_delete=models.CASCADE)
    manager = models.ForeignKey('manager.Manager', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.BigIntegerField()
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"
