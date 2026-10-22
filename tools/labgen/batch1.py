# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

# ===== Лаба 2/3: нумератор =====
write('DocumentNumerators/СквознаяНумерация.xml',
 f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<DocumentNumerator uuid="{U("N/СквознаяНумерация")}">\n\t\t<InternalInfo/>\n\t\t<Properties>\n'
 '\t\t\t<Name>СквознаяНумерация</Name>\n' + syn('Сквозная нумерация', 3) +
 '\t\t\t<Comment/>\n\t\t\t<NumberType>String</NumberType>\n\t\t\t<NumberLength>9</NumberLength>\n\t\t\t<NumberAllowedLength>Variable</NumberAllowedLength>\n'
 '\t\t\t<NumberPeriodicity>Nonperiodical</NumberPeriodicity>\n\t\t\t<CheckUnique>true</CheckUnique>\n\t\t</Properties>\n\t</DocumentNumerator>\n</MetaDataObject>')
cfg_add('DocumentNumerator', 'СквознаяНумерация')

# ===== Документ ОказаниеУслуги =====
SKL = t_ref('CatalogRef.Склады'); KLI = t_ref('CatalogRef.Клиенты'); SOT = t_ref('CatalogRef.Сотрудники'); NOM = t_ref('CatalogRef.Номенклатура')
write('Documents/ОказаниеУслуги.xml', document_xml('ОказаниеУслуги', 'Оказание услуг',
  [('Склад', SKL, 'DontCheck', 'Catalog.Склады.Основной'), ('Клиент', KLI, 'ShowError', None), ('Мастер', SOT, 'ShowError', None)],
  [('ПереченьНоменклатуры', 'ShowError', [('Номенклатура', NOM, 'ShowError'), ('Количество', t_num(15, 3), 'ShowError'),
                                          ('Цена', t_num(15, 2), 'ShowError'), ('Сумма', t_num(15, 2), 'ShowError')])],
  numerator='DocumentNumerator.СквознаяНумерация', registers=['AccumulationRegister.ОстаткиМатериалов']))
