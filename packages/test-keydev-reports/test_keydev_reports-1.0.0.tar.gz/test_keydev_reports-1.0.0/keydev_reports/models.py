from django.db import models


class ReportTemplate(models.Model):
    """
    Модель шаблона отчета.
    """
    name: models.CharField = models.CharField(max_length=100, verbose_name='Название отчета')
    related_model: models.CharField = models.CharField(max_length=100, verbose_name='Модель', null=True, blank=True)
    file: models.FileField = models.FileField(upload_to='keydev_reports/report_templates/', max_length=255,
                                              verbose_name='Файл')
    is_active: models.BooleanField = models.BooleanField(default=True, verbose_name='Активен')
    product: models.CharField = models.CharField(max_length=100, verbose_name='Продукт', null=True, blank=True)

    class Meta:
        verbose_name = 'Шаблон отчета'
        verbose_name_plural = 'Шаблоны отчетов'

    def __str__(self):
        return self.name
