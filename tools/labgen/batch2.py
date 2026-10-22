# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

QUERY = '''ВЫБРАТЬ
	ОстаткиМатериаловОстаткиИОбороты.Склад КАК Склад,
	ОстаткиМатериаловОстаткиИОбороты.Материал КАК Материал,
	ОстаткиМатериаловОстаткиИОбороты.КоличествоНачальныйОстаток КАК НачальныйОстаток,
	ОстаткиМатериаловОстаткиИОбороты.КоличествоПриход КАК Приход,
	ОстаткиМатериаловОстаткиИОбороты.КоличествоРасход КАК Расход,
	ОстаткиМатериаловОстаткиИОбороты.КоличествоКонечныйОстаток КАК КонечныйОстаток
ИЗ
	РегистрНакопления.ОстаткиМатериалов.ОстаткиИОбороты(&НачалоПериода, &КонецПериода, , ) КАК ОстаткиМатериаловОстаткиИОбороты'''
FIELDS = ['Склад', 'Материал', 'НачальныйОстаток', 'Приход', 'Расход', 'КонечныйОстаток']
def fields_xml():
    return ''.join(dcs_field(f) for f in FIELDS)
TOTALS = [(f, f'Сумма({f})') for f in FIELDS[2:]]
def params_xml():
    return (dcs_param('НачалоПериода', 'Начало периода', DATE_TYPE, DATE_ZERO, restrict=False) +
            dcs_param('КонецПериода', 'Конец периода', DATE_TYPE, DATE_ZERO, restrict=False))

# --- Материалы: общий итог ---
sch = dcs_schema(fields_xml(), QUERY, TOTALS, params_xml(), sel_items(FIELDS, 4),
    data_param('НачалоПериода', '<dcscor:value xsi:type="xs:dateTime">0001-01-01T00:00:00</dcscor:value>', 'Q/Мат/нач') +
    data_param('КонецПериода', '<dcscor:value xsi:type="xs:dateTime">0001-01-01T00:00:00</dcscor:value>', 'Q/Мат/кон'),
    group_item(None, '', 3))
report_files('Материалы', sch, ['Бухгалтерия', 'УчетМатериалов', 'ОказаниеУслуг'])

# --- Материалы на складах: группировка по складу + детальные записи, периоды по умолчанию ---
detail = group_item(None, '', 4)
sch2 = dcs_schema(fields_xml(), QUERY, TOTALS, params_xml(), sel_items(FIELDS, 4),
    data_param('НачалоПериода', std_date('BeginningOfThisMonth'), 'Q/МНС/нач') +
    data_param('КонецПериода', std_date('BeginningOfNextMonth'), 'Q/МНС/кон'),
    group_item('Склад', detail, 3))
report_files('МатериалыНаСкладах', sch2, ['Бухгалтерия', 'УчетМатериалов', 'ОказаниеУслуг'], synonym='Материалы на складах')
print('batch2 ok')
