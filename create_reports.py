import openpyxl
import os
from openpyxl.styles import Font, Alignment, numbers
from openpyxl.styles.borders import Border, Side


def create_reports_sday(sl_object_all: dict, node_param_rus: str, sl_param: dict):
    # sl_object_all =
    # { (Объект, рус имя объекта, индекс объекта): {контроллер: (ip основной, ip резервный, индекс объекта)} }
    # sl_param = {cpu: {Перфискспапки.alg_par: русское имя}}
    num_cel = 8
    num_par = 1

    thin_border = Border(left=Side(style='thin'),  # thick - толстые границы, thin - тонкие
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    tuple_sh = ('W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH')
    str_sh = 'IJKLMNOPQRST'

    # Для каждого объекта
    for obj in sl_object_all:
        # Создаём эксельку
        wb = openpyxl.Workbook()
        # Выбираем активный лист
        sheet = wb.active
        sheet.title = 'Лист 1'
        # Заполняем стартовую информацию
        for col, w in {'F': 7, 'G': 105, 'H': 15}.items():
            sheet.column_dimensions[col].width = w
        sheet['E2'] = f'="{obj[0]}."'
        for cell, value in {'A2': '=NOW()', 'B2': '="№ ГПА"', 'A3': '=reportdate', 'A4': '=smena', 'A5': '="smena=1"',
                            'A6': '="smena=2"', 'B3': '="дата"', 'B4': '="смена"', 'B5': '="дневная"',
                            'B6': '="ночная"', 'C7': '="узел"', 'D7': '="ед.изм"', 'E7': '="значение"',
                            'D3': '="начало пути"', 'E3': '="Получение данных с OPC UA@"',
                            'D4': '="значение"', 'E4': '=".Value;1"', 'E5': '=".Value.100;1"',
                            'A9': '=YEAR(A3)', 'B9': '="год"', 'A10': '=MONTH(A3)', 'B10': '="месяц"',
                            'A11': '=DAY(A3)', 'B11': '="день"', 'A12': '=DATE(A9, A10, A11)',
                            'A14': '=IF(A4=1, TIME(8, 0, 0), TIME(20, 0, 0))', 'A15': '=TIME(0, 3, 0)',
                            'B14': '="выбор смены"', 'B15': '="диапазон"'}.items():
            sheet[cell] = value
        # Заполняем временные формулы
        for cell, value in {'I5': '=A12+A14', 'I6': '=I5+$A$15'}.items():
            sheet[cell] = value
        cell_ind_str = 'JKLMNOPQRST'
        formul_ind_str = 'IJKLMNOPQRS'
        for i in range(len(cell_ind_str)):
            sheet[f'{cell_ind_str[i]}5'] = f'={formul_ind_str[i]}5+1/24'
            sheet[f'{cell_ind_str[i]}6'] = f'={cell_ind_str[i]}5+$A$15'
        for coll in 'IJKLMNOPQRST':
            sheet[f'{coll}4'] = f'=IF($A$2>{coll}5, true, false)'
        # Выставляем форматы
        for cell, value in {'A2': 22, 'A3': 22, 'A12': 22, 'A14': 21, 'A15': 21}.items():
            sheet[cell].number_format = numbers.BUILTIN_FORMATS[value]
        for coll in 'IJKLMNOPQRST':
            sheet[f'{coll}5'].number_format = numbers.BUILTIN_FORMATS[22]
            sheet[f'{coll}6'].number_format = numbers.BUILTIN_FORMATS[22]
        # Заполняем шапку формул данных
        sheet['V5'] = '="текущие значения"'
        for i in range(len(tuple_sh)):
            sheet[f'{tuple_sh[i]}5'] = f'={str_sh[i]}7'
            sheet[f'{tuple_sh[i]}5'].number_format = numbers.BUILTIN_FORMATS[22]
        # Создаём заголовок
        sheet.row_dimensions[2].height = 20
        sheet.row_dimensions[1].height = 25
        sheet[f'G2'] = f'="Сменная ведомость {obj[1]} на "'
        sheet[f'G2'].font = Font(size=16, name='Arial', bold=True)
        sheet[f'G2'].alignment = Alignment(horizontal="right", vertical="top")
        sheet[f'H2'] = f'=A3'
        sheet[f'H2'].font = Font(size=16, name='Arial', bold=True)
        sheet[f'H2'].alignment = Alignment(horizontal="center", vertical="top")
        sheet[f'H2'].number_format = numbers.BUILTIN_FORMATS[15]

        for cell, i in {'F7': '="№"', 'G7': '="Наименование  "',
                        'H7': '="ед.изм"'}.items():
            sheet[cell] = i
            sheet[cell].font = Font(size=14, name='Arial', bold=True)
            sheet[cell].alignment = Alignment(horizontal="center", vertical="center")
            sheet[cell].border = thin_border
        # Проставляем время каждый час в первой шапке
        for coll in str_sh:
            sheet[f'{coll}7'] = f'=TIME(HOUR({coll}5), 0, 0)'
            sheet[f'{coll}7'].font = Font(size=14, name='Arial', bold=True)
            sheet[f'{coll}7'].alignment = Alignment(horizontal="center", vertical="center")
            sheet[f'{coll}7'].border = thin_border
            sheet[f'{coll}7'].number_format = numbers.BUILTIN_FORMATS[20]
            sheet.column_dimensions[coll].width = 10

        # Для каждого контроллера...
        for cpu, sl_par in sl_param.items():
            # ...при условии, что объект содержит текущий контроллер...
            if cpu in sl_object_all[obj]:
                # ...для каждого параметра...
                for par, property_par in sl_par.items():
                    # Если отсчитали 17 параметров, то добавляем шапку для следующего листа
                    if not (num_par - 1) % 26 and num_par != 1:
                        num_cel += 2
                        for _ in range(3):
                            sheet.row_dimensions[num_cel].height = 35
                            for cell, i in {'G': '="должность"', 'J': '="ФИО"', 'M': '="подпись"'}.items():
                                sheet[f'{cell}{num_cel}'] = i
                                sheet[f'{cell}{num_cel}'].font = Font(size=12, name='Arial')
                                sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                            for coll in 'GHIJKLMN':
                                sheet[f'{coll}{num_cel}'].border = Border(top=Side(style='thin'))
                            num_cel += 1

                        num_cel += 1
                        sheet.row_dimensions[num_cel].height = 25
                        sheet[f'G{num_cel}'] = f'="Сменная ведомость {obj[1]} на "'
                        sheet[f'G{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'G{num_cel}'].alignment = Alignment(horizontal="right", vertical="top")
                        sheet[f'H{num_cel}'] = f'=H2'
                        sheet[f'H{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'H{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                        sheet[f'H{num_cel}'].number_format = numbers.BUILTIN_FORMATS[15]
                        num_cel += 2
                        sheet.row_dimensions[num_cel].height = 20
                        for cell, i in {'F': '="№"', 'G': '="Наименование  "',
                                        'H': '="ед.изм"'}.items():
                            sheet[f'{cell}{num_cel}'] = i
                            sheet[f'{cell}{num_cel}'].font = Font(size=14, name='Arial', bold=True)
                            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                            sheet[f'{cell}{num_cel}'].border = thin_border
                        for coll in 'IJKLMNOPQRST':
                            sheet[f'{coll}{num_cel}'] = f'={coll}7'
                            sheet[f'{coll}{num_cel}'].font = Font(size=14, name='Arial', bold=True)
                            sheet[f'{coll}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                            sheet[f'{coll}{num_cel}'].border = thin_border
                            sheet[f'{coll}{num_cel}'].number_format = numbers.BUILTIN_FORMATS[20]
                        num_cel += 1
                    # Заполняем параметры
                    sheet[f'C{num_cel}'] = f'="{par}"'
                    sheet[f'F{num_cel}'] = f'="{num_par}"'
                    rus_name = property_par.replace("\"", "\"\"")
                    sheet[f'G{num_cel}'] = f'="{rus_name}  "'  # Русское наименование

                    # Заполняем формулы для вывода данных
                    sheet[f'V{num_cel}'] = f'=CurrAttrValue(E{num_cel}, 0)'
                    for i in range(len(tuple_sh)):
                        sheet[f'{tuple_sh[i]}{num_cel}'] = f'=ArchiveAttributeValue($E{num_cel}, ' \
                                                           f'0, {str_sh[i]}$5, {str_sh[i]}$6, 1)'
                    for i in range(len(str_sh)):
                        sheet[f'{str_sh[i]}{num_cel}'] = f'=IF({str_sh[i]}$4, IF(ISNUMBER({tuple_sh[i]}{num_cel}), ' \
                                                         f'{tuple_sh[i]}{num_cel}, $V{num_cel}), "-")'
                        sheet[f'{str_sh[i]}{num_cel}'].number_format = numbers.BUILTIN_FORMATS[2]
                        sheet[f'{str_sh[i]}{num_cel}'].font = Font(size=14, name='Arial')
                        sheet[f'{str_sh[i]}{num_cel}'].border = thin_border
                    # Заполняем ссылки
                    for i, value in {'D': f'=CONCATENATE($E$3, $E$2, $C{num_cel}, $E$5)',
                                     'E': f'=CONCATENATE($E$3, $E$2, $C{num_cel}, $E$4)'}.items():
                        sheet[f'{i}{num_cel}'] = value
                    # Заполняем формулы
                    for i, value in {'H': f'=CurrAttrValue(D{num_cel}, 0)'}.items():
                        sheet[f'{i}{num_cel}'] = value

                    # Устанавливаем для ячеек размер шрифта 14, Arial и выставляем границу
                    for i in 'FGH':
                        sheet[f'{i}{num_cel}'].font = Font(size=14, name='Arial')
                        sheet[f'{i}{num_cel}'].border = thin_border
                    # Выводим в центр нумерацию, значения и единицы измерения
                    for i, vert_alig in {'F': 'center', 'G': 'left', 'H': 'center', 'S': 'center'}.items():
                        sheet[f'{i}{num_cel}'].alignment = Alignment(horizontal=vert_alig, vertical="center",
                                                                     wrap_text=True)
                    sheet.row_dimensions[num_cel].height = 20
                    num_cel += 1
                    num_par += 1
        # Прячем столбцы с привязками
        for col in ('A', 'B', 'C', 'D', 'E'):
            sheet.column_dimensions[col].hidden = True
        for row in (4, 5, 6):
            sheet.row_dimensions[row].hidden = True
        for col in ('V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK',
                    'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX'):
            sheet.column_dimensions[col].hidden = True
        # Добавляем подпись в конце
        num_cel += 2
        for _ in range(3):
            sheet.row_dimensions[num_cel].height = 35
            for cell, i in {'G': '="должность"', 'J': '="ФИО"', 'M': '="подпись"'}.items():
                sheet[f'{cell}{num_cel}'] = i
                sheet[f'{cell}{num_cel}'].font = Font(size=12, name='Arial')
                sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
            for coll in 'GHIJKLMN':
                sheet[f'{coll}{num_cel}'].border = Border(top=Side(style='thin'))
            num_cel += 1

        wb.save(os.path.join('File_for_Import', 'Reports', f'{node_param_rus} {obj[1]}.xlsx'))
    return


def create_reports_pz(sl_object_all: dict, node_param_rus: str, node_alg_name: str, sl_param: dict):
    # sl_object_all =
    # { (Объект, рус имя объекта, индекс объекта): {контроллер: (ip основной, ip резервный, индекс объекта)} }
    # sl_param = {cpu: {алг_имя(A000): (тип защиты в студии, рус.имя, ед измерения)}}
    num_cel = 4
    num_par = 1

    thin_border = Border(left=Side(style='thin'),  # thick - толстые границы, thin - тонкие
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    # Для каждого объекта
    for obj in sl_object_all:
        # Создаём эксельку
        wb = openpyxl.Workbook()
        # Выбираем активный лист
        sheet = wb.active
        sheet.title = 'Лист 1'
        # Заполняем стартовую информацию
        for col, w in {'P': 7, 'Q': 105}.items():
            sheet.column_dimensions[col].width = w
        sheet['A1'] = f'="{obj[0]}."'
        for cell, value in {'A2': '="Получение данных с OPC UA@"', 'B2': '=".TRDELAY;1"', 'C2': '=".TDELAY;1"',
                            'D2': '=".SETPOINT;1"', 'E2': '=".VALUE;1"', 'F2': '=".VALUE.5501;1"',
                            'G2': '=".VALUE.100;1"', 'H2': '=".BLOCKED;1"', 'I2': '=".CHECK;1"',
                            'J2': '=".CHECKVALUE;1"'}.items():
            sheet[cell] = value
        for cell, value in {'B3': '="Таймер"', 'C3': '="Задержка"', 'D3': '="Уставка"', 'E3': '="Значение"',
                            'F3': '="Название"', 'G3': '="ед.измерения"'}.items():
            sheet[cell] = value
        # Создаём заголовок
        sheet.row_dimensions[3].height = 20
        sheet.row_dimensions[1].height = 25
        sheet['Q1'] = f'="Протокол проверки защит {obj[1]} на  "'
        sheet['Q1'].font = Font(size=16, name='Arial', bold=True)
        sheet['Q1'].alignment = Alignment(horizontal="right", vertical="top")
        sheet['R1'] = f'=NOW()'
        sheet['R1'].font = Font(size=16, name='Arial', bold=True)
        sheet['R1'].alignment = Alignment(horizontal="center", vertical="top")
        sheet['R1'].number_format = numbers.BUILTIN_FORMATS[15]
        sheet['S1'] = f'=NOW()'
        sheet['S1'].font = Font(size=16, name='Arial', bold=True)
        sheet['S1'].alignment = Alignment(horizontal="left", vertical="top")
        sheet['S1'].number_format = numbers.BUILTIN_FORMATS[20]
        for cell, i in {'P3': '="№"', 'Q3': '="Наименование защиты  "',
                        'R3': '="Таймер"', 'S3': '="Задержка"', 'T3': '="Уставка"', 'U3': '="Значение"',
                        'V3': '="Eд.изм"', 'W3': '="Отметка о проверке"'}.items():
            sheet[cell] = i
            sheet[cell].font = Font(size=14, name='Arial', bold=True)
            sheet[cell].alignment = Alignment(horizontal="center", vertical="center")
            sheet[cell].border = thin_border

        # Для каждого контроллера...
        for cpu, sl_par in sl_param.items():
            # ...при условии, что объект содержит текущий контроллер...
            if cpu in sl_object_all[obj]:
                # ...для каждого параметра...
                for par, property_par in sl_par.items():
                    # Если отсчитали 17 параметров, то добавляем шапку для следующего листа
                    if not (num_par - 1) % 26 and num_par != 1:
                        num_cel += 2
                        for _ in range(3):
                            sheet.row_dimensions[num_cel].height = 35
                            for cell, i in {'Q': '="должность"', 'S': '="ФИО"', 'U': '="подпись"'}.items():
                                sheet[f'{cell}{num_cel}'] = i
                                sheet[f'{cell}{num_cel}'].font = Font(size=12, name='Arial')
                                sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                            for coll in 'QRSTU':
                                sheet[f'{coll}{num_cel}'].border = Border(top=Side(style='thin'))
                            num_cel += 1

                        num_cel += 1
                        sheet.row_dimensions[num_cel].height = 25
                        sheet[f'Q{num_cel}'] = f'="Протокол проверки защит {obj[1]} на "'
                        sheet[f'Q{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'Q{num_cel}'].alignment = Alignment(horizontal="right", vertical="top")
                        sheet[f'R{num_cel}'] = f'=R1'
                        sheet[f'R{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'R{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                        sheet[f'R{num_cel}'].number_format = numbers.BUILTIN_FORMATS[15]
                        sheet[f'S{num_cel}'] = f'=S1'
                        sheet[f'S{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'S{num_cel}'].alignment = Alignment(horizontal="left", vertical="top")
                        sheet[f'S{num_cel}'].number_format = numbers.BUILTIN_FORMATS[20]
                        num_cel += 2
                        sheet.row_dimensions[num_cel].height = 20
                        for cell, i in {'P': '="№"', 'Q': '="Наименование защиты  "',
                                        'R': '="Таймер"', 'S': '="Задержка"', 'T': '="Уставка"', 'U': '="Значение"',
                                        'V': '="Eд.изм"', 'W': '="Отметка о проверке"'}.items():
                            sheet[f'{cell}{num_cel}'] = i
                            sheet[f'{cell}{num_cel}'].font = Font(size=14, name='Arial', bold=True)
                            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                            sheet[f'{cell}{num_cel}'].border = thin_border
                        num_cel += 1
                    # Заполняем параметры
                    sheet[f'A{num_cel}'] = f'="{node_alg_name}.{par}"'
                    sheet[f'P{num_cel}'] = f'="{num_par}"'
                    rus_name = property_par[1].replace("\"", "\"\"")
                    sheet[f'Q{num_cel}'] = f'="{rus_name}  "'  # Русское наименование
                    # Заполняем ссылки
                    for i, value in {'B': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, B$2)',
                                     'C': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, C$2)',
                                     'D': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, D$2)',
                                     'E': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, E$2)',
                                     'F': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, F$2)',
                                     'G': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, G$2)',
                                     'H': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, H$2)',
                                     'I': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, I$2)',
                                     'J': f'=CONCATENATE($A$2, $A$1, $A{num_cel}, J$2)'}.items():
                        sheet[f'{i}{num_cel}'] = value
                    # Заполняем формулы
                    for i, value in {'K': f'=CurrAttrValue(D{num_cel}, 0)', 'L': f'=CurrAttrValue(E{num_cel}, 0)',
                                     'M': f'=CurrAttrValue(H{num_cel}, 0)', 'N': f'=CurrAttrValue(I{num_cel}, 0)',
                                     'O': f'=CurrAttrValue(J{num_cel}, 0)'}.items():
                        sheet[f'{i}{num_cel}'] = value
                    # Заполняем инфу по параметрам
                    for i, value in {'R': (f'=IF(N{num_cel}, S{num_cel}, "")', 15),
                                     'S': (f'=CurrAttrValue(C{num_cel}, 0)', 15),
                                     'T': (f'=IF(K{num_cel}=-200, "д.вх.", K{num_cel})', 13),
                                     'U': (f'=IF(L{num_cel}=-200, "д.вх.", IF(N{num_cel}, O{num_cel}, L{num_cel}))',
                                           15),
                                     'V': (f'=CurrAttrValue(G{num_cel}, 0)', 12),
                                     'W': (f'=IF(M{num_cel}, "Блокирована", IF(N{num_cel}, "Проверено", "-"))',
                                           30)}.items():
                        sheet[f'{i}{num_cel}'] = value[0]
                        sheet.column_dimensions[i].width = value[1]
                    # Выставляем формат
                    for i in 'RS':
                        sheet[f'{i}{num_cel}'].number_format = numbers.BUILTIN_FORMATS[2]
                    # Устанавливаем для ячеек размер шрифта 14, Arial и выставляем границу
                    for i in ('P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W'):
                        sheet[f'{i}{num_cel}'].font = Font(size=14, name='Arial')
                        sheet[f'{i}{num_cel}'].border = thin_border
                    # Выводим в центр нумерацию, значения и единицы измерения
                    for i, vert_alig in {'P': 'center', 'Q': 'left', 'R': 'center', 'S': 'center',
                                         'T': 'center', 'U': 'center', 'V': 'center', 'W': 'center'}.items():
                        sheet[f'{i}{num_cel}'].alignment = Alignment(horizontal=vert_alig, vertical="center",
                                                                     wrap_text=True)
                    sheet.row_dimensions[num_cel].height = 20
                    num_cel += 1
                    num_par += 1
        # Прячем столбцы с привязками
        for col in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'):
            sheet.column_dimensions[col].hidden = True
        # Добавляем подпись в конце
        num_cel += 2
        for _ in range(3):
            sheet.row_dimensions[num_cel].height = 35
            for cell, i in {'Q': '="должность"', 'S': '="ФИО"', 'U': '="подпись"'}.items():
                sheet[f'{cell}{num_cel}'] = i
                sheet[f'{cell}{num_cel}'].font = Font(size=12, name='Arial')
                sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
            for coll in 'QRSTU':
                sheet[f'{coll}{num_cel}'].border = Border(top=Side(style='thin'))
            num_cel += 1

        wb.save(os.path.join('File_for_Import', 'Reports', f'{node_param_rus} {obj[1]}.xlsx'))
    return


def create_reports(sl_object_all: dict, node_param_rus: str, node_alg_name: str, sl_param: dict):
    sl_r = {'AI': 'значений измеряемых параметров', 'AE': 'значений расчётных параметров',
            'System.CNT': 'накопленных значений по наработке'}
    # sl_object_all =
    # { (Объект, рус имя объекта, индекс объекта): {контроллер: (ip основной, ip резервный, индекс объекта)} }

    # sl_param = {cpu: {алг_пар: (тип параметра в студии, русское имя, ед измер, короткое имя, количество знаков)}}
    num_cel = 4
    num_par = 1

    thin_border = Border(left=Side(style='thin'),  # thick - толстые границы, thin - тонкие
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))

    # Для каждого объекта
    for obj in sl_object_all:
        # Создаём эксельку
        wb = openpyxl.Workbook()
        # Выбираем активный лист
        sheet = wb.active
        sheet.title = 'Лист 1'
        # Заполняем стартовую информацию
        sheet.column_dimensions['D'].width = 7
        sheet.column_dimensions['E'].width = 105
        sheet.column_dimensions['F'].width = 20
        sheet.column_dimensions['G'].width = 15
        sheet['A1'] = f'="{obj[0]}."'
        sheet['B1'] = '=".Value;1"'
        sheet['A2'] = '="Получение данных с OPC UA@"'
        sheet['B2'] = '=".Value.100;1"'
        # Создаём заголовок
        sheet.row_dimensions[3].height = 20
        sheet.row_dimensions[1].height = 40
        sheet['E1'] = f'="Срез {sl_r.get(node_alg_name)} {obj[1]} на "'
        sheet['E1'].font = Font(size=16, name='Arial',  bold=True)
        sheet['E1'].alignment = Alignment(horizontal="right", vertical="top")
        sheet['F1'] = f'=NOW()'
        sheet['F1'].font = Font(size=16, name='Arial', bold=True)
        sheet['F1'].alignment = Alignment(horizontal="center", vertical="top")
        sheet['F1'].number_format = numbers.BUILTIN_FORMATS[15]
        sheet['G1'] = f'=NOW()'
        sheet['G1'].font = Font(size=16, name='Arial', bold=True)
        sheet['G1'].alignment = Alignment(horizontal="left", vertical="top")
        sheet['G1'].number_format = numbers.BUILTIN_FORMATS[20]
        for cell, i in {'D3': '="№"', 'E3': '="Наименование параметра  "',
                        'F3': '="Значение"', 'G3': '="Ед. изм."'}.items():
            sheet[cell] = i
            sheet[cell].font = Font(size=14, name='Arial',  bold=True)
            sheet[cell].alignment = Alignment(horizontal="center", vertical="center")
            sheet[cell].border = thin_border

        # Для каждого контроллера...
        for cpu, sl_par in sl_param.items():
            # ...при условии, что объект содержит текущий контроллер...
            if cpu in sl_object_all[obj]:
                # ...для каждого параметра...
                for par, property_par in sl_par.items():
                    # Если отсчитали 17 параметров, то добавляем шапку для следующего листа
                    if not (num_par-1) % 18 and num_par != 1:
                        num_cel += 2
                        sheet.row_dimensions[num_cel].height = 35
                        for cell, i in {'E': '="должность"', 'F': '="ФИО"', 'G': '="подпись"'}.items():
                            sheet[f'{cell}{num_cel}'] = i
                            sheet[f'{cell}{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                            sheet[f'{cell}{num_cel}'].border = Border(top=Side(style='thin'))

                        num_cel += 1
                        sheet.row_dimensions[num_cel].height = 40
                        sheet[f'E{num_cel}'] = f'="Срез {sl_r.get(node_alg_name)} {obj[1]} на "'
                        sheet[f'E{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'E{num_cel}'].alignment = Alignment(horizontal="right", vertical="top")
                        sheet[f'F{num_cel}'] = f'=F1'
                        sheet[f'F{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'F{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
                        sheet[f'F{num_cel}'].number_format = numbers.BUILTIN_FORMATS[15]
                        sheet[f'G{num_cel}'] = f'=G1'
                        sheet[f'G{num_cel}'].font = Font(size=16, name='Arial', bold=True)
                        sheet[f'G{num_cel}'].alignment = Alignment(horizontal="left", vertical="top")
                        sheet[f'G{num_cel}'].number_format = numbers.BUILTIN_FORMATS[20]
                        num_cel += 2
                        sheet.row_dimensions[num_cel].height = 20
                        for cell, i in {'D': '="№"', 'E': '="Наименование параметра  "',
                                        'F': '="Значение"', 'G': '="Ед. изм"'}.items():
                            sheet[f'{cell}{num_cel}'] = i
                            sheet[f'{cell}{num_cel}'].font = Font(size=14, name='Arial', bold=True)
                            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                            sheet[f'{cell}{num_cel}'].border = thin_border
                        num_cel += 1

                    sheet[f'C{num_cel}'] = f'="{node_alg_name}.{par}"'
                    sheet[f'D{num_cel}'] = f'="{num_par}"'
                    rus_name = property_par[1].replace("\"", "\"\"")
                    sheet[f'E{num_cel}'] = f'="{rus_name}  "'  # Русское наименование
                    sheet[f'A{num_cel}'] = f'=CONCATENATE($A$2, $A$1, C{num_cel}, $B$2)'
                    sheet[f'B{num_cel}'] = f'=CONCATENATE($A$2, $A$1, C{num_cel}, $B$1)'
                    sheet[f'F{num_cel}'] = f'=CurrAttrValue(B{num_cel}, 0)'
                    e_unit = (('="-"' if 'Swap' in par else '="час"') if node_alg_name == 'System.CNT'
                              else f'=CurrAttrValue(A{num_cel}, 0)')
                    sheet[f'G{num_cel}'] = e_unit
                    # Устанавливаем для ячеек размер шрифта 14, Arial и выставляем границу
                    for i in ('C', 'D', 'E', 'A', 'B', 'F', 'G'):
                        sheet[f'{i}{num_cel}'].font = Font(size=14, name='Arial')
                        sheet[f'{i}{num_cel}'].border = thin_border
                    # Выводим в центр нумерацию, значения и единицы измерения
                    for i, vert_alig in {'D': 'center', 'E': 'left', 'F': 'center', 'G': 'center'}.items():
                        sheet[f'{i}{num_cel}'].alignment = Alignment(horizontal=vert_alig, vertical="center",
                                                                     wrap_text=True)
                    sheet.row_dimensions[num_cel].height = 20
                    num_cel += 1
                    num_par += 1
        # Прячем столбцы с привязками
        for col in ('A', 'B', 'C'):
            sheet.column_dimensions[col].hidden = True
        # Добавляем подпись в конце
        num_cel += 2
        sheet.row_dimensions[num_cel].height = 35
        for cell, i in {'E': '="должность"', 'F': '="ФИО"', 'G': '="подпись"'}.items():
            sheet[f'{cell}{num_cel}'] = i
            sheet[f'{cell}{num_cel}'].font = Font(size=16, name='Arial', bold=True)
            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="top")
            sheet[f'{cell}{num_cel}'].border = Border(top=Side(style='thin'))

        wb.save(os.path.join('File_for_Import', 'Reports', f'{node_param_rus} {obj[1]}.xlsx'))

    return
