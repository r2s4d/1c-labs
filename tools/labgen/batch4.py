# -*- coding: utf-8 -*-
"""Лаба 6: периодический регистр сведений Цены, функция РозничнаяЦена, подстановка цены в формах документов."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *
import forms

NOM = t_ref('CatalogRef.Номенклатура')

# ===== Регистр сведений Цены =====
def inforeg_xml(name, list_pres, record_pres, dim, resource):
    """Независимый периодический регистр сведений: одно ведущее измерение и один ресурс."""
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<InformationRegister uuid="{U("IR/"+name)}">\n\t\t<InternalInfo>\n'
    for k, c in (('InformationRegisterRecord', 'Record'), ('InformationRegisterManager', 'Manager'), ('InformationRegisterSelection', 'Selection'),
                 ('InformationRegisterList', 'List'), ('InformationRegisterRecordSet', 'RecordSet'), ('InformationRegisterRecordKey', 'RecordKey'),
                 ('InformationRegisterRecordManager', 'RecordManager')):
        o += gtype(k, name, c)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n' + f'\t\t\t<Name>{name}</Name>\n' + syn(human(name), 3)
    o += ('\t\t\t<Comment/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n\t\t\t<EditType>InList</EditType>\n'
          '\t\t\t<DefaultRecordForm/>\n\t\t\t<DefaultListForm/>\n\t\t\t<AuxiliaryRecordForm/>\n\t\t\t<AuxiliaryListForm/>\n'
          '\t\t\t<InformationRegisterPeriodicity>Second</InformationRegisterPeriodicity>\n\t\t\t<WriteMode>Independent</WriteMode>\n'
          '\t\t\t<MainFilterOnPeriod>false</MainFilterOnPeriod>\n\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n'
          '\t\t\t<DataLockControlMode>Managed</DataLockControlMode>\n\t\t\t<FullTextSearch>Use</FullTextSearch>\n'
          '\t\t\t<EnableTotalsSliceFirst>false</EnableTotalsSliceFirst>\n\t\t\t<EnableTotalsSliceLast>false</EnableTotalsSliceLast>\n')
    o += lstr('RecordPresentation', record_pres, 3, 'v8:LocalStringType').replace(' xsi:type="v8:LocalStringType"', '')
    o += '\t\t\t<ExtendedRecordPresentation/>\n'
    o += lstr('ListPresentation', list_pres, 3, 'v8:LocalStringType').replace(' xsi:type="v8:LocalStringType"', '')
    o += ('\t\t\t<ExtendedListPresentation/>\n\t\t\t<Explanation/>\n\t\t\t<DataHistory>DontUse</DataHistory>\n'
          '\t\t\t<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>\n'
          '\t\t\t<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>\n'
          '\t\t</Properties>\n\t\t<ChildObjects>\n')

    def member(kind, key, nm, tx, tail):
        return (f'\t\t\t<{kind} uuid="{U(key)}">\n\t\t\t\t<Properties>\n\t\t\t\t\t<Name>{nm}</Name>\n' + syn(nm, 5) + '\t\t\t\t\t<Comment/>\n' +
                type_block(tx, 5) + '\t\t\t\t\t<PasswordMode>false</PasswordMode>\n\t\t\t\t\t<Format/>\n\t\t\t\t\t<EditFormat/>\n\t\t\t\t\t<ToolTip/>\n'
                '\t\t\t\t\t<MarkNegatives>false</MarkNegatives>\n\t\t\t\t\t<Mask/>\n\t\t\t\t\t<MultiLine>false</MultiLine>\n\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>\n'
                '\t\t\t\t\t<MinValue xsi:nil="true"/>\n\t\t\t\t\t<MaxValue xsi:nil="true"/>\n\t\t\t\t\t<FillChecking>DontCheck</FillChecking>\n'
                '\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>\n\t\t\t\t\t<ChoiceParameterLinks/>\n\t\t\t\t\t<ChoiceParameters/>\n'
                '\t\t\t\t\t<QuickChoice>Auto</QuickChoice>\n\t\t\t\t\t<CreateOnInput>Auto</CreateOnInput>\n\t\t\t\t\t<ChoiceForm/>\n\t\t\t\t\t<LinkByType/>\n'
                '\t\t\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n' + tail + f'\t\t\t\t</Properties>\n\t\t\t</{kind}>\n')
    rn, rt = resource
    o += member('Resource', f'IRR/{name}/{rn}', rn, rt, '\t\t\t\t\t<Indexing>DontIndex</Indexing>\n\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>\n\t\t\t\t\t<DataHistory>Use</DataHistory>\n')
    dn, dt = dim
    o += member('Dimension', f'IRD/{name}/{dn}', dn, dt,
                '\t\t\t\t\t<Indexing>Index</Indexing>\n\t\t\t\t\t<FullTextSearch>Use</FullTextSearch>\n'
                '\t\t\t\t\t<DenyIncompleteValues>true</DenyIncompleteValues>\n\t\t\t\t\t<Master>true</Master>\n\t\t\t\t\t<MainFilter>false</MainFilter>\n'
                '\t\t\t\t\t<DataHistory>Use</DataHistory>\n')
    o += '\t\t</ChildObjects>\n\t</InformationRegister>\n</MetaDataObject>'
    return o

write('InformationRegisters/Цены.xml', inforeg_xml('Цены', 'Цены на номенклатуру', 'Цена', ('Номенклатура', NOM), ('Цена', t_num(15, 2))))
cfg_add('InformationRegister', 'Цены')

for sub in ('УчетМатериалов', 'ОказаниеУслуг', 'Бухгалтерия'):
    sub_content_add(sub, 'InformationRegister.Цены')
    ci_visible(sub, 'InformationRegister.Цены.StandardCommand.OpenList')
    ci_placement(sub, 'InformationRegister.Цены.StandardCommand.OpenList', 'NavigationPanelSeeAlso')

# ===== Общий модуль РаботаСоСправочниками (сервер, вызов сервера) =====
write('CommonModules/РаботаСоСправочниками.xml',
 f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<CommonModule uuid="{U("CM/РаботаСоСправочниками")}">\n\t\t<Properties>\n\t\t\t<Name>РаботаСоСправочниками</Name>\n'
 + syn('Работа со справочниками', 3) +
 '\t\t\t<Comment/>\n\t\t\t<Global>false</Global>\n\t\t\t<ClientManagedApplication>false</ClientManagedApplication>\n\t\t\t<Server>true</Server>\n\t\t\t<ExternalConnection>false</ExternalConnection>\n'
 '\t\t\t<ClientOrdinaryApplication>false</ClientOrdinaryApplication>\n\t\t\t<ServerCall>true</ServerCall>\n\t\t\t<Privileged>false</Privileged>\n\t\t\t<ReturnValuesReuse>DontUse</ReturnValuesReuse>\n\t\t</Properties>\n\t</CommonModule>\n</MetaDataObject>')
write('CommonModules/РаботаСоСправочниками/Ext/Module.bsl',
'''// Возвращает актуальную на указанную дату розничную цену элемента номенклатуры из регистра сведений Цены.
Функция РозничнаяЦена(АктуальнаяДата, ЭлементНоменклатуры) Экспорт
	Отбор = Новый Структура;
	Отбор.Вставить("Номенклатура", ЭлементНоменклатуры);
	ЗначенияРесурсов = РегистрыСведений.Цены.ПолучитьПоследнее(АктуальнаяДата, Отбор);
	Возврат ЗначенияРесурсов.Цена;
КонецФункции
''')
cfg_add('CommonModule', 'РаботаСоСправочниками')

# ===== Подстановка цены при выборе номенклатуры (формы документов) =====
s = forms.S['ОказаниеУслуги']
s['columns'][0][2] = 'ПереченьНоменклатурыНоменклатураПриИзменении'
s['handlers'].append(
'''&НаКлиенте
Процедура ПереченьНоменклатурыНоменклатураПриИзменении(Элемент)
	СтрокаТабличнойЧасти = Элементы.ПереченьНоменклатуры.ТекущиеДанные;
	СтрокаТабличнойЧасти.Цена = РаботаСоСправочниками.РозничнаяЦена(Объект.Дата, СтрокаТабличнойЧасти.Номенклатура);
	РаботаСДокументами.РассчитатьСумму(СтрокаТабличнойЧасти);
КонецПроцедуры
''')
s = forms.S['ПриходнаяНакладная']
s['columns'][0][2] = 'МатериалыМатериалПриИзменении'
s['handlers'].append(
'''&НаКлиенте
Процедура МатериалыМатериалПриИзменении(Элемент)
	СтрокаТабличнойЧасти = Элементы.Материалы.ТекущиеДанные;
	СтрокаТабличнойЧасти.Цена = РаботаСоСправочниками.РозничнаяЦена(Объект.Дата, СтрокаТабличнойЧасти.Материал);
	РаботаСДокументами.РассчитатьСумму(СтрокаТабличнойЧасти);
КонецПроцедуры
''')
print('batch4 ok')
