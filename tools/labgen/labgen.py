# -*- coding: utf-8 -*-
"""Генератор XML-выгрузки конфигурации 1С (формат 2.20, платформа 8.3.27) для лабораторных."""
import os, re, uuid

ROOT = os.environ.get('LABGEN_ROOT') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config'))
NSMAP = ('xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
 'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
 'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
 'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
 'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
 'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
 'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
 'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20"')
FORM_NS = ('xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
 'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" '
 'xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" '
 'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
 'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
 'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
 'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
 'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20"')
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'

def U(key):
    """Детерминированный UUID: повторный запуск генератора даёт те же идентификаторы."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'labgen/' + key))

def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    text = text.replace('\r\n', '\n').replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(b'\xef\xbb\xbf' + text.encode('utf-8'))

def read(rel):
    with open(os.path.join(ROOT, rel), 'rb') as f:
        t = f.read().decode('utf-8-sig')
    return t.replace('\r\n', '\n')

def syn(text, ind):
    t = '\t' * ind
    return (f'{t}<Synonym>\n{t}\t<v8:item>\n{t}\t\t<v8:lang>ru</v8:lang>\n{t}\t\t<v8:content>{text}</v8:content>\n'
            f'{t}\t</v8:item>\n{t}</Synonym>\n')

def human(name):
    """ПриходнаяНакладная -> Приходная накладная"""
    s = re.sub(r'(?<=[а-яa-z])(?=[А-ЯA-Z])', ' ', name)
    return s[0] + s[1:].lower() if s else s

# ---- типы ----
def t_ref(x):   return f'<v8:Type>cfg:{x}</v8:Type>'
def t_str(n):   return f'<v8:Type>xs:string</v8:Type>\n\t\t\t\t\t\t<v8:StringQualifiers>\n\t\t\t\t\t\t\t<v8:Length>{n}</v8:Length>\n\t\t\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>\n\t\t\t\t\t\t</v8:StringQualifiers>'
def t_num(d, f, nonneg=True):
    return (f'<v8:Type>xs:decimal</v8:Type>\n\t\t\t\t\t\t<v8:NumberQualifiers>\n\t\t\t\t\t\t\t<v8:Digits>{d}</v8:Digits>\n'
            f'\t\t\t\t\t\t\t<v8:FractionDigits>{f}</v8:FractionDigits>\n\t\t\t\t\t\t\t<v8:AllowedSign>{"Nonnegative" if nonneg else "Any"}</v8:AllowedSign>\n\t\t\t\t\t\t</v8:NumberQualifiers>')
def t_date():   return '<v8:Type>xs:dateTime</v8:Type>\n\t\t\t\t\t\t<v8:DateQualifiers>\n\t\t\t\t\t\t\t<v8:DateFractions>DateTime</v8:DateFractions>\n\t\t\t\t\t\t</v8:DateQualifiers>'

def type_block(tx, ind):
    t = '\t' * ind
    lines = tx.split('\n')
    # нормализуем отступы вложенных строк
    out = [f'{t}<Type>']
    for ln in lines:
        out.append(f'{t}\t' + ln.strip())
    out.append(f'{t}</Type>')
    # вложенность qualifiers
    res = []
    depth = 0
    for ln in out[1:-1]:
        s = ln.strip()
        if s.startswith('</v8:') and not s.startswith('</v8:Type>'):
            depth -= 1
        res.append(t + '\t' + '\t' * depth + s)
        if re.match(r'<v8:(NumberQualifiers|StringQualifiers|DateQualifiers)>', s):
            depth += 1
    return out[0] + '\n' + '\n'.join(res) + '\n' + out[-1] + '\n'

def attr_xml(kind, key, name, tx, fillcheck='DontCheck', fillvalue=None, ind=3, syn_text=None, extra_tail=''):
    """kind: Attribute (реквизит документа/ТЧ)"""
    t = '\t' * ind
    fv = f'{t}\t<FillFromFillingValue>false</FillFromFillingValue>\n{t}\t<FillValue xsi:type="xr:DesignTimeRef">{fillvalue}</FillValue>\n' if fillvalue else ''
    return (f'{t}<Attribute uuid="{U(key)}">\n{t}\t<Properties>\n{t}\t\t<Name>{name}</Name>\n' + syn(syn_text or human(name) if False else (syn_text or name), ind + 2) +
            f'{t}\t\t<Comment/>\n' + type_block(tx, ind + 2) +
            f'{t}\t\t<PasswordMode>false</PasswordMode>\n{t}\t\t<Format/>\n{t}\t\t<EditFormat/>\n{t}\t\t<ToolTip/>\n'
            f'{t}\t\t<MarkNegatives>false</MarkNegatives>\n{t}\t\t<Mask/>\n{t}\t\t<MultiLine>false</MultiLine>\n'
            f'{t}\t\t<ExtendedEdit>false</ExtendedEdit>\n{t}\t\t<MinValue xsi:nil="true"/>\n{t}\t\t<MaxValue xsi:nil="true"/>\n'
            + (f'{t}\t\t<FillFromFillingValue>false</FillFromFillingValue>\n{t}\t\t<FillValue xsi:type="xr:DesignTimeRef">{fillvalue}</FillValue>\n' if fillvalue else '') +
            f'{t}\t\t<FillChecking>{fillcheck}</FillChecking>\n{t}\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>\n'
            f'{t}\t\t<ChoiceParameterLinks/>\n{t}\t\t<ChoiceParameters/>\n{t}\t\t<QuickChoice>Auto</QuickChoice>\n'
            f'{t}\t\t<CreateOnInput>Auto</CreateOnInput>\n{t}\t\t<ChoiceForm/>\n{t}\t\t<LinkByType/>\n'
            f'{t}\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n{t}\t\t<Indexing>DontIndex</Indexing>\n'
            f'{t}\t\t<FullTextSearch>Use</FullTextSearch>\n{t}\t\t<DataHistory>Use</DataHistory>\n{extra_tail}'
            f'{t}\t</Properties>\n{t}</Attribute>\n')

# ---------- Документ ----------
def gtype(kind, name, cat, ind=3):
    t = '\t' * ind
    return (f'{t}<xr:GeneratedType name="{kind}.{name}" category="{cat}">\n'
            f'{t}\t<xr:TypeId>{U("T/"+kind+name)}</xr:TypeId>\n{t}\t<xr:ValueId>{U("V/"+kind+name)}</xr:ValueId>\n{t}</xr:GeneratedType>\n')

def regrefs(items, ind=3, tag='RegisterRecords'):
    t = '\t' * ind
    if not items:
        return f'{t}<{tag}/>\n'
    return f'{t}<{tag}>\n' + ''.join(f'{t}\t<xr:Item xsi:type="xr:MDObjectRef">{i}</xr:Item>\n' for i in items) + f'{t}</{tag}>\n'

def document_xml(name, list_pres, attrs, tabs, numerator='', registers=(), form=True, obj_pres=None):
    """attrs: [(Имя, тип, проверка, значение_заполнения)], tabs: [(Имя, проверка, [(Имя, тип, проверка)])]"""
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Document uuid="{U("D/"+name)}">\n\t\t<InternalInfo>\n'
    for k, c in (('DocumentObject', 'Object'), ('DocumentRef', 'Ref'), ('DocumentSelection', 'Selection'),
                 ('DocumentList', 'List'), ('DocumentManager', 'Manager')):
        o += gtype(k, name, c)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n'
    o += f'\t\t\t<Name>{name}</Name>\n' + syn(human(name), 3)
    o += '\t\t\t<Comment/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n'
    o += f'\t\t\t<Numerator>{numerator}</Numerator>\n' if numerator else '\t\t\t<Numerator/>\n'
    o += ('\t\t\t<NumberType>String</NumberType>\n\t\t\t<NumberLength>9</NumberLength>\n\t\t\t<NumberAllowedLength>Variable</NumberAllowedLength>\n'
          '\t\t\t<NumberPeriodicity>Nonperiodical</NumberPeriodicity>\n\t\t\t<CheckUnique>true</CheckUnique>\n\t\t\t<Autonumbering>true</Autonumbering>\n'
          '\t\t\t<Characteristics/>\n\t\t\t<BasedOn/>\n\t\t\t<InputByString>\n'
          f'\t\t\t\t<xr:Field>Document.{name}.StandardAttribute.Number</xr:Field>\n\t\t\t</InputByString>\n'
          '\t\t\t<CreateOnInput>Use</CreateOnInput>\n\t\t\t<SearchStringModeOnInputByString>Begin</SearchStringModeOnInputByString>\n'
          '\t\t\t<FullTextSearchOnInputByString>DontUse</FullTextSearchOnInputByString>\n\t\t\t<ChoiceDataGetModeOnInputByString>Directly</ChoiceDataGetModeOnInputByString>\n')
    o += f'\t\t\t<DefaultObjectForm>Document.{name}.Form.ФормаДокумента</DefaultObjectForm>\n' if form else '\t\t\t<DefaultObjectForm/>\n'
    o += ('\t\t\t<DefaultListForm/>\n\t\t\t<DefaultChoiceForm/>\n\t\t\t<AuxiliaryObjectForm/>\n\t\t\t<AuxiliaryListForm/>\n\t\t\t<AuxiliaryChoiceForm/>\n'
          '\t\t\t<Posting>Allow</Posting>\n\t\t\t<RealTimePosting>Allow</RealTimePosting>\n\t\t\t<RegisterRecordsDeletion>AutoDeleteOnUnpost</RegisterRecordsDeletion>\n'
          '\t\t\t<RegisterRecordsWritingOnPost>WriteSelected</RegisterRecordsWritingOnPost>\n\t\t\t<SequenceFilling>AutoFill</SequenceFilling>\n')
    o += regrefs(registers, 3)
    o += ('\t\t\t<PostInPrivilegedMode>true</PostInPrivilegedMode>\n\t\t\t<UnpostInPrivilegedMode>true</UnpostInPrivilegedMode>\n'
          '\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n\t\t\t<DataLockFields/>\n\t\t\t<DataLockControlMode>Managed</DataLockControlMode>\n'
          '\t\t\t<FullTextSearch>Use</FullTextSearch>\n\t\t\t<ObjectPresentation/>\n\t\t\t<ExtendedObjectPresentation/>\n')
    o += '\t\t\t<ListPresentation>\n\t\t\t\t<v8:item>\n\t\t\t\t\t<v8:lang>ru</v8:lang>\n' + f'\t\t\t\t\t<v8:content>{list_pres}</v8:content>\n\t\t\t\t</v8:item>\n\t\t\t</ListPresentation>\n'
    o += ('\t\t\t<ExtendedListPresentation/>\n\t\t\t<Explanation/>\n\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n\t\t\t<DataHistory>DontUse</DataHistory>\n'
          '\t\t\t<UpdateDataHistoryImmediatelyAfterWrite>false</UpdateDataHistoryImmediatelyAfterWrite>\n'
          '\t\t\t<ExecuteAfterWriteDataHistoryVersionProcessing>false</ExecuteAfterWriteDataHistoryVersionProcessing>\n\t\t</Properties>\n\t\t<ChildObjects>\n')
    for (an, at, fc, fv) in attrs:
        o += attr_xml('Attribute', f'DA/{name}/{an}', an, at, fc, fv, ind=3)
    if form:
        o += '\t\t\t<Form>ФормаДокумента</Form>\n'
    for (tn, tfc, tattrs) in tabs:
        o += f'\t\t\t<TabularSection uuid="{U("TS/"+name+"/"+tn)}">\n\t\t\t\t<InternalInfo>\n'
        o += gtype('DocumentTabularSection', f'{name}.{tn}', 'TabularSection', 5) + gtype('DocumentTabularSectionRow', f'{name}.{tn}', 'TabularSectionRow', 5)
        o += '\t\t\t\t</InternalInfo>\n\t\t\t\t<Properties>\n' + f'\t\t\t\t\t<Name>{tn}</Name>\n' + syn(tn, 5)
        o += f'\t\t\t\t\t<Comment/>\n\t\t\t\t\t<ToolTip/>\n\t\t\t\t\t<FillChecking>{tfc}</FillChecking>\n\t\t\t\t\t<LineNumberLength>9</LineNumberLength>\n\t\t\t\t</Properties>\n\t\t\t\t<ChildObjects>\n'
        for (an, at, fc) in tattrs:
            o += attr_xml('Attribute', f'DTA/{name}/{tn}/{an}', an, at, fc, None, ind=5)
        o += '\t\t\t\t</ChildObjects>\n\t\t\t</TabularSection>\n'
    o += '\t\t</ChildObjects>\n\t</Document>\n</MetaDataObject>'
    return o

# ---------- Форма документа ----------
class Ids:
    def __init__(self): self.n = 0
    def __call__(self): self.n += 1; return self.n

def input_field(nm, dp, ids, event=None, ind=2, footer=None):
    t = '\t' * ind
    i, c, e = ids(), ids(), ids()
    ft = ''
    if footer:
        ft = (f'{t}\t<FooterDataPath>{footer[1]}</FooterDataPath>\n' if footer[1] else '') + (f'{t}\t<FooterText>{footer[0]}</FooterText>\n' if footer[0] else '') + f'{t}\t<FooterHorizontalAlign>Right</FooterHorizontalAlign>\n'
    ev = f'{t}\t<Events>\n{t}\t\t<Event name="OnChange">{event}</Event>\n{t}\t</Events>\n' if event else ''
    return (f'{t}<InputField name="{nm}" id="{i}">\n{t}\t<DataPath>{dp}</DataPath>\n{t}\t<EditMode>EnterOnInput</EditMode>\n{ft}'
            f'{t}\t<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>\n{t}\t<ContextMenu name="{nm}КонтекстноеМеню" id="{c}"/>\n'
            f'{t}\t<ExtendedTooltip name="{nm}РасширеннаяПодсказка" id="{e}"/>\n{ev}{t}</InputField>\n')

def label_field(nm, dp, ids, ind=2, hyperlink=False):
    t = '\t' * ind
    i, c, e = ids(), ids(), ids()
    return (f'{t}<LabelField name="{nm}" id="{i}">\n{t}\t<DataPath>{dp}</DataPath>\n{t}\t<EditMode>EnterOnInput</EditMode>\n'
            f'{t}\t<ContextMenu name="{nm}КонтекстноеМеню" id="{c}"/>\n{t}\t<ExtendedTooltip name="{nm}РасширеннаяПодсказка" id="{e}"/>\n{t}</LabelField>\n')

def table_xml(tname, columns, ids, ind=2, footer=False):
    """columns: [(суффикс, datapath_tail, событие|None)]; первая служебная NumberСтроки добавляется автоматически."""
    t = '\t' * ind
    ti, ci, ai, ei = ids(), ids(), ids(), ids()
    o = (f'{t}<Table name="{tname}" id="{ti}">\n{t}\t<Representation>List</Representation>\n' + (f'{t}\t<Footer>true</Footer>\n' if footer else '') + f'{t}\t<AutoInsertNewRow>true</AutoInsertNewRow>\n'
         f'{t}\t<EnableStartDrag>true</EnableStartDrag>\n{t}\t<EnableDrag>true</EnableDrag>\n{t}\t<DataPath>Объект.{tname}</DataPath>\n'
         f'{t}\t<RowFilter xsi:nil="true"/>\n{t}\t<ContextMenu name="{tname}КонтекстноеМеню" id="{ci}"/>\n'
         f'{t}\t<AutoCommandBar name="{tname}КоманднаяПанель" id="{ai}"/>\n{t}\t<ExtendedTooltip name="{tname}РасширеннаяПодсказка" id="{ei}"/>\n')
    for add, typ, nm in (('SearchStringAddition', 'SearchStringRepresentation', 'СтрокаПоиска'),
                         ('ViewStatusAddition', 'ViewStatusRepresentation', 'СостояниеПросмотра'),
                         ('SearchControlAddition', 'SearchControl', 'УправлениеПоиском')):
        a, b, c = ids(), ids(), ids()
        o += (f'{t}\t<{add} name="{tname}{nm}" id="{a}">\n{t}\t\t<AdditionSource>\n{t}\t\t\t<Item>{tname}</Item>\n{t}\t\t\t<Type>{typ}</Type>\n'
              f'{t}\t\t</AdditionSource>\n{t}\t\t<ContextMenu name="{tname}{nm}КонтекстноеМеню" id="{b}"/>\n'
              f'{t}\t\t<ExtendedTooltip name="{tname}{nm}РасширеннаяПодсказка" id="{c}"/>\n{t}\t</{add}>\n')
    o += f'{t}\t<ChildItems>\n'
    o += label_field(f'{tname}НомерСтроки', f'Объект.{tname}.LineNumber', ids, ind + 2)
    for col in columns:
        suf, dp, ev = col[0], col[1], col[2]
        ftr = col[3] if len(col) > 3 else None
        o += input_field(f'{tname}{suf}', f'Объект.{tname}.{dp}', ids, ev, ind + 2, ftr)
    o += f'{t}\t</ChildItems>\n{t}</Table>\n'
    return o

def form_meta_xml(uuid_key, name='ФормаДокумента', synonym='Форма документа'):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Form uuid="{U(uuid_key)}">\n\t\t<Properties>\n'
            f'\t\t\t<Name>{name}</Name>\n' + syn(synonym, 3) +
            '\t\t\t<Comment/>\n\t\t\t<FormType>Managed</FormType>\n\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n\t\t\t<UsePurposes>\n'
            '\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>\n'
            '\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>\n\t\t\t</UsePurposes>\n'
            '\t\t</Properties>\n\t</Form>\n</MetaDataObject>')

def document_form_xml(docname, header, tname, columns, after_table='', extra_attrs='', extra_commands='', nav_items=(), top_extra='', cmdbar_items=(), footer=False):
    """header: [(имя_элемента, datapath)] — поля шапки. nav_items: [(команда, группа)] для панели навигации формы."""
    ids = Ids()
    o = (f'<?xml version="1.0" encoding="UTF-8"?>\n<Form {FORM_NS}>\n\t<AutoTime>CurrentOrLast</AutoTime>\n\t<UsePostingMode>Auto</UsePostingMode>\n'
         '\t<RepostOnWrite>true</RepostOnWrite>\n')
    # командный интерфейс формы (панель навигации)
    if nav_items or cmdbar_items:
        o += '\t<CommandInterface>\n'
        for tag, items in (('NavigationPanel', nav_items), ('CommandBar', cmdbar_items)):
            if not items:
                continue
            o += f'\t\t<{tag}>\n'
            for cmd, grp in items:
                o += (f'\t\t\t<Item>\n\t\t\t\t<Command>{cmd}</Command>\n\t\t\t\t<Type>Auto</Type>\n\t\t\t\t<CommandGroup>{grp}</CommandGroup>\n'
                      '\t\t\t\t<DefaultVisible>false</DefaultVisible>\n\t\t\t\t<Visible>\n\t\t\t\t\t<xr:Common>true</xr:Common>\n\t\t\t\t</Visible>\n\t\t\t</Item>\n')
            o += f'\t\t</{tag}>\n'
        o += '\t</CommandInterface>\n'
    o += '\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>\n\t<ChildItems>\n'
    for nm, dp in header:
        o += input_field(nm, dp, ids, None, 2)
    o += top_extra
    o += table_xml(tname, columns, ids, 2, footer)
    o += after_table
    o += ('\t</ChildItems>\n\t<Attributes>\n\t\t<Attribute name="Объект" id="1">\n\t\t\t<Type>\n'
          f'\t\t\t\t<v8:Type>cfg:DocumentObject.{docname}</v8:Type>\n\t\t\t</Type>\n\t\t\t<MainAttribute>true</MainAttribute>\n'
          '\t\t\t<SavedData>true</SavedData>\n\t\t\t<UseAlways>\n\t\t\t\t<Field>Объект.RegisterRecords</Field>\n\t\t\t</UseAlways>\n\t\t</Attribute>\n'
          f'{extra_attrs}\t</Attributes>\n{extra_commands}</Form>')
    return o

# ---------- Конфигурация ----------
ORDER = ['Language','Subsystem','StyleItem','Style','CommonPicture','SessionParameter','Role','CommonTemplate','FilterCriterion',
         'CommonModule','CommonAttribute','ExchangePlan','XDTOPackage','WebService','HTTPService','WSReference','EventSubscription',
         'ScheduledJob','SettingsStorage','FunctionalOption','FunctionalOptionsParameter','DefinedType','CommonCommand','CommandGroup',
         'Constant','CommonForm','Catalog','Document','DocumentNumerator','Sequence','DocumentJournal','Enum','Report','DataProcessor',
         'InformationRegister','AccumulationRegister','ChartOfCharacteristicTypes','ChartOfAccounts','AccountingRegister',
         'ChartOfCalculationTypes','CalculationRegister','BusinessProcess','Task','ExternalDataSource']

def cfg_add(kind, name):
    t = read('Configuration.xml')
    line = f'\t\t\t<{kind}>{name}</{kind}>\n'
    if line in t:
        return
    m = re.search(r'\t\t<ChildObjects>\n(.*?)\t\t</ChildObjects>', t, re.S)
    body = m.group(1)
    rows = body.split('\n')[:-1]
    idx = ORDER.index(kind)
    pos = len(rows)
    for i, r in enumerate(rows):
        k = re.match(r'\t\t\t<(\w+)>', r).group(1)
        if ORDER.index(k) > idx:
            pos = i
            break
    rows.insert(pos, line.rstrip('\n'))
    nb = '\n'.join(rows) + '\n'
    t = t[:m.start(1)] + nb + t[m.end(1):]
    write('Configuration.xml', t)

def sub_content_add(sub, ref):
    p = f'Subsystems/{sub}.xml'
    t = read(p)
    item = f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">{ref}</xr:Item>\n'
    if item in t:
        return
    t = t.replace('\t\t\t</Content>', item + '\t\t\t</Content>')
    write(p, t)

CI_HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<CommandInterface xmlns="http://v8.1c.ru/8.3/xcf/extrnprops" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\n'

def ci_load(sub):
    p = f'Subsystems/{sub}/Ext/CommandInterface.xml'
    try:
        t = read(p)
    except FileNotFoundError:
        t = CI_HEAD + '</CommandInterface>'
    return p, t

def ci_visible(sub, cmd, visible=True):
    p, t = ci_load(sub)
    block = f'\t\t<Command name="{cmd}">\n\t\t\t<Visibility>\n\t\t\t\t<xr:Common>{"true" if visible else "false"}</xr:Common>\n\t\t\t</Visibility>\n\t\t</Command>\n'
    if f'<Command name="{cmd}">\n\t\t\t<Visibility>' in t:
        return
    if '<CommandsVisibility>' in t:
        t = t.replace('\t</CommandsVisibility>', block + '\t</CommandsVisibility>', 1)
    else:
        t = t.replace('</CommandInterface>', '\t<CommandsVisibility>\n' + block + '\t</CommandsVisibility>\n</CommandInterface>')
    write(p, t)

def ci_placement(sub, cmd, group):
    p, t = ci_load(sub)
    block = f'\t\t<Command name="{cmd}">\n\t\t\t<CommandGroup>{group}</CommandGroup>\n\t\t\t<Placement>Auto</Placement>\n\t\t</Command>\n'
    if f'<Command name="{cmd}">\n\t\t\t<CommandGroup>' in t:
        return
    if '<CommandsPlacement>' in t:
        t = t.replace('\t</CommandsPlacement>', block + '\t</CommandsPlacement>', 1)
    else:
        # CommandsPlacement идёт после CommandsVisibility
        if '</CommandsVisibility>' in t:
            t = t.replace('</CommandsVisibility>\n', '</CommandsVisibility>\n\t<CommandsPlacement>\n' + block + '\t</CommandsPlacement>\n', 1)
        else:
            t = t.replace('</CommandInterface>', '\t<CommandsPlacement>\n' + block + '\t</CommandsPlacement>\n</CommandInterface>')
    write(p, t)

# ---------- Отчёты и СКД ----------
DCS_NS = ('xmlns="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcscom="http://v8.1c.ru/8.1/data-composition-system/common" '
 'xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" '
 'xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
SET_NS = ('xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
 'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
 'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
 'xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def lstr(tag, text, ind, typ='v8:LocalStringType'):
    t = '\t' * ind
    return (f'{t}<{tag} xsi:type="{typ}">\n{t}\t<v8:item>\n{t}\t\t<v8:lang>ru</v8:lang>\n{t}\t\t<v8:content>{text}</v8:content>\n{t}\t</v8:item>\n{t}</{tag}>\n')

def dcs_field(path, title=None, role=None, extra=''):
    o = f'\t\t<field xsi:type="DataSetFieldField">\n\t\t\t<dataPath>{path}</dataPath>\n\t\t\t<field>{path}</field>\n'
    if title:
        o += lstr('title', title, 3)
    o += extra + '\t\t</field>\n'
    return o

def dcs_param(name, title, vtype, value_xml, expr=None, restrict=True, avail=False):
    o = f'\t<parameter>\n\t\t<name>{name}</name>\n'
    if title:
        o += lstr('title', title, 2)
    o += f'\t\t<valueType>\n\t\t\t{vtype}\n\t\t</valueType>\n'
    o += f'\t\t{value_xml}\n'
    o += f'\t\t<useRestriction>{"true" if restrict else "false"}</useRestriction>\n'
    if expr:
        o += f'\t\t<expression>{esc(expr)}</expression>\n'
    if avail is not None:
        o += f'\t\t<availableAsField>{"true" if avail else "false"}</availableAsField>\n'
    o += '\t</parameter>\n'
    return o

DATE_TYPE = '<v8:Type>xs:dateTime</v8:Type>\n\t\t\t<v8:DateQualifiers>\n\t\t\t\t<v8:DateFractions>DateTime</v8:DateFractions>\n\t\t\t</v8:DateQualifiers>'
DATE_ZERO = '<value xsi:type="xs:dateTime">0001-01-01T00:00:00</value>'

def sel_items(names, ind):
    t = '\t' * ind
    return ''.join(f'{t}<dcsset:item xsi:type="dcsset:SelectedItemField">\n{t}\t<dcsset:field>{n}</dcsset:field>\n{t}</dcsset:item>\n' for n in names)

def std_date(variant):
    return f'<dcscor:value xsi:type="v8:StandardBeginningDate">\n\t\t\t\t\t\t<v8:variant xsi:type="v8:StandardBeginningDateVariant">{variant}</v8:variant>\n\t\t\t\t\t</dcscor:value>'

def data_param(name, value_xml, quick_key=None, use=True):
    o = (f'\t\t\t\t<dcscor:item xsi:type="dcsset:SettingsParameterValue">\n\t\t\t\t\t<dcscor:use>{"true" if use else "false"}</dcscor:use>\n'
         f'\t\t\t\t\t<dcscor:parameter>{name}</dcscor:parameter>\n\t\t\t\t\t{value_xml}\n')
    if quick_key:
        o += f'\t\t\t\t\t<dcsset:userSettingID>{U(quick_key)}</dcsset:userSettingID>\n'
    return o + '\t\t\t\t</dcscor:item>\n'

def group_item(field, inner, ind=3, hier=None):
    t = '\t' * ind
    g = ''
    if field:
        g = (f'{t}\t<dcsset:groupItems>\n{t}\t\t<dcsset:item xsi:type="dcsset:GroupItemField">\n{t}\t\t\t<dcsset:field>{field}</dcsset:field>\n'
             f'{t}\t\t\t<dcsset:groupType>{hier or "Items"}</dcsset:groupType>\n{t}\t\t\t<dcsset:periodAdditionType>None</dcsset:periodAdditionType>\n'
             f'{t}\t\t\t<dcsset:periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionBegin>\n'
             f'{t}\t\t\t<dcsset:periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</dcsset:periodAdditionEnd>\n{t}\t\t</dcsset:item>\n{t}\t</dcsset:groupItems>\n')
    return (f'{t}<dcsset:item xsi:type="dcsset:StructureItemGroup">\n{g}{t}\t<dcsset:order>\n{t}\t\t<dcsset:item xsi:type="dcsset:OrderItemAuto"/>\n{t}\t</dcsset:order>\n'
            f'{t}\t<dcsset:selection>\n{t}\t\t<dcsset:item xsi:type="dcsset:SelectedItemAuto"/>\n{t}\t</dcsset:selection>\n{inner}{t}</dcsset:item>\n')

def dcs_schema(fields_xml, query, totals, params_xml, selection_xml, data_params_xml, structure_xml, extra_top='', ds_name='НаборДанных1', variant_title='Основной', extra_settings=''):
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<DataCompositionSchema {DCS_NS}>\n'
    o += '\t<dataSource>\n\t\t<name>ИсточникДанных1</name>\n\t\t<dataSourceType>Local</dataSourceType>\n\t</dataSource>\n'
    o += f'\t<dataSet xsi:type="DataSetQuery">\n\t\t<name>{ds_name}</name>\n{fields_xml}\t\t<dataSource>ИсточникДанных1</dataSource>\n\t\t<query>{esc(query)}</query>\n\t</dataSet>\n'
    o += extra_top
    for (path, expr) in totals:
        o += f'\t<totalField>\n\t\t<dataPath>{path}</dataPath>\n\t\t<expression>{esc(expr)}</expression>\n\t</totalField>\n'
    o += params_xml
    o += (f'\t<settingsVariant>\n\t\t<dcsset:name>Основной</dcsset:name>\n\t\t<dcsset:presentation xsi:type="xs:string">{variant_title}</dcsset:presentation>\n'
          f'\t\t<dcsset:settings {SET_NS}>\n')
    o += '\t\t\t<dcsset:selection>\n' + selection_xml + '\t\t\t</dcsset:selection>\n'
    if data_params_xml:
        o += '\t\t\t<dcsset:dataParameters>\n' + data_params_xml + '\t\t\t</dcsset:dataParameters>\n'
    o += extra_settings + structure_xml
    o += '\t\t</dcsset:settings>\n\t</settingsVariant>\n</DataCompositionSchema>'
    return o

def report_files(name, schema_xml, subsystems=(), synonym=None, extra_children='', main_form=None, object_module=None, extra_props=''):
    """Создаёт отчёт с основной схемой компоновки данных."""
    base = f'Reports/{name}'
    tmpl = 'ОсновнаяСхемаКомпоновкиДанных'
    o = f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Report uuid="{U("RP/"+name)}">\n\t\t<InternalInfo>\n'
    o += gtype('ReportObject', name, 'Object', 3) + gtype('ReportManager', name, 'Manager', 3)
    o += '\t\t</InternalInfo>\n\t\t<Properties>\n' + f'\t\t\t<Name>{name}</Name>\n' + syn(synonym or human(name), 3)
    o += ('\t\t\t<Comment/>\n\t\t\t<UseStandardCommands>true</UseStandardCommands>\n'
          + (f'\t\t\t<DefaultForm>Report.{name}.Form.{main_form}</DefaultForm>\n' if main_form else '\t\t\t<DefaultForm/>\n') +
          '\t\t\t<AuxiliaryForm/>\n'
          f'\t\t\t<MainDataCompositionSchema>Report.{name}.Template.{tmpl}</MainDataCompositionSchema>\n'
          '\t\t\t<DefaultSettingsForm/>\n\t\t\t<AuxiliarySettingsForm/>\n\t\t\t<DefaultVariantForm/>\n\t\t\t<VariantsStorage/>\n\t\t\t<SettingsStorage/>\n'
          '\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>\n\t\t\t<ExtendedPresentation/>\n\t\t\t<Explanation/>\n' + extra_props + '\t\t</Properties>\n\t\t<ChildObjects>\n')
    o += f'\t\t\t<Template>{tmpl}</Template>\n' + extra_children + '\t\t</ChildObjects>\n\t</Report>\n</MetaDataObject>'
    write(f'{base}.xml', o)
    write(f'{base}/Templates/{tmpl}.xml',
          f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Template uuid="{U("RT/"+name)}">\n\t\t<Properties>\n\t\t\t<Name>{tmpl}</Name>\n'
          + syn('Основная схема компоновки данных', 3) + '\t\t\t<Comment/>\n\t\t\t<TemplateType>DataCompositionSchema</TemplateType>\n\t\t</Properties>\n\t</Template>\n</MetaDataObject>')
    write(f'{base}/Templates/{tmpl}/Ext/Template.xml', schema_xml)
    if object_module:
        write(f'{base}/Ext/ObjectModule.bsl', object_module)
    cfg_add('Report', name)
    for s in subsystems:
        sub_content_add(s, f'Report.{name}')

# ---------- Табличный документ (макет) ----------
SHEET_NS = ('xmlns="http://v8.1c.ru/8.2/data/spreadsheet" xmlns:dcscom="http://v8.1c.ru/8.1/data-composition-system/common" '
 'xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" '
 'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
 'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')

def sheet_xml(widths, rows, named):
    """widths: [ширина колонок]; rows: [[(col, 'text'|'param', значение, bold)]]; named: [(имя, строка_от, строка_до)]"""
    fmts = [('font', 0)]           # 1: жирный
    wfmt = {}
    for w in widths:
        if w not in wfmt:
            fmts.append(('width', w)); wfmt[w] = len(fmts)
    o = (f'<?xml version="1.0" encoding="UTF-8"?>\n<document {SHEET_NS}>\n\t<languageSettings>\n\t\t<currentLanguage>ru</currentLanguage>\n'
         '\t\t<defaultLanguage>ru</defaultLanguage>\n\t\t<languageInfo>\n\t\t\t<id>ru</id>\n\t\t\t<code>Русский</code>\n\t\t\t<description>Русский</description>\n'
         '\t\t</languageInfo>\n\t</languageSettings>\n')
    o += f'\t<columns>\n\t\t<size>{len(widths)}</size>\n'
    for i, w in enumerate(widths):
        o += f'\t\t<columnsItem>\n\t\t\t<index>{i}</index>\n\t\t\t<column>\n\t\t\t\t<formatIndex>{wfmt[w]}</formatIndex>\n\t\t\t</column>\n\t\t</columnsItem>\n'
    o += '\t</columns>\n'
    for r, cells in enumerate(rows):
        o += f'\t<rowsItem>\n\t\t<index>{r}</index>\n\t\t<row>\n'
        for (col, kind, val, bold) in cells:
            o += '\t\t\t<c>\n'
            if col is not None and col > 0:
                o += f'\t\t\t\t<i>{col}</i>\n'
            o += '\t\t\t\t<c>\n'
            if bold:
                o += '\t\t\t\t\t<f>1</f>\n'
            if kind == 'param':
                o += f'\t\t\t\t\t<parameter>{val}</parameter>\n'
            else:
                o += ('\t\t\t\t\t<tl>\n\t\t\t\t\t\t<v8:item>\n\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>\n' + f'\t\t\t\t\t\t\t<v8:content>{val}</v8:content>\n'
                      '\t\t\t\t\t\t</v8:item>\n\t\t\t\t\t</tl>\n')
            o += '\t\t\t\t</c>\n\t\t\t</c>\n'
        o += '\t\t</row>\n\t</rowsItem>\n'
    o += f'\t<templateMode>true</templateMode>\n\t<height>{len(rows)}</height>\n\t<vgRows>{len(rows)}</vgRows>\n'
    for (nm, a, b) in named:
        o += (f'\t<namedItem xsi:type="NamedItemCells">\n\t\t<name>{nm}</name>\n\t\t<area>\n\t\t\t<type>Rows</type>\n\t\t\t<beginRow>{a}</beginRow>\n'
              f'\t\t\t<endRow>{b}</endRow>\n\t\t\t<beginColumn>-1</beginColumn>\n\t\t\t<endColumn>-1</endColumn>\n\t\t</area>\n\t</namedItem>\n')
    o += '\t<font faceName="Arial" height="10" bold="true" italic="false" underline="false" strikeout="false" kind="Absolute" scale="100"/>\n'
    for kind, v in fmts:
        if kind == 'font':
            o += '\t<format>\n\t\t<font>0</font>\n\t</format>\n'
        else:
            o += f'\t<format>\n\t\t<width>{v}</width>\n\t</format>\n'
    o += '</document>'
    return o

def add_print_form(doc, sheet, manager_bsl, command_bsl, form_cmd_group='FormCommandBarImportant'):
    """Макет Печать + команда Печать + модуль менеджера у документа doc."""
    base = f'Documents/{doc}'
    write(f'{base}/Templates/Печать.xml',
          f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Template uuid="{U("DT/"+doc+"/Печать")}">\n\t\t<Properties>\n\t\t\t<Name>Печать</Name>\n'
          + syn('Печать', 3) + '\t\t\t<Comment/>\n\t\t\t<TemplateType>SpreadsheetDocument</TemplateType>\n\t\t</Properties>\n\t</Template>\n</MetaDataObject>')
    write(f'{base}/Templates/Печать/Ext/Template.xml', sheet)
    write(f'{base}/Commands/Печать/Ext/CommandModule.bsl', command_bsl)
    write(f'{base}/Ext/ManagerModule.bsl', manager_bsl)
    p = f'{base}.xml'
    t = read(p)
    if '<Template>Печать</Template>' not in t:
        cmd = (f'\t\t\t<Command uuid="{U("DC/"+doc+"/Печать")}">\n\t\t\t\t<Properties>\n\t\t\t\t\t<Name>Печать</Name>\n' + syn('Печать', 5) + '\t\t\t\t\t<Comment/>\n'
               f'\t\t\t\t\t<Group>{form_cmd_group}</Group>\n'
               f'\t\t\t\t\t<CommandParameterType>\n\t\t\t\t\t\t<v8:Type>cfg:DocumentRef.{doc}</v8:Type>\n\t\t\t\t\t</CommandParameterType>\n'
               '\t\t\t\t\t<ParameterUseMode>Single</ParameterUseMode>\n\t\t\t\t\t<ModifiesData>false</ModifiesData>\n\t\t\t\t\t<Representation>Auto</Representation>\n'
               '\t\t\t\t\t<ToolTip/>\n\t\t\t\t\t<Picture/>\n\t\t\t\t\t<Shortcut/>\n\t\t\t\t\t<OnMainServerUnavalableBehavior>Auto</OnMainServerUnavalableBehavior>\n\t\t\t\t</Properties>\n\t\t\t</Command>\n')
        t = t.replace('\t\t</ChildObjects>\n\t</Document>', '\t\t\t<Template>Печать</Template>\n' + cmd + '\t\t</ChildObjects>\n\t</Document>')
        write(p, t)
