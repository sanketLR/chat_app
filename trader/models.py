from django.db import models

# Create your models here.

    
class TradeData(models.Model):
    tradeName = models.CharField(max_length = 200, null = True, blank = True)
    tradeJson = models.JSONField()

    def __str__(self):
        return self.tradeJson["s"]
    