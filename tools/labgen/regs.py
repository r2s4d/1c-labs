# -*- coding: utf-8 -*-
"""Копия accreg_xml из batch1 для новых регистров накопления (batch1 не трогаем)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

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
