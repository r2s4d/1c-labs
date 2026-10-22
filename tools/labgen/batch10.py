# -*- coding: utf-8 -*-
"""Лаба 12: отчёт ВыручкаМастеров: группировки Мастер -> Период (с дополнением всех дней) -> Клиенты, второй вариант ОбъемВыручки: измерительная диаграмма."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

DATE_ONLY = '<v8:Type>xs:dateTime</v8:Type>\n\t\t\t<v8:DateQualifiers>\n\t\t\t\t<v8:DateFractions>Date</v8:DateFractions>\n\t\t\t</v8:DateQualifiers>'
_UNUSED = ('\t\t\t\t<dcsset:order>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n\t\t\t\t</dcsset:order>\n'
        '\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n\t\t\t\t</dcsset:selection>\n')

def qparam(name, value_xml, key, use=True):
    u = '' if use else '\t\t\t\t\t<dcscor:use>false</dcscor:use>\n'
    return (f'\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n{u}\t\t\t\t\t<dcscor:parameter>{name}</dcscor:parameter>\n\t\t\t\t\t{value_xml}\n'
            f'\t\t\t\t\t<dcsset:viewMode>QuickAccess</dcsset:viewMode>\n\t\t\t\t\t<dcsset:userSettingID>{U(key)}</dcsset:userSettingID>\n\t\t\t\t</dcscor:item>\n')

def group(field, inner, period=False, ind=3):
    t = '\t' * ind
    if period:
        gi = ('\t\t<dcsset:groupItems>\n\t\t\t<dcsset:item xsi:type="dcsset:GroupItemField">\n\t\t\t\t<dcsset:field>Период</dcsset:field>\n'
              '\t\t\t\t<dcsset:groupType>Items</dcsset:groupType>\n\t\t\t\t<dcsset:periodAdditionType>Day</dcsset:periodAdditionType>\n'
              '\t\t\t\t<dcsset:periodAdditionBegin xsi:type="dcscor:Field">DataParameters.НачалоПериода</dcsset:periodAdditionBegin>\n'
              '\t\t\t\t<dcsset:periodAdditionEnd xsi:type="dcscor:Field">DataParameters.ДатаОкончания</dcsset:periodAdditionEnd>\n'
              '\t\t\t</dcsset:item>\n\t\t</dcsset:groupItems>\n')
    elif field:
        gi = (f'\t\t<dcsset:groupItems>\n\t\t\t<dcsset:item xsi:type="dcsset:GroupItemField">\n\t\t\t\t<dcsset:field>{field}</dcsset:field>\n'
              '\t\t\t\t<dcsset:groupType>Items</dcsset:groupType>\n\t\t\t\t<dcsset:periodAdditionType>None</dcsset:periodAdditionType>\n'
              '\t\t\t\t<dcsset:periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionBegin>\n'
              '\t\t\t\t<dcsset:periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionEnd>\n'
              '\t\t\t</dcsset:item>\n\t\t</dcsset:groupItems>\n')
    else:
        gi = ''
    out = f'{t}<dcsset:item xsi:type="dcsset:StructureItemGroup">\n'
    for ln in gi.splitlines():
        out += '\t' * (ind - 2) + ln + '\n'
    out += (f'{t}\t<dcsset:order>\n{t}\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n{t}\t</dcsset:order>\n'
            f'{t}\t<dcsset:selection>\n{t}\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n{t}\t</dcsset:selection>\n{inner}{t}</dcsset:item>\n')
    return out

QUERY = '''ВЫБРАТЬ
	ПродажиОбороты.Мастер КАК Мастер,
	ПродажиОбороты.Период КАК Период,
	ПродажиОбороты.Клиент КАК Клиент,
	ПродажиОбороты.ВыручкаОборот КАК Выручка
ИЗ
	РегистрНакопления.Продажи.Обороты(&НачалоПериода, &КонецПериода, День, ) КАК ПродажиОбороты'''
fields = dcs_field('Мастер') + dcs_field('Период') + dcs_field('Клиент') + dcs_field('Выручка')
params = (dcs_param('НачалоПериода', 'Дата начала', DATE_ONLY, DATE_ZERO, restrict=False) +
          dcs_param('КонецПериода', None, DATE_TYPE, DATE_ZERO, expr='КонецПериода(&ДатаОкончания, "День")', restrict=True) +
          dcs_param('ДатаОкончания', 'Дата окончания', DATE_ONLY, DATE_ZERO, restrict=False))
title_param = lambda s: ('\t\t\t<dcsset:outputParameters>\n\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>Заголовок</dcscor:parameter>\n'
                         f'\t\t\t\t\t<dcscor:value xsi:type="xs:string">{s}</dcscor:value>\n\t\t\t\t</dcscor:item>\n')

# --- Основной вариант: Мастер -> Период (дополнение дней) -> детальные записи ---
detail = group(None, '', ind=5)
by_period = group(None, detail, period=True, ind=4)
structure = group('Мастер', by_period, ind=3)
dparams = (qparam('НачалоПериода', std_date('BeginningOfThisMonth'), 'Q/ВыручкаМастеров/нач') +
           qparam('ДатаОкончания', std_date('BeginningOfThisDay'), 'Q/ВыручкаМастеров/кон'))
sch = dcs_schema(fields, QUERY, [('Выручка', 'Сумма(Выручка)')], params, sel_items(['Клиент', 'Выручка'], 4), dparams, structure,
                 extra_settings=title_param('Выручка мастеров') + '\t\t\t</dcsset:outputParameters>\n')

# --- Вариант ОбъемВыручки: измерительная диаграмма по мастерам ---
d2 = (qparam('НачалоПериода', std_date('BeginningOfThisMonth'), 'Q/ВыручкаМастеров/диагр/нач', use=False) +
      qparam('ДатаОкончания', std_date('BeginningOfThisDay'), 'Q/ВыручкаМастеров/диагр/кон', use=False))
chart = ('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemChart">\n\t\t\t\t<dcsset:point>\n\t\t\t\t\t<dcsset:groupItems>\n\t\t\t\t\t\t<dcsset:item xsi:type="dcsset:GroupItemField">\n'
         '\t\t\t\t\t\t\t<dcsset:field>Мастер</dcsset:field>\n\t\t\t\t\t\t\t<dcsset:groupType>Items</dcsset:groupType>\n\t\t\t\t\t\t\t<dcsset:periodAdditionType>None</dcsset:periodAdditionType>\n'
         '\t\t\t\t\t\t\t<dcsset:periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionBegin>\n'
         '\t\t\t\t\t\t\t<dcsset:periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionEnd>\n'
         '\t\t\t\t\t\t</dcsset:item>\n\t\t\t\t\t</dcsset:groupItems>\n\t\t\t\t\t<dcsset:order>\n\t\t\t\t\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n\t\t\t\t\t</dcsset:order>\n'
         '\t\t\t\t\t<dcsset:selection>\n\t\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n\t\t\t\t\t</dcsset:selection>\n\t\t\t\t</dcsset:point>\n'
         '\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n\t\t\t\t</dcsset:selection>\n\t\t\t</dcsset:item>\n')
variant2 = ('\t<settingsVariant>\n\t\t<dcsset:name>ОбъемВыручки</dcsset:name>\n\t\t<dcsset:presentation xsi:type="xs:string">Объем выручки</dcsset:presentation>\n'
            f'\t\t<dcsset:settings {SET_NS}>\n\t\t\t<dcsset:selection>\n' + sel_items(['Выручка'], 4) + '\t\t\t</dcsset:selection>\n'
            '\t\t\t<dcsset:dataParameters>\n' + d2 + '\t\t\t</dcsset:dataParameters>\n'
            '\t\t\t<dcsset:outputParameters>\n\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>ТипДиаграммы</dcscor:parameter>\n'
            '\t\t\t\t\t<dcscor:value xsi:type="v8ui:ChartType">Gauge</dcscor:value>\n\t\t\t\t</dcscor:item>\n'
            '\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>Заголовок</dcscor:parameter>\n'
            '\t\t\t\t\t<dcscor:value xsi:type="xs:string">Объем выручки</dcscor:value>\n\t\t\t\t</dcscor:item>\n\t\t\t</dcsset:outputParameters>\n'
            + chart + '\t\t</dcsset:settings>\n\t</settingsVariant>\n')
assert sch.endswith('</DataCompositionSchema>')
sch = sch[:-len('</DataCompositionSchema>')] + variant2 + '</DataCompositionSchema>'
report_files('ВыручкаМастеров', sch, ['ОказаниеУслуг', 'РасчетЗарплаты'], synonym='Выручка мастеров')
print('batch10 ok')
