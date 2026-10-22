# -*- coding: utf-8 -*-
"""Лаба 14: оптимизация проведения ОказаниеУслуги: запрос + временная таблица вместо обращения через точку, стоимость по среднему.
Реквизит Стоимость табличной части больше не нужен (удаляется, как в лекции 19)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *
import forms

# ===== Удаляем реквизит ПереченьНоменклатуры.Стоимость (он был добавлен лабой 8) =====
p = 'Documents/ОказаниеУслуги.xml'
t = read(p)
m = re.search(r'\t\t\t\t\t<Attribute uuid="[0-9a-f-]+">\n\t\t\t\t\t\t<Properties>\n\t\t\t\t\t\t\t<Name>Стоимость</Name>.*?\t\t\t\t\t</Attribute>\n', t, re.S)
if m:
    t = t[:m.start()] + t[m.end():]
    write(p, t)
cols = forms.S['ОказаниеУслуги']['columns']
forms.S['ОказаниеУслуги']['columns'] = [c for c in cols if c[0] != 'Стоимость']

from posting import posting_module

write('Documents/ОказаниеУслуги/Ext/ObjectModule.bsl', posting_module(False))
print('batch12 ok')
