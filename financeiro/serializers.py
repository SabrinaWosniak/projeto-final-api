from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import Categoria, Conta, Lancamento


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ContaSerializer(serializers.ModelSerializer):
    saldo = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Conta
        fields = ['id', 'nome', 'banco', 'criada_em', 'saldo']


class LancamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lancamento
        fields = '__all__'

    # ---- Validações de campo ----
    def validate_valor(self, v):
        if v <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        return v

    def validate_descricao(self, texto):
        texto = texto.strip()
        if len(texto) < 3:
            raise ValidationError('A descrição deve ter pelo menos 3 caracteres.')
        return texto

    # ---- REGRA DE NEGÓCIO: a conta nunca pode ficar com saldo negativo ----
    def validate(self, dados):
        inst = self.instance
        conta = dados.get('conta') or (inst.conta if inst else None)
        tipo = dados.get('tipo') or (inst.tipo if inst else None)
        valor = dados.get('valor') or (inst.valor if inst else None)

        saldo = conta.saldo
        if inst and inst.conta_id == conta.id:
            saldo -= inst.efeito  # tira o efeito antigo deste lançamento
        elif inst and inst.tipo == 'entrada' and inst.conta.saldo - inst.valor < 0:
            raise ValidationError(
                {'conta': 'Mover esta entrada deixaria a conta de origem com saldo negativo.'})

        efeito = valor if tipo == 'entrada' else -valor
        if saldo + efeito < 0:
            raise ValidationError(
                {'valor': f'Saldo insuficiente. Saldo disponível: {saldo:.2f}.'})
        return dados
