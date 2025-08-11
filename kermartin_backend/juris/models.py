from django.db import models


class Jurisprudencia(models.Model):
    titulo = models.CharField(max_length=255)
    tribunal = models.CharField(max_length=100, blank=True, null=True)
    data_julgamento = models.DateField(blank=True, null=True)
    ementa = models.TextField(blank=True, null=True)
    fundamentacao = models.TextField(blank=True, null=True)
    pontos_estrategicos = models.TextField(blank=True, null=True)
    teses_defensivas = models.TextField(blank=True, null=True)
    tema = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    vinculante = models.BooleanField(default=False)
    dispositivos_citados = models.JSONField(blank=True, null=True, default=list)
    fase = models.CharField(max_length=100, blank=True, null=True)
    bloco = models.IntegerField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_julgamento', '-id']
        verbose_name = 'Jurisprudência'
        verbose_name_plural = 'Jurisprudências'

    def __str__(self) -> str:
        return self.titulo


class JurisEmbedding(models.Model):
    jurisprudencia = models.OneToOneField(Jurisprudencia, on_delete=models.CASCADE, related_name='embedding')
    embedding = models.JSONField()  # lista de floats
    dim = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Embedding de Jurisprudência'
        verbose_name_plural = 'Embeddings de Jurisprudência'

    def __str__(self) -> str:
        return f"Embedding({self.jurisprudencia_id}, dim={self.dim})"

