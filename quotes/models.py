from django.db import models

# Create your models here.

class Announcement(models.Model):
    content = models.TextField(max_length=750)
    creation_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

class Tag(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Quote(models.Model):
    content = models.TextField(max_length=750)
    tags = models.ManyToManyField(Tag, related_name="quotes")
    approved = models.BooleanField(default=False)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.content
