from django.contrib.gis.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
from django.contrib.gis.utils import LayerMapping
from datetime import date
from datetime import datetime
import os
from zipfile import ZipFile
from anotador import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cellphone = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    institution = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    municipality = models.CharField(max_length=50)
    speciality = models.CharField(max_length=50)
    is_manager = models.BooleanField(default=False)
    is_annotator = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)
    is_contact = models.BooleanField(default=False)
    active_proj = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Profile"


class Macroproject(models.Model):
    macro_project_name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, default='')
    start_date = models.DateField(default=date.today)
    manager = models.ManyToManyField(User, related_name="works_as_macroproject_manager")

    class Meta:
        verbose_name_plural = "MacroProjects"

    def __str__(self):
        return self.macro_project_name


class Samplesproject(models.Model):
    project_name = models.CharField(max_length=50)
    users = models.ManyToManyField(User)
    place_name = models.CharField(max_length=50, default='Villa Clara')
    local_site = models.CharField(max_length=50, default='')
    Longitud_site = models.CharField(max_length=50, default='-79.49')
    Latitud_site = models.CharField(max_length=50, default='22.07')
    start_date = models.DateField(default=date.today)
    producer = models.CharField(max_length=50, default='Geocuba IC')
    client = models.CharField(max_length=50, default='MINAG')
    macro_project = models.ForeignKey(Macroproject, on_delete=models.CASCADE, related_name="macroproyect")

    class Meta:
        verbose_name_plural = "SamplesProjects"

    def __str__(self):
        return self.project_name


class Image(models.Model):
    PLATFORM_TYPES = (
        ('1', 'Sentinel'),
        ('2', 'Drones'),
        ('3', 'Russia'),
        ('4', 'Landsat'),
        ('5', 'Spot'),
    )
    NAME_TYPES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
        ('I', 'I'),
        ('J', 'J'),
    )
    image_file = models.FileField(upload_to='temporal_files/', default=None, blank=False)
    platform = models.CharField(max_length=200, choices=PLATFORM_TYPES)
    date_captured = models.DateField(default=date.today)
    name = models.CharField(max_length=200, choices=NAME_TYPES, default='A')
    sample_project = models.ForeignKey(Samplesproject, on_delete=models.CASCADE, default=None,
                                       related_name='image_samplesproject')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

        plat = {
            '1': 'sentinel',
            '2': 'drones',
            '3': 'russia',
            '4': 'landsat',
            '5': 'spot',
        }

        if self.image_file is not None:
            imagefile = self.image_file.path

            project = Samplesproject.objects.get(pk=self.sample_project_id)
            project_name = str(self.sample_project_id) + '-' + project.project_name

            ruta_extraccion = settings.MEDIA_ROOT + "images/" + project_name
            p = plat[str(self.platform)]

            if self.date_captured.month < 10:
                m = '0' + str(self.date_captured.month)
            else:
                m = str(self.date_captured.month)

            if self.date_captured.day < 10:
                d = '0' + str(self.date_captured.day)
            else:
                d = str(self.date_captured.day)
            fecha = str(self.date_captured.year) + m + d

            ruta_extraccion = ruta_extraccion + '/' + p + '/' + fecha + '/' + self.name + '/'
            try:
                os.mkdir(ruta_extraccion)
            except:
                pass

            unziped = ZipFile(imagefile, 'r')
            unziped.extractall(path=ruta_extraccion)
            unziped.close()

    class Meta:
        verbose_name_plural = "Images"


class Shape(models.Model):
    shape_file = models.FileField(upload_to='temporal_files/', default=None, blank=False)
    description = models.TextField(max_length=500, default='')
    date_captured = models.DateField(default=date.today)
    sample_project = models.ForeignKey(Samplesproject, on_delete=models.CASCADE, default=None,
                                       related_name='shape_samplesproject')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

        if self.shape_file is not None:
            shapefile = self.shape_file.path

            project = Samplesproject.objects.get(pk=self.sample_project_id)
            project_name = str(self.sample_project_id) + '-' + project.project_name

            ruta_extraccion = settings.MEDIA_ROOT + "shape/" + project_name

            if self.date_captured.month < 10:
                m = '0' + str(self.date_captured.month)
            else:
                m = str(self.date_captured.month)

            if self.date_captured.day < 10:
                d = '0' + str(self.date_captured.day)
            else:
                d = str(self.date_captured.day)

            fecha = str(self.date_captured.year) + m + d

            ruta_extraccion = ruta_extraccion + '/' + fecha + '/'
            try:
                os.mkdir(ruta_extraccion)
            except:
                pass

            unziped = ZipFile(shapefile, 'r')
            unziped.extractall(path=ruta_extraccion)
            unziped.close()

    class Meta:
        verbose_name_plural = "Shapes"


class Label(models.Model):
    macro_project = models.ForeignKey(Macroproject, on_delete=models.CASCADE, related_name="label_macroproject")
    label_name = models.CharField(max_length=255, default='')
    color = ColorField(default='#FF0000')
    description = models.TextField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "Labels"

    def __str__(self):
        return self.label_name


class Site(models.Model):
    sample_project = models.ForeignKey(Samplesproject, on_delete=models.CASCADE, default=None,
                                       related_name='site_samplesproject')
    label = models.ForeignKey(Label, on_delete=models.CASCADE, default=None, blank=True, related_name='site_label')
    point = models.PointField(srid=4326, null=True, blank=True)
    date_satellite = models.DateField(default=date(2020, 7, 16))
    site_name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Sites"
        permissions = (("add_samples", "delete_samples"),)

    def __str__(self):
        return self.site_name



class Corte(models.Model):
    cpa = models.CharField(max_length=255, default='')
    fecha = models.DateField(default=date(2020, 12, 1))
    bloque = models.IntegerField(default=0)
    campo = models.IntegerField(default=0)
    variedad = models.CharField(max_length=255, default='')
    cepa = models.CharField(max_length=255, default='')
    edad = models.FloatField(default=0.0)
    pol_cana = models.FloatField(default=0.0)
    pol_jugo = models.FloatField(default=0.0)
    pureza = models.FloatField(default=0.0)
    index = models.FloatField(default=0.0)
    brix = models.FloatField(default=0.0)
    brix_inf = models.FloatField(default=0.0)
    brix_sup = models.FloatField(default=0.0)
    im = models.FloatField(default=0.0)
    fibra = models.FloatField(default=0.0)
    rendimiento = models.FloatField(default=0.0)
    ha = models.FloatField(default=0.0)
    t_ha = models.FloatField(default=0.0)
    t = models.FloatField(default=0.0)
    sample_project = models.ForeignKey(Samplesproject, on_delete=models.CASCADE, default=None,
                                       related_name='corte_samplesproject')

    def __str__(self):
        return self.campo

