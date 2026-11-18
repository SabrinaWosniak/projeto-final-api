from decimal import Decimal, InvalidOperation

from django.utils.dateparse import parse_date
from rest_framework import filters, viewsets
from rest_framework.serializers import ValidationError

from .models import Categoria, Conta, Lancamento
from .serializers import CategoriaSerializer, ContaSerializer, LancamentoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by('nome')
    serializer_class = CategoriaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['id', 'nome']


class ContaViewSet(viewsets.ModelViewSet):
    queryset = Conta.objects.all().order_by('nome')
    serializer_class = ContaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'banco']
    ordering_fields = ['id', 'nome', 'criada_em']


class LancamentoViewSet(viewsets.ModelViewSet):
    queryset = Lancamento.objects.select_related('conta', 'categoria').order_by('-data', '-id')
    serializer_class = LancamentoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descricao']          # ?search=mercado
    ordering_fields = ['data', 'valor', 'id']  # ?ordering=-valor

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        erros = {}

        tipo = p.get('tipo')
        if tipo:
            if tipo not in ('entrada', 'saida'):
                erros['tipo'] = "Use 'entrada' ou 'saida'."
            else:
                qs = qs.filter(tipo=tipo)

        for campo in ('conta', 'categoria'):
            v = p.get(campo)
            if v:
                if not v.isdigit():
                    erros[campo] = 'Informe o id (número).'
                else:
                    qs = qs.filter(**{f'{campo}_id': int(v)})

        for param, lookup in (('data_inicio', 'data__gte'), ('data_fim', 'data__lte')):
            v = p.get(param)
            if v:
                try:
                    d = parse_date(v)
                except ValueError:
                    d = None
                if d is None:
                    erros[param] = 'Use o formato AAAA-MM-DD.'
                else:
                    qs = qs.filter(**{lookup: d})

        for param, lookup in (('valor_min', 'valor__gte'), ('valor_max', 'valor__lte')):
            v = p.get(param)
            if v:
                try:
                    qs = qs.filter(**{lookup: Decimal(v)})
                except InvalidOperation:
                    erros[param] = 'Informe um número.'

        if erros:
            raise ValidationError(erros)
        return qs

    def perform_destroy(self, instance):
        # Regra de negócio: não excluir uma entrada se isso deixar o saldo negativo
        if instance.tipo == 'entrada' and instance.conta.saldo - instance.valor < 0:
            raise ValidationError(
                'Não é possível excluir: a conta ficaria com saldo negativo.')
        instance.delete()
