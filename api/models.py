from django.db import models
from django.utils import timezone

from users.models import CustomUser

class Questionnaire(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    content = models.TextField()

    def __str__(self):
        return str(self.pk) + ' @ ' + str(self.date_created)


class Submission(models.Model):
    submission_time = models.DateTimeField(default=timezone.now)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return str(self.user) + ' -> ' + str(self.questionnaire)
