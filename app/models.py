
from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):

    STATUS = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    start_date = models.DateField()
    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Not Started'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Email reminder tracking
    reminder_sent_for_due_date = models.DateField(
        null=True,
        blank=True
    )

    def progress(self):

        tasks = Task.objects.filter(
            milestone__project=self
        )

        total_tasks = tasks.count()

        if total_tasks == 0:
            return 0

        completed_tasks = tasks.filter(
            completed=True
        ).count()

        return round(
            (completed_tasks / total_tasks) * 100
        )

    def __str__(self):
        return self.title


class Milestone(models.Model):

    STATUS = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones'
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Pending'
    )

    # Email reminder tracking
    reminder_sent_for_due_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class Task(models.Model):

    milestone = models.ForeignKey(
        Milestone,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
