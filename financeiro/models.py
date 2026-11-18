from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Categoria(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.nome


class Conta(models.Model):
    nome = models.CharField(max_length=100)
    banco = models.CharField(max_length=60, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    @property
    def saldo(self):
        zero = Decimal('0.00')
        entradas = self.lancamentos.filter(tipo='entrada').aggregate(t=Sum('valor'))['t'] or zero
        saidas = self.lancamentos.filter(tipo='saida').aggregate(t=Sum('valor'))['t'] or zero
        return entradas - saidas

    def __str__(self):
        return self.nome


class Lancamento(models.Model):
    TIPOS = [('entrada', 'Entrada'), ('saida', 'Saída')]

    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='lancamentos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='lancamentos')
    tipo = models.CharField(max_length=7, choices=TIPOS)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data = models.DateField()

    @property
    def efeito(self):
        """Quanto este lançamento soma (+) ou subtrai (-) do saldo."""
        return self.valor if self.tipo == 'entrada' else -self.valor

    def __str__(self):
        return f'{self.descricao} ({self.tipo})'
