# -*- coding: utf-8 -*-
"""Лаба 13: отчёты ЦеныНаУслуги (срез последних, иерархия, вариант-гистограмма), РейтингКлиентов (вычисляемое поле, диаграмма), Универсальный."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

DATE_ONLY = '<v8:Type>xs:dateTime</v8:Type>\n\t\t\t<v8:DateQualifiers>\n\t\t\t\t<v8:DateFractions>Date</v8:DateFractions>\n\t\t\t</v8:DateQualifiers>'
ENUM_VID = '<v8:Type xmlns:d4p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d4p1:EnumRef.ВидыНоменклатуры</v8:Type>'

def qparam(name, value_xml, key, use=True):
    u = '' if use else '\t\t\t\t\t<dcscor:use>false</dcscor:use>\n'
    return (f'\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n{u}\t\t\t\t\t<dcscor:parameter>{name}</dcscor:parameter>\n\t\t\t\t\t{value_xml}\n'
            f'\t\t\t\t\t<dcsset:viewMode>QuickAccess</dcsset:viewMode>\n\t\t\t\t\t<dcsset:userSettingID>{U(key)}</dcsset:userSettingID>\n\t\t\t\t</dcscor:item>\n')

def out_params(title, chart_type=None, chart_quick_key=None):
    o = '\t\t\t<dcsset:outputParameters>\n'
    if chart_type:
        q = (f'\t\t\t\t\t<dcsset:viewMode>QuickAccess</dcsset:viewMode>\n\t\t\t\t\t<dcsset:userSettingID>{U(chart_quick_key)}</dcsset:userSettingID>\n' if chart_quick_key else '')
        o += ('\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>ТипДиаграммы</dcscor:parameter>\n'
              f'\t\t\t\t\t<dcscor:value xsi:type="v8ui:ChartType">{chart_type}</dcscor:value>\n{q}\t\t\t\t</dcscor:item>\n')
    o += ('\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>Заголовок</dcscor:parameter>\n'
          f'\t\t\t\t\t<dcscor:value xsi:type="xs:string">{title}</dcscor:value>\n\t\t\t\t</dcscor:item>\n\t\t\t</dcsset:outputParameters>\n')
    return o

AUTO_OS = ('\t\t\t\t<dcsset:order>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n\t\t\t\t</dcsset:order>\n'
           '\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n\t\t\t\t</dcsset:selection>\n')

def group_field(field, gtype='Items'):
    return (f'\t\t\t\t<dcsset:groupItems>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:GroupItemField">\n\t\t\t\t\t\t<dcsset:field>{field}</dcsset:field>\n'
            f'\t\t\t\t\t\t<dcsset:groupType>{gtype}</dcsset:groupType>\n\t\t\t\t\t\t<dcsset:periodAdditionType>None</dcsset:periodAdditionType>\n'
            '\t\t\t\t\t\t<dcsset:periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionBegin>\n'
            '\t\t\t\t\t\t<dcsset:periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionEnd>\n\t\t\t\t\t</dcsset:item>\n\t\t\t\t</dcsset:groupItems>\n')

def group(field, inner='', gtype='Items'):
    return ('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemGroup">\n' + (group_field(field, gtype) if field else '') + AUTO_OS + inner + '\t\t\t</dcsset:item>\n')

def chart_item(point_field):
    return ('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemChart">\n\t\t\t\t<dcsset:point>\n' + group_field(point_field).replace('\t\t\t\t', '\t\t\t\t\t', 1) +
            AUTO_OS.replace('\t\t\t\t', '\t\t\t\t\t') + '\t\t\t\t</dcsset:point>\n\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n'
            '\t\t\t\t</dcsset:selection>\n\t\t\t</dcsset:item>\n')

def add_variant(sch, name, presentation, selection_fields, dparams, outputs, structure):
    v = (f'\t<settingsVariant>\n\t\t<dcsset:name>{name}</dcsset:name>\n\t\t<dcsset:presentation xsi:type="xs:string">{presentation}</dcsset:presentation>\n'
         f'\t\t<dcsset:settings {SET_NS}>\n\t\t\t<dcsset:selection>\n' + sel_items(selection_fields, 4) + '\t\t\t</dcsset:selection>\n' +
         ('\t\t\t<dcsset:dataParameters>\n' + dparams + '\t\t\t</dcsset:dataParameters>\n' if dparams else '') + outputs + structure + '\t\t</dcsset:settings>\n\t</settingsVariant>\n')
    end = '</DataCompositionSchema>'
    assert sch.endswith(end)
    return sch[:-len(end)] + v + end

# ================= ЦеныНаУслуги =================
Q1 = '''ВЫБРАТЬ
	СпрНоменклатура.Родитель КАК ГруппаУслуг,
	СпрНоменклатура.Ссылка КАК Услуга,
	ЦеныСрезПоследних.Цена КАК Цена
ИЗ
	Справочник.Номенклатура КАК СпрНоменклатура
		ЛЕВОЕ СОЕДИНЕНИЕ РегистрСведений.Цены.СрезПоследних(&ДатаОтчета, ) КАК ЦеныСрезПоследних
		ПО (ЦеныСрезПоследних.Номенклатура = СпрНоменклатура.Ссылка)
ГДЕ
	НЕ СпрНоменклатура.ЭтоГруппа
	И СпрНоменклатура.ВидНоменклатуры = &ВидНоменклатуры'''
f1 = dcs_field('ГруппаУслуг') + dcs_field('Услуга') + dcs_field('Цена')
p1 = (dcs_param('ДатаОтчета', 'Дата отчета', DATE_ONLY, DATE_ZERO, restrict=False) +
      dcs_param('ВидНоменклатуры', None, ENUM_VID, '<value xsi:type="dcscor:DesignTimeValue">Перечисление.ВидыНоменклатуры.Услуга</value>', restrict=True))
dp1 = qparam('ДатаОтчета', std_date('BeginningOfThisDay'), 'Q/ЦеныНаУслуги/дата')
struct1 = group('ГруппаУслуг', group(None), gtype='Hierarchy')
sch1 = dcs_schema(f1, Q1, [], p1, sel_items(['Услуга', 'Цена'], 4), dp1, struct1, extra_settings=out_params('Цены на услуги'))
# итог по ресурсу Цена, рассчитываемый по полю Услуга (нужен для диаграммы)
sch1 = sch1.replace('\t<parameter>', '\t<totalField>\n\t\t<dataPath>Цена</dataPath>\n\t\t<expression>Сумма(Цена)</expression>\n\t\t<group>Услуга</group>\n\t</totalField>\n\t<parameter>', 1)
sch1 = add_variant(sch1, 'Гистограмма', 'Гистограмма', ['Цена'], qparam('ДатаОтчета', std_date('BeginningOfThisDay'), 'Q/ЦеныНаУслуги/диагр/дата'),
                   out_params('Цены на услуги (гистограмма)', 'Column'), chart_item('Услуга'))
report_files('ЦеныНаУслуги', sch1, ['ОказаниеУслуг', 'Бухгалтерия'], synonym='Цены на услуги')

# ================= РейтингКлиентов =================
Q2 = '''ВЫБРАТЬ
	ПродажиОбороты.Клиент КАК Клиент,
	ПродажиОбороты.ВыручкаОборот КАК Выручка,
	ПродажиОбороты.СтоимостьОборот КАК Стоимость
ИЗ
	РегистрНакопления.Продажи.Обороты КАК ПродажиОбороты'''
f2 = dcs_field('Клиент') + dcs_field('Выручка') + dcs_field('Стоимость')
calc = ('\t<calculatedField>\n\t\t<dataPath>Доход</dataPath>\n\t\t<expression>Выручка - Стоимость</expression>\n' + lstr('title', 'Доход', 2) + '\t</calculatedField>\n')
sch2 = dcs_schema(f2, Q2, [('Выручка', 'Сумма(Выручка)'), ('Доход', 'Сумма(Доход)'), ('Стоимость', 'Сумма(Стоимость)')], '',
                  sel_items(['Доход'], 4), '', chart_item('Клиент'), extra_top=calc,
                  extra_settings=out_params('Рейтинг клиентов', 'Pie3D', 'Q/РейтингКлиентов/тип'))
report_files('РейтингКлиентов', sch2, ['ОказаниеУслуг', 'Бухгалтерия'], synonym='Рейтинг клиентов')

# ================= Универсальный =================
Q3 = '''ВЫБРАТЬ
	ПродажиОбороты.Номенклатура КАК Номенклатура,
	ПродажиОбороты.Клиент КАК Клиент,
	ПродажиОбороты.Мастер КАК Мастер,
	ПродажиОбороты.КоличествоОборот КАК КоличествоОборот,
	ПродажиОбороты.ВыручкаОборот КАК ВыручкаОборот,
	ПродажиОбороты.СтоимостьОборот КАК СтоимостьОборот
ИЗ
	РегистрНакопления.Продажи.Обороты(&НачалоПериода, &КонецПериода, , ) КАК ПродажиОбороты'''
F3 = ['Номенклатура', 'Клиент', 'Мастер', 'КоличествоОборот', 'ВыручкаОборот', 'СтоимостьОборот']
f3 = ''.join(dcs_field(f) for f in F3)
p3 = (dcs_param('НачалоПериода', 'Начало периода', DATE_TYPE, DATE_ZERO, restrict=False) +
      dcs_param('КонецПериода', 'Конец периода', DATE_TYPE, DATE_ZERO, restrict=False))
table = ('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemTable">\n\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n'
         '\t\t\t\t</dcsset:selection>\n\t\t\t</dcsset:item>\n')
sch3 = dcs_schema(f3, Q3, [(f, f'Сумма({f})') for f in F3[3:]], p3, '', '', table)
report_files('Универсальный', sch3, ['ОказаниеУслуг'], synonym='Универсальный')
print('batch11 ok')
