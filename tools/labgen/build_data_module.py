# -*- coding: utf-8 -*-
import sys, os, re, glob
sys.path.insert(0, os.path.dirname(__file__))
from labgen import *
parts = [open(f, encoding='utf-8').read() for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__), 'bsl', '*.bsl')))]
body = '\n'.join(parts).replace('@@INFOBASE_DIR@@', os.environ.get('INFOBASE_DIR', 'C:\\Users\\nikak\\Projects\\1c-labs-ib\\'))
fills = re.findall(r'Процедура (Заполнить_\w+)\(Лог\)', body)
checks = re.findall(r'Процедура (Проверка_\w+)\(Лог\)', body)
tail = '''
Процедура Вызвать(Имя, Лог)
	Попытка
		Выполнить(Имя + "(Лог);");
	Исключение
		ЗаписатьЛог(Лог, "ОШИБКА в " + Имя + ": " + ОписаниеОшибки());
	КонецПопытки;
КонецПроцедуры

// Возвращает Истина, если был выполнен прогон.
Функция Запустить() Экспорт
	Флаг = Новый Файл(КаталогБазы() + "run.flag");
	Если Не Флаг.Существует() Тогда
		Возврат Ложь;
	КонецЕсли;
	Лог = Новый Массив;
	ЗаписатьЛог(Лог, "Старт: " + Строка(ТекущаяДата()));
'''
for f in fills: tail += f'\tВызвать("{f}", Лог);\n'
for c in checks: tail += f'\tВызвать("{c}", Лог);\n'
tail += '''	Если Новый Файл(КаталогБазы() + "users.flag").Существует() Тогда
		Вызвать("СоздатьПользователейЛабы", Лог);
		УдалитьФайлы(КаталогБазы() + "users.flag");
	КонецЕсли;
	ЗаписатьЛог(Лог, "Конец: " + Строка(ТекущаяДата()));
	Текст = Новый ТекстовыйДокумент;
	Текст.УстановитьТекст(СтрСоединить(Лог, Символы.ПС));
	Текст.Записать(КаталогБазы() + "verify.txt", КодировкаТекста.UTF8);
	УдалитьФайлы(КаталогБазы() + "run.flag");
	Возврат Истина;
КонецФункции
'''
mod = body + tail
write('CommonModules/ЗаполнениеДанных/Ext/Module.bsl', mod)
write('CommonModules/ЗаполнениеДанных.xml',
 f'<?xml version="1.0" encoding="UTF-8"?>\n<MetaDataObject {NSMAP}>\n\t<CommonModule uuid="{U("CM/ЗаполнениеДанных")}">\n\t\t<Properties>\n\t\t\t<Name>ЗаполнениеДанных</Name>\n' + syn('Заполнение данных (временный)', 3) +
 '\t\t\t<Comment/>\n\t\t\t<Global>false</Global>\n\t\t\t<ClientManagedApplication>false</ClientManagedApplication>\n\t\t\t<Server>true</Server>\n\t\t\t<ExternalConnection>false</ExternalConnection>\n'
 '\t\t\t<ClientOrdinaryApplication>false</ClientOrdinaryApplication>\n\t\t\t<ServerCall>true</ServerCall>\n\t\t\t<Privileged>true</Privileged>\n\t\t\t<ReturnValuesReuse>DontUse</ReturnValuesReuse>\n\t\t</Properties>\n\t</CommonModule>\n</MetaDataObject>')
cfg_add('CommonModule', 'ЗаполнениеДанных')
write('Ext/ManagedApplicationModule.bsl', '''Процедура ПриНачалеРаботыСистемы()
	// Временный служебный запуск проверки лабораторных (см. ОбщийМодуль.ЗаполнениеДанных).
	Если ЗаполнениеДанных.Запустить() Тогда
		ЗавершитьРаботуСистемы(Ложь);
	КонецЕсли;
КонецПроцедуры
''')
print('fills', fills, 'checks', checks)
