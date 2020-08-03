from django.db import models

class Product(models.Model):
    name            = models.CharField(max_length=20)
    description     = models.CharField(max_length=50)

    class Meta:
        db_table = 'products'

class Size(models.Model):
    name        = models.CharField(max_length=20)
    description = models.CharField(max_length=10,null=True)

    class Meta:
        db_table = 'sizes'

class Color(models.Model):
    name      = models.CharField(max_length=20)
    code      = models.CharField(max_length=20,null=True)
    image_url = models.URLField(max_length=1000,null=True)

    class Meta:
        db_table = 'colors'

class SkinType(models.Model):
    name    = models.CharField(max_length=10)

    class Meta:
        db_table = 'skin_types'

    def __str__(self):
        return self.name

class Option(models.Model):
    size        = models.ForeignKey('Size',on_delete=models.SET_NULL,null=True)
    color       = models.ForeignKey('Color',on_delete=models.SET_NULL,null=True)
    skin_type   = models.ForeignKey('SkinType',on_delete=models.SET_NULL,null=True)

    class Meta:
        db_table = 'options'

class ProductOption(models.Model):
    price     = models.DecimalField(max_digits=10, decimal_places=2)
    option    = models.ForeignKey('Option',on_delete= models.SET_NULL,null=True)
    product   = models.ForeignKey('Product',on_delete= models.SET_NULL,null=True)
    image_url = models.URLField(max_length=1000,null=True)

    class Meta:
        db_table = 'products_options'