write('Documents/ОказаниеУслуги/Forms/ФормаДокумента.xml', form_meta_xml('F/ОказаниеУслуги/ФормаДокумента'))
write('Documents/ОказаниеУслуги/Ext/ObjectModule.bsl',
'''Процедура ОбработкаПроведения(Отказ, Режим)
	//{{__КОНСТРУКТОР_ДВИЖЕНИЙ_РЕГИСТРОВ
	// Данный фрагмент построен конструктором.
	// При повторном использовании конструктора, внесенные вручную изменения будут утеряны!!!

	// регистр ОстаткиМатериалов Расход
	Движения.ОстаткиМатериалов.Записывать = Истина;
	Для Каждого ТекСтрокаПереченьНоменклатуры Из ПереченьНоменклатуры Цикл
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
cfg_add('Document', 'ОказаниеУслуги')

# ===== Правки ПриходнаяНакладная =====
p = 'Documents/ПриходнаяНакладная.xml'; t = read(p)
t = t.replace('\t\t\t<Numerator/>', '\t\t\t<Numerator>DocumentNumerator.СквознаяНумерация</Numerator>')
t = t.replace('\t\t\t<RegisterRecords/>', '\t\t\t<RegisterRecords>\n\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">AccumulationRegister.ОстаткиМатериалов</xr:Item>\n\t\t\t</RegisterRecords>')
write(p, t)
write('Documents/ПриходнаяНакладная/Ext/ObjectModule.bsl',
'''Процедура ОбработкаПроведения(Отказ, Режим)
	//{{__КОНСТРУКТОР_ДВИЖЕНИЙ_РЕГИСТРОВ
	// Данный фрагмент построен конструктором.
	// При повторном использовании конструктора, внесенные вручную изменения будут утеряны!!!

	// регистр ОстаткиМатериалов Приход
	Движения.ОстаткиМатериалов.Записывать = Истина;
	Для Каждого ТекСтрокаМатериалы Из Материалы Цикл
		Движение = Движения.ОстаткиМатериалов.Добавить();
		Движение.ВидДвижения = ВидДвиженияНакопления.Приход;
		Движение.Период = Дата;
		Движение.Материал = ТекСтрокаМатериалы.Материал;
		Движение.Склад = Склад;
		Движение.Количество = ТекСтрокаМатериалы.Количество;
	КонецЦикла;
	//}}__КОНСТРУКТОР_ДВИЖЕНИЙ_РЕГИСТРОВ
КонецПроцедуры
''')
# ===== Журнал документов =====
def journal_xml():
    n = 'СкладскиеДокументы'
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<DocumentJournal uuid="{U("J/"+n)}">\n\t\t<InternalInfo>\n'
    for k, c in (('DocumentJournalSelection', 'Selection'), ('DocumentJournalList', 'List'), ('DocumentJournalManager', 'Manager')):
        o += gtype(k, n, c)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n' + f'\t\t\t<Name>{n}</Name>\n' + syn('Складские документы', 3)
    o += ('\t\t\t<Comment/>\n\t\t\t<DefaultForm/>\n\t\t\t<AuxiliaryForm/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n'
          + regrefs(['Document.ПриходнаяНакладная', 'Document.ОказаниеУслуги'], 3, 'RegisteredDocuments') +
          '\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n'
          '\t\t\t<ListPresentation/>\n\t\t\t<ExtendedListPresentation/>\n\t\t\t<Explanation/>\n\t\t</Properties>\n\t\t<ChildObjects>\n')
    o += (f'\t\t\t<Column uuid="{U("JC/Склад")}">\n\t\t\t\t<Properties>\n\t\t\t\t\t<Name>Склад</Name>\n' + syn('Склад', 5) +
          '\t\t\t\t\t<Comment/>\n\t\t\t\t\t<Indexing>DontIndex</Indexing>\n\t\t\t\t\t<References>\n'
          '\t\t\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Document.ПриходнаяНакладная.Attribute.Склад</xr:Item>\n'
          '\t\t\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">Document.ОказаниеУслуги.Attribute.Склад</xr:Item>\n'
          '\t\t\t\t\t</References>\n\t\t\t\t</Properties>\n\t\t\t</Column>\n')
    o += '\t\t</ChildObjects>\n\t</DocumentJournal>\n</MetaDataObject>'
    return o
write('DocumentJournals/СкладскиеДокументы.xml', journal_xml())
cfg_add('DocumentJournal', 'СкладскиеДокументы')

# ===== Регистр накопления ОстаткиМатериалов =====
def accreg_xml(name, rtype, dims, ress, ext_pres='', attrs=()):
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<AccumulationRegister uuid="{U("R/"+name)}">\n\t\t<InternalInfo>\n'
    for k, c in (('AccumulationRegisterRecord', 'Record'), ('AccumulationRegisterManager', 'Manager'), ('AccumulationRegisterSelection', 'Selection'),
                 ('AccumulationRegisterList', 'List'), ('AccumulationRegisterRecordSet', 'RecordSet'), ('AccumulationRegisterRecordKey', 'RecordKey')):
        o += gtype(k, name, c)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n' + f'\t\t\t<Name>{name}</Name>\n' + syn(human(name), 3)
    o += ('\t\t\t<Comment/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n\t\t\t<DefaultListForm/>\n\t\t\t<AuxiliaryListForm/>\n'
          f'\t\t\t<RegisterType>{rtype}</RegisterType>\n\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n'
          '\t\t\t<DataLockControlMode>Managed</DataLockControlMode>\n\t\t\t<EnableTotalsSplitting>true</EnableTotalsSplitting>\n'
          '\t\t\t<FullTextSearch>Use</FullTextSearch>\n\t\t\t<ListPresentation/>\n')
    if ext_pres:
        o += '\t\t\t<ExtendedListPresentation>\n\t\t\t\t<v8:item>\n\t\t\t\t\t<v8:lang>ru</v8:lang>\n' + f'\t\t\t\t\t<v8:content>{ext_pres}</v8:content>\n\t\t\t\t</v8:item>\n\t\t\t</ExtendedListPresentation>\n'
    else:
        o += '\t\t\t<ExtendedListPresentation/>\n'
    o += '\t\t\t<Explanation/>\n\t\t</Properties>\n\t\t<ChildObjects>\n'
    def common(kind, key, nm, tx, tail):
        return (f'\t\t\t<{kind} uuid="{U(key)}">\n\t\t\t\t<Properties>\n\t\t\t\t\t<Name>{nm}</Name>\n' + syn(nm, 5) + '\t\t\t\t\t<Comment/>\n' +
                type_block(tx, 5) + '\t\t\t\t\t<PasswordMode>false</PasswordMode>\n\t\t\t\t\t<Format/>\n\t\t\t\t\t<EditFormat/>\n\t\t\t\t\t<ToolTip/>\n'
                '\t\t\t\t\t<MarkNegatives>false</MarkNegatives>\n\t\t\t\t\t<Mask/>\n\t\t\t\t\t<MultiLine>false</MultiLine>\n\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>\n'
                '\t\t\t\t\t<MinValue xsi:nil="true"/>\n\t\t\t\t\t<MaxValue xsi:nil="true"/>\n\t\t\t\t\t<FillChecking>DontCheck</FillChecking>\n'
                '\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>\n\t\t\t\t\t<ChoiceParameterLinks/>\n\t\t\t\t\t<ChoiceParameters/>\n'
                '\t\t\t\t\t<QuickChoice>Auto</QuickChoice>\n\t\t\t\t\t<CreateOnInput>Auto</CreateOnInput>\n\t\t\t\t\t<ChoiceForm/>\n\t\t\t\t\t<LinkByType/>\n'
                '\t\t\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n' + tail + f'\t\t\t\t</Properties>\n\t\t\t</{kind}>\n')
    for (nm, tx) in ress:
        o += common('Resource', f'RR/{name}/{nm}', nm, tx, '\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>\n')
    for (nm, tx) in attrs:
        o += common('Attribute', f'RA/{name}/{nm}', nm, tx, '\t\t\t\t\t<Indexing>DontIndex</Indexing>\n\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>\n')
    for (nm, tx) in dims:
        o += common('Dimension', f'RD/{name}/{nm}', nm, tx,
                    '\t\t\t\t\t<DenyIncompleteValues>false</DenyIncompleteValues>\n\t\t\t\t\t<Indexing>Index</Indexing>\n\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>\n\t\t\t\t\t<UseInTotals>true</UseInTotals>\n')
    o += '\t\t</ChildObjects>\n\t</AccumulationRegister>\n</MetaDataObject>'
    return o
write('AccumulationRegisters/ОстаткиМатериалов.xml', accreg_xml('ОстаткиМатериалов', 'Balance',
      [('Материал', NOM), ('Склад', SKL)], [('Количество', t_num(15, 3, False))], ext_pres='Движения по регистру Остатки материалов'))
cfg_add('AccumulationRegister', 'ОстаткиМатериалов')

# ===== Подсистемы и командный интерфейс =====
for sub in ('УчетМатериалов', 'ОказаниеУслуг', 'Бухгалтерия'):
    sub_content_add(sub, 'AccumulationRegister.ОстаткиМатериалов')
    ci_visible(sub, 'AccumulationRegister.ОстаткиМатериалов.StandardCommand.OpenList')
    ci_placement(sub, 'AccumulationRegister.ОстаткиМатериалов.StandardCommand.OpenList', 'NavigationPanelSeeAlso')
sub_content_add('УчетМатериалов', 'DocumentJournal.СкладскиеДокументы')
sub_content_add('ОказаниеУслуг', 'DocumentJournal.СкладскиеДокументы')
for sub in ('ОказаниеУслуг', 'Бухгалтерия'):
    sub_content_add(sub, 'Document.ОказаниеУслуги')
ci_visible('ОказаниеУслуг', 'Document.ОказаниеУслуги.StandardCommand.Create')
print('batch1 ok')
