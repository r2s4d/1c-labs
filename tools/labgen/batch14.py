# -*- coding: utf-8 -*-
"""Лаба 16: роли (Администратор, Директор, Мастер, Бухгалтер), права, командные интерфейсы подсистем по ролям, справочники в подсистему Предприятие.
Начальная страница (рабочий стол) здесь не генерируется: она требует форм списка, см. STATE.md (делается в Конфигураторе)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *

A, D, M, B = 'Администратор', 'Директор', 'Мастер', 'Бухгалтер'
ROLES = {A: 'Администратор', D: 'Директор', M: 'Мастер', B: 'Бухгалтер'}
CATALOGS = ['Номенклатура', 'Клиенты', 'Сотрудники', 'Склады', 'Районы']

# ---------- состав подсистем: справочники только в Предприятие, журнал и в Бухгалтерию ----------
def sub_content_remove(sub, ref):
    p = f'Subsystems/{sub}.xml'
    t = read(p)
    item = f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">{ref}</xr:Item>\n'
    if item in t:
        write(p, t.replace(item, ''))

def sub_content_add2(sub, ref):
    p = f'Subsystems/{sub}.xml'
    t = read(p)
    item = f'\t\t\t\t<xr:Item xsi:type="xr:MDObjectRef">{ref}</xr:Item>\n'
    if item in t:
        return
    if '\t\t\t<Content/>' in t:
        t = t.replace('\t\t\t<Content/>', '\t\t\t<Content>\n' + item + '\t\t\t</Content>')
    else:
        t = t.replace('\t\t\t</Content>', item + '\t\t\t</Content>')
    write(p, t)

for sub in ('Бухгалтерия', 'УчетМатериалов', 'ОказаниеУслуг', 'РасчетЗарплаты'):
    for c in CATALOGS:
        sub_content_remove(sub, f'Catalog.{c}')
for c in CATALOGS:
    sub_content_add2('Предприятие', f'Catalog.{c}')
sub_content_add2('Бухгалтерия', 'DocumentJournal.СкладскиеДокументы')

# ---------- командные интерфейсы подсистем ----------
CI_ROOT = CI_HEAD
def vis_xml(spec):
    if spec == 'all':
        return '\t\t\t\t<xr:Common>true</xr:Common>\n'
    kind, roles = spec
    if kind == 'only':
        return '\t\t\t\t<xr:Common>false</xr:Common>\n' + ''.join(f'\t\t\t\t<xr:Value name="Role.{r}">true</xr:Value>\n' for r in roles)
    return '\t\t\t\t<xr:Common>true</xr:Common>\n' + ''.join(f'\t\t\t\t<xr:Value name="Role.{r}">false</xr:Value>\n' for r in roles)

def ci_write(sub, items):
    """items: [(команда, группа, видимость, порядок в группе)]; группы: NavigationPanelImportant/Ordinary/SeeAlso, ActionsPanelCreate."""
    o = CI_ROOT + '\t<CommandsVisibility>\n'
    for cmd, grp, spec in items:
        o += f'\t\t<Command name="{cmd}">\n\t\t\t<Visibility>\n' + vis_xml(spec) + '\t\t\t</Visibility>\n\t\t</Command>\n'
    o += '\t</CommandsVisibility>\n\t<CommandsPlacement>\n'
    for cmd, grp, spec in items:
        o += f'\t\t<Command name="{cmd}">\n\t\t\t<CommandGroup>{grp}</CommandGroup>\n\t\t\t<Placement>Auto</Placement>\n\t\t</Command>\n'
    o += '\t</CommandsPlacement>\n\t<CommandsOrder>\n'
    for cmd, grp, spec in items:
        o += f'\t\t<Command name="{cmd}">\n\t\t\t<CommandGroup>{grp}</CommandGroup>\n\t\t</Command>\n'
    o += '\t</CommandsOrder>\n</CommandInterface>'
    write(f'Subsystems/{sub}/Ext/CommandInterface.xml', o)

IMP, ORD, SEE, CRE = 'NavigationPanelImportant', 'NavigationPanelOrdinary', 'NavigationPanelSeeAlso', 'ActionsPanelCreate'
OL = 'StandardCommand.OpenList'; CR = 'StandardCommand.Create'
only = lambda *r: ('only', r)
exc = lambda *r: ('except', r)
REGS = ['AccumulationRegister.ОстаткиМатериалов', 'AccumulationRegister.СтоимостьМатериалов', 'AccumulationRegister.Продажи']

ci_write('УчетМатериалов', [
    ('Document.ПриходнаяНакладная.' + OL, IMP, 'all'),
    ('Document.ПриходнаяНакладная.' + CR, CRE, only(B)),
    ('InformationRegister.Цены.' + CR, CRE, only(B)),
    ('InformationRegister.Цены.' + OL, ORD, 'all'),
    ('DocumentJournal.СкладскиеДокументы.' + OL, ORD, 'all'),
] + [(r + '.' + OL, SEE, only(A, B)) for r in REGS])

ci_write('ОказаниеУслуг', [
    ('Document.ОказаниеУслуги.' + OL, IMP, 'all'),
    ('DocumentJournal.СкладскиеДокументы.' + OL, IMP, 'all'),
    ('Document.ОказаниеУслуги.' + CR, CRE, only(M)),
    ('InformationRegister.Цены.' + CR, CRE, only(B)),
    ('InformationRegister.Цены.' + OL, ORD, 'all'),
] + [(r + '.' + OL, SEE, only(A, B)) for r in REGS])

ci_write('Бухгалтерия', [
    ('Document.ПриходнаяНакладная.' + OL, IMP, 'all'),
    ('Document.ОказаниеУслуги.' + OL, IMP, 'all'),
    ('Document.ПриходнаяНакладная.' + CR, CRE, only(B)),
    ('InformationRegister.Цены.' + CR, CRE, only(B)),
    ('InformationRegister.Цены.' + OL, ORD, 'all'),
    ('DocumentJournal.СкладскиеДокументы.' + OL, ORD, 'all'),
] + [(r + '.' + OL, SEE, only(A, B)) for r in REGS])

# Предприятие: списки справочников всем (Директору только Номенклатура, Сотрудники, Клиенты), создание: Бухгалтеру, Клиентов и Районы ещё Мастеру
pred = []
for c in ('Номенклатура', 'Клиенты', 'Сотрудники', 'Склады', 'Районы'):
    pred.append((f'Catalog.{c}.' + OL, ORD, 'all' if c in ('Номенклатура', 'Клиенты', 'Сотрудники') else exc(D)))
for c in ('Номенклатура', 'Клиенты', 'Сотрудники', 'Склады', 'Районы'):
    pred.append((f'Catalog.{c}.' + CR, CRE, only(B, M) if c in ('Клиенты', 'Районы') else only(B)))
ci_write('Предприятие', pred)

# РасчетЗарплаты: справочник Сотрудники переехал в Предприятие, команды создания тут больше нет
stale = os.path.join(ROOT, 'Subsystems', 'РасчетЗарплаты', 'Ext', 'CommandInterface.xml')
if os.path.exists(stale):
    os.remove(stale)

# ---------- роли и права ----------
RIGHTS = {
 'Catalog': dict(view=['Read', 'View', 'InputByString'],
                 edit=['Read', 'Insert', 'Update', 'View', 'Edit', 'InteractiveInsert', 'InteractiveSetDeletionMark', 'InteractiveClearDeletionMark', 'InputByString']),
 'Document': dict(view=['Read', 'View', 'InputByString'],
                  edit=['Read', 'Insert', 'Update', 'View', 'Edit', 'InteractiveInsert', 'InteractiveSetDeletionMark', 'InteractiveClearDeletionMark',
                        'Posting', 'UndoPosting', 'InteractivePosting', 'InteractivePostingRegular', 'InteractiveUndoPosting', 'InteractiveChangeOfPosted', 'InputByString']),
 'DocumentJournal': dict(view=['Read', 'View'], edit=['Read', 'View']),
# Enum намеренно нет: права на перечисления вешают Конфигуратор при загрузке XML (проверено на платформе)
 'InformationRegister': dict(view=['Read', 'View'], edit=['Read', 'Update', 'View', 'Edit']),
 'AccumulationRegister': dict(view=['Read', 'View'], edit=['Read', 'View']),
 'Report': dict(view=['Use', 'View'], edit=['Use', 'View']),
 'Subsystem': dict(view=['View'], edit=['View']),
}
FULL_EXTRA = {'Catalog': ['Delete'], 'Document': ['Delete'], 'InformationRegister': ['TotalsControl'], 'AccumulationRegister': ['Update', 'Edit', 'TotalsControl']}

def cfg_objects():
    t = read('Configuration.xml')
    objs = []
    for kind in RIGHTS:
        for name in re.findall(rf'\t\t\t<{kind}>([^<]+)</{kind}>', t):
            objs.append((kind, name))
    cfg_name = re.search(r'<Name>([^<]+)</Name>', t).group(1)
    return objs, cfg_name

OBJS, CFG = cfg_objects()
SUBS = [n for k, n in OBJS if k == 'Subsystem']

def level_for(role, kind, name):
    """None | 'view' | 'edit' | 'full'"""
    if role == A:
        return 'full'
    if role == D:
        return 'view'
    if role == B:
        return 'view' if (kind, name) == ('Document', 'ОказаниеУслуги') else 'edit'
    if role == M:
        if kind == 'Subsystem':
            return 'view' if name in ('ОказаниеУслуг', 'Предприятие') else None
        if kind == 'Catalog':
            return 'edit' if name in ('Клиенты', 'Районы') else 'view'
        if kind == 'Document':
            return 'edit' if name == 'ОказаниеУслуги' else 'view'
        return 'view'

def rights_for(kind, lvl):
    r = RIGHTS[kind]
    if lvl == 'full':
        out = list(r['edit'])
        for x in FULL_EXTRA.get(kind, []):
            if x not in out:
                out.append(x)
        return out
    return r[lvl]

CLIENT_RIGHTS = {
    A: ['Administration', 'DataAdministration', 'UpdateDataBaseConfiguration', 'ExclusiveMode', 'ActiveUsers', 'EventLog', 'ThinClient', 'WebClient', 'ThickClient', 'ExternalConnection', 'Automation', 'Output', 'SaveUserData', 'MainWindowModeNormal', 'MainWindowModeWorkplace', 'MainWindowModeEmbeddedWorkplace', 'MainWindowModeFullscreenWorkplace', 'MainWindowModeKiosk'],
}
for r in (D, M, B):
    CLIENT_RIGHTS[r] = ['ThinClient', 'WebClient', 'Output', 'SaveUserData', 'MainWindowModeNormal', 'MainWindowModeWorkplace']

def right_xml(name, value=True):
    return f'\t\t<right>\n\t\t\t<name>{name}</name>\n\t\t\t<value>{"true" if value else "false"}</value>\n\t\t</right>\n'

for role in (A, D, M, B):
    o = ('<?xml version="1.0" encoding="UTF-8"?>\n<Rights xmlns="http://v8.1c.ru/8.2/roles" xmlns:xs="http://www.w3.org/2001/XMLSchema" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="Rights" version="2.20">\n'
         f'\t<setForNewObjects>{"true" if role == A else "false"}</setForNewObjects>\n\t<setForAttributesByDefault>true</setForAttributesByDefault>\n'
         '\t<independentRightsOfChildObjects>false</independentRightsOfChildObjects>\n')
    o += f'\t<object>\n\t\t<name>Configuration.{CFG}</name>\n' + ''.join(right_xml(n) for n in CLIENT_RIGHTS[role]) + '\t</object>\n'
    for kind, name in OBJS:
        lvl = level_for(role, kind, name)
        if not lvl:
            continue
        o += f'\t<object>\n\t\t<name>{kind}.{name}</name>\n' + ''.join(right_xml(n) for n in rights_for(kind, lvl)) + (right_xml('InteractiveDelete', False) if lvl == 'full' and kind in ('Catalog', 'Document') else '') + '\t</object>\n'
    o += '</Rights>'
    write(f'Roles/{role}/Ext/Rights.xml', o)
    write(f'Roles/{role}.xml',
          f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<Role uuid="{U("ROLE/"+role)}">\n\t\t<Properties>\n\t\t\t<Name>{role}</Name>\n'
          + syn(role, 3) + '\t\t\t<Comment/>\n\t\t</Properties>\n\t</Role>\n</MetaDataObject>')
    cfg_add('Role', role)
print('batch14 ok')
