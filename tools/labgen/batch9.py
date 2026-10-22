# -*- coding: utf-8 -*-
"""Лаба 11: отчёты РейтингУслуг и РейтингМатериалов (запрос с левым соединением к Продажи.Обороты, параметры периода, условное оформление)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

DATE_ONLY = '<v8:Type>xs:dateTime</v8:Type>\n\t\t\t<v8:DateQualifiers>\n\t\t\t\t<v8:DateFractions>Date</v8:DateFractions>\n\t\t\t</v8:DateQualifiers>'
ENUM_VID = '<v8:Type xmlns:d4p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d4p1:EnumRef.ВидыНоменклатуры</v8:Type>'

def quick_param(name, value_xml, key):
    """Параметр данных в быстрых пользовательских настройках (viewMode QuickAccess)."""
    return (f'\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>{name}</dcscor:parameter>\n\t\t\t\t\t{value_xml}\n'
            f'\t\t\t\t\t<dcsset:viewMode>QuickAccess</dcsset:viewMode>\n\t\t\t\t\t<dcsset:userSettingID>{U(key)}</dcsset:userSettingID>\n\t\t\t\t</dcscor:item>\n')

def rating_report(name, synonym, title, vid_value, entity_alias, res_expr, res_alias, res_title, threshold, appearance_title, query_title):
    query = f'''ВЫБРАТЬ
	СпрНоменклатура.Ссылка КАК {entity_alias},
	ПродажиОбороты.{res_expr} КАК {res_alias}
ИЗ
	Справочник.Номенклатура КАК СпрНоменклатура
		ЛЕВОЕ СОЕДИНЕНИЕ РегистрНакопления.Продажи.Обороты(&НачалоПериода, &КонецПериода, , ) КАК ПродажиОбороты
		ПО (ПродажиОбороты.Номенклатура = СпрНоменклатура.Ссылка)
ГДЕ
	НЕ СпрНоменклатура.ЭтоГруппа
	И СпрНоменклатура.ВидНоменклатуры = &ВидНоменклатуры

УПОРЯДОЧИТЬ ПО
	{res_alias} УБЫВ'''
    fields = dcs_field(entity_alias) + dcs_field(res_alias, res_title)
    params = (dcs_param('НачалоПериода', 'Дата начала', DATE_ONLY, DATE_ZERO, restrict=False) +
              dcs_param('КонецПериода', None, DATE_TYPE, DATE_ZERO, expr='КонецПериода(&ДатаОкончания, "День")', restrict=True) +
              dcs_param('ДатаОкончания', 'Дата окончания', DATE_ONLY, DATE_ZERO, restrict=False) +
              dcs_param('ВидНоменклатуры', None, ENUM_VID, f'<value xsi:type="dcscor:DesignTimeValue">Перечисление.ВидыНоменклатуры.{vid_value}</value>', restrict=True))
    sel = sel_items([entity_alias, res_alias], 4)
    dparams = (quick_param('НачалоПериода', std_date('BeginningOfThisMonth'), f'Q/{name}/нач') +
               quick_param('ДатаОкончания', std_date('BeginningOfThisDay'), f'Q/{name}/кон'))
    appearance = (f'\t\t\t<dcsset:conditionalAppearance>\n\t\t\t\t<dcsset:item>\n\t\t\t\t\t<dcsset:selection>\n'
                  f'\t\t\t\t\t\t<dcsset:item>\n\t\t\t\t\t\t\t<dcsset:field>{entity_alias}</dcsset:field>\n\t\t\t\t\t\t</dcsset:item>\n'
                  f'\t\t\t\t\t\t<dcsset:item>\n\t\t\t\t\t\t\t<dcsset:field>{res_alias}</dcsset:field>\n\t\t\t\t\t\t</dcsset:item>\n\t\t\t\t\t</dcsset:selection>\n'
                  f'\t\t\t\t\t<dcsset:filter>\n\t\t\t\t\t\t<dcsset:item xsi:type="dcsset:FilterItemComparison">\n'
                  f'\t\t\t\t\t\t\t<dcsset:left xsi:type="dcscor:Field">{res_alias}</dcsset:left>\n\t\t\t\t\t\t\t<dcsset:comparisonType>Less</dcsset:comparisonType>\n'
                  f'\t\t\t\t\t\t\t<dcsset:right xsi:type="xs:decimal">{threshold}</dcsset:right>\n\t\t\t\t\t\t</dcsset:item>\n\t\t\t\t\t</dcsset:filter>\n'
                  f'\t\t\t\t\t<dcsset:appearance>\n\t\t\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t\t\t<dcscor:parameter>ЦветТекста</dcscor:parameter>\n'
                  f'\t\t\t\t\t\t\t<dcscor:value xsi:type="v8ui:Color">#FF0000</dcscor:value>\n\t\t\t\t\t\t</dcscor:item>\n\t\t\t\t\t</dcsset:appearance>\n'
                  f'\t\t\t\t\t<dcsset:presentation xsi:type="xs:string">{appearance_title}</dcsset:presentation>\n\t\t\t\t\t<dcsset:viewMode>Normal</dcsset:viewMode>\n'
                  f'\t\t\t\t\t<dcsset:userSettingID>{U("Q/"+name+"/оформление")}</dcsset:userSettingID>\n\t\t\t\t</dcsset:item>\n\t\t\t</dcsset:conditionalAppearance>\n'
                  f'\t\t\t<dcsset:outputParameters>\n\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:parameter>Заголовок</dcscor:parameter>\n'
                  f'\t\t\t\t\t<dcscor:value xsi:type="xs:string">{title}</dcscor:value>\n\t\t\t\t</dcscor:item>\n\t\t\t</dcsset:outputParameters>\n')
    detail = ('\t\t\t<dcsset:item xsi:type="dcsset:StructureItemGroup">\n\t\t\t\t<dcsset:order>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:OrderItemField">\n'
              f'\t\t\t\t\t\t<dcsset:field>{res_alias}</dcsset:field>\n\t\t\t\t\t\t<dcsset:orderType>Desc</dcsset:orderType>\n\t\t\t\t\t</dcsset:item>\n\t\t\t\t</dcsset:order>\n'
              '\t\t\t\t<dcsset:selection>\n\t\t\t\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n\t\t\t\t</dcsset:selection>\n\t\t\t</dcsset:item>\n')
    sch = dcs_schema(fields, query, [(res_alias, f'Сумма({res_alias})')], params, sel, dparams, detail, extra_settings=appearance)
    report_files(name, sch, ['ОказаниеУслуг', 'Бухгалтерия'], synonym=synonym)

rating_report('РейтингУслуг', 'Рейтинг услуг', 'Рейтинг услуг', 'Услуга', 'Услуга', 'ВыручкаОборот', 'Выручка', 'Выручка', 5000,
              'Непопулярная услуга', 'Услуги')
rating_report('РейтингМатериалов', 'Рейтинг материалов', 'Рейтинг материалов', 'Материал', 'Материал', 'КоличествоОборот', 'Количество', 'Количество', 3,
              'Малоколичественный материал', 'Материалы')
print('batch9 ok')
