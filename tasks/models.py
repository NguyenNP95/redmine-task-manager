from django.db import models


class RedmineConfiguration(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "Redmine Configuration"
        verbose_name_plural = "Redmine Configurations"
