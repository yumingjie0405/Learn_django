from django.db import models

# Create your models here.
class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_name = models.CharField(max_length=100)
    price = models.FloatField()
    publish_date = models.DateField()
    category = models.CharField(max_length=50)
    editor = models.CharField(max_length=50)

    def __str__(self):
        return self.book_name

