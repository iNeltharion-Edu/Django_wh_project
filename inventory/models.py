from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('supplier', 'Supplier'),
        ('consumer', 'Consumer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="inventory_user_groups",
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="inventory_user_permissions",
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Product(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    warehouse = models.ForeignKey(Warehouse, related_name='products', on_delete=models.CASCADE)
