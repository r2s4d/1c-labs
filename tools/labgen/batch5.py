# -*- coding: utf-8 -*-
"""Лаба 7: перечисление ВидыНоменклатуры, реквизит ВидНоменклатуры, проведение только материалов, проверка вида в ПриходнаяНакладная."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *
import forms

# ===== Перечисление =====
def enum_xml(name, values):
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Enum uuid="{U("E/"+name)}">\n\t\t<InternalInfo>\n'
    for k, c in (('EnumRef', 'Ref'), ('EnumManager', 'Manager'), ('EnumList', 'List')):
        o += gtype(k, name, c)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n' + f'\t\t\t<Name>{name}</Name>\n' + syn(human(name), 3)
    o += ('\t\t\t<Comment/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n\t\t\t<Characteristics/>\n\t\t\t<QuickChoice>true</QuickChoice>\n'
          '\t\t\t<ChoiceMode>BothWays</ChoiceMode>\n\t\t\t<DefaultListForm/>\n\t\t\t<DefaultChoiceForm/>\n\t\t\t<AuxiliaryListForm/>\n\t\t\t<AuxiliaryChoiceForm/>\n'
          '\t\t\t<ListPresentation/>\n\t\t\t<ExtendedListPresentation/>\n\t\t\t<Explanation/>\n\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n'
          '\t\t</Properties>\n\t\t<ChildObjects>\n')
    for v in values:
        o += (f'\t\t\t<EnumValue uuid="{U("EV/"+name+"/"+v)}">\n\t\t\t\t<Properties>\n\t\t\t\t\t<Name>{v}</Name>\n' + syn(v, 5) +
              '\t\t\t\t\t<Comment/>\n\t\t\t\t</Properties>\n\t\t\t</EnumValue>\n')
    o += '\t\t</ChildObjects>\n\t</Enum>\n</MetaDataObject>'
    return o

write('Enums/ВидыНоменклатуры.xml', enum_xml('ВидыНоменклатуры', ['Материал', 'Услуга']))
cfg_add('Enum', 'ВидыНоменклатуры')

# ===== Реквизит ВидНоменклатуры у справочника Номенклатура =====
p = 'Catalogs/Номенклатура.xml'
t = read(p)
if '<Name>ВидНоменклатуры</Name>' not in t:
    attr = attr_xml('Attribute', 'CA/Номенклатура/ВидНоменклатуры', 'ВидНоменклатуры', t_ref('EnumRef.ВидыНоменклатуры'), 'DontCheck', None, ind=3,
                    syn_text='Вид номенклатуры')
    attr = attr.replace('\t\t\t\t\t<Indexing>DontIndex</Indexing>', '\t\t\t\t\t<Use>ForItem</Use>\n\t\t\t\t\t<Indexing>DontIndex</Indexing>')
    assert '\t\t<ChildObjects/>' in t
    t = t.replace('\t\t<ChildObjects/>', '\t\t<ChildObjects>\n' + attr + '\t\t</ChildObjects>')
    write(p, t)

# ===== Проведение ОказаниеУслуги: только материалы =====
write('Documents/ОказаниеУслуги/Ext/ObjectModule.bsl',
'''Процедура ОбработкаПроведения(Отказ, Режим)
	//{{__КОНСТРУКТОР_ДВИЖЕНИЙ_РЕГИСТРОВ
	// Данный фрагмент построен конструктором.
	// При повторном использовании конструктора, внесенные вручную изменения будут утеряны!!!

	// регистр ОстаткиМатериалов Расход
	Движения.ОстаткиМатериалов.Записывать = Истина;
	Для Каждого ТекСтрокаПереченьНоменклатуры Из ПереченьНоменклатуры Цикл
		Если ТекСтрокаПереченьНоменклатуры.Номенклатура.ВидНоменклатуры <> Перечисления.ВидыНоменклатуры.Материал Тогда
			Продолжить;
		КонецЕсли;
		Движение = Движения.ОстаткиМатериалов.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Расход;
		Движение.Период = Дата;
		Движение.Материал = ТекСтрокаПереченьНоменклатуры.Номенклатура;
		Движение.Склад = Склад;
		Движение.Количество = ТекСтрокаПереченьНоменклатуры.Количество;
	КонецЦикла;
	//}}__КОНСТРУКТОР_ДВИЖЕНИЙ_РЕГИСТРОВ
КонецПроцедуры
''')

# ===== ПриходнаяНакладная: проверка вида номенклатуры при выборе материала =====
s = forms.S['ПриходнаяНакладная']
new_handler = '''&НаКлиенте
Процедура МатериалыМатериалПриИзменении(Элемент)
	//Получить текущую строку табличной части
	СтрокаТабличнойЧасти = Элементы.Материалы.ТекущиеДанные;

	//Проверка вида номенклатуры
	Проверка = ПроверкаВидаНоменклатуры(СтрокаТабличнойЧасти.Материал);
	Если Проверка Тогда
		//Установить цену
		СтрокаТабличнойЧасти.Цена = РаботаСоСправочниками.РозничнаяЦена(Объект.Дата, СтрокаТабличнойЧасти.Материал);
		//пересчитать сумму строки
		РаботаСДокументами.РассчитатьСумму(СтрокаТабличнойЧасти);
	Иначе
		Сообщить("В документе ПриходнаяНакладная можно выбирать только материалы. Выберите материал!");
	КонецЕсли;
КонецПроцедуры
'''
server_fn = '''&НаСервере
Функция ПроверкаВидаНоменклатуры(Материал)
	Если Материал.ВидНоменклатуры = Перечисления.ВидыНоменклатуры.Материал Тогда
		Рез = Истина;
	Иначе
		Рез = Ложь;
	КонецЕсли;
	Возврат Рез;
КонецФункции
'''
hs = s['handlers']
for i, h in enumerate(hs):
    if 'Процедура МатериалыМатериалПриИзменении' in h:
        hs[i] = new_handler
        break
else:
    raise SystemExit('batch5: handler МатериалыМатериалПриИзменении не найден (batch4 должен идти раньше)')
if not any('ПроверкаВидаНоменклатуры(Материал)' in h and 'Функция' in h for h in hs):
    hs.append(server_fn)
print('batch5 ok')
