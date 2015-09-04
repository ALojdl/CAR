from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField


class Ignore(models.Model):
    uuid = models.CharField(max_length=30)
    ignored = models.CharField(max_length=30)


class Keys(models.Model):
    temp = models.CharField(max_length=60)
    real = models.CharField(max_length=40)
    time = models.DateTimeField(auto_now=True, auto_now_add=False)


class RecommendationMatrix(models.Model):
    name = models.CharField(max_length=60)
    data = models.CharField(max_length=8192)


class Area(models.Model):
    name = models.CharField(max_length=60)
    lat_id = models.IntegerField()
    lng_id = models.IntegerField()
    data = ListField(EmbeddedModelField('MetaDataFormat'))


class MetaDataFormat(models.Model):
    content_id = models.CharField(max_length=60)
    type = models.CharField(max_length=60)
    description = models.CharField(max_length=60)
    project = models.CharField(max_length=60)
    attributes = EmbeddedModelField()


class PoiAttributes(models.Model):
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=60)
    url = models.CharField(max_length=60)

    openHours = ListField(EmbeddedModelField('PoiOpenHour'))
    fee = ListField(EmbeddedModelField('PoiFee'))
    tags = ListField(models.CharField(max_length=60))
    coords = ListField(models.DecimalField())
    city = EmbeddedModelField('PoiCity')


class PoiOpenHour(models.Model):
    frondow = models.IntegerField()
    fromtime = models.IntegerField()
    todow = models.IntegerField()
    totime = models.IntegerField()
    startdate = models.IntegerField()
    occurence = models.IntegerField()
    every = models.IntegerField()


class PoiFee(models.Model):
    currency = models.CharField(max_length=60)
    value = models.IntegerField()
    hint = models.CharField(max_length=60)


class PoiCity(models.Model):
    locode = models.CharField(max_length=60)
    displayName = models.CharField(max_length=60)
    description = models.CharField(max_length=60)
    locale = models.CharField(max_length=60)
    coords = ListField(models.DecimalField())


class PoiSocialAttribute(models.Model):
    likes = models.IntegerField()
    checkins = models.IntegerField()
    ratings = EmbeddedModelField('PoiSocialAttributeRating')


class PoiSocialAttributeRating(models.Model):
    count = models.IntegerField()
    average = models.FloatField()