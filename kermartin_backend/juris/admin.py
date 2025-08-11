from django.contrib import admin
from .models import Jurisprudencia

@admin.register(Jurisprudencia)
class JurisprudenciaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tribunal", "data_julgamento", "tema")
    list_filter = ("tribunal", "tema")
    search_fields = ("titulo", "ementa", "fundamentacao", "teses_defensivas")

