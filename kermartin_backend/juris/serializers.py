from rest_framework import serializers
from .models import Jurisprudencia


class JurisprudenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jurisprudencia
        fields = (
            'id', 'titulo', 'tribunal', 'data_julgamento', 'ementa', 'fundamentacao',
            'pontos_estrategicos', 'teses_defensivas', 'tema', 'link', 'vinculante', 'dispositivos_citados', 'fase', 'bloco', 'criado_em'
        )

