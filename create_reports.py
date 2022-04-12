import openpyxl
import os
from openpyxl.styles import Font, Alignment, numbers
from openpyxl.styles.borders import Border, Side


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
        sheet.column_dimensions['E'].width = 100
        sheet.column_dimensions['F'].width = 25
        sheet.column_dimensions['G'].width = 25
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
                        'F3': '="Значение"', 'G3': '="Ед. измерения"'}.items():
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
                    if not (num_par-1) % 17 and num_par != 1:
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
                                        'F': '="Значение"', 'G': '="Ед. измерения"'}.items():
                            sheet[f'{cell}{num_cel}'] = i
                            sheet[f'{cell}{num_cel}'].font = Font(size=14, name='Arial', bold=True)
                            sheet[f'{cell}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                            sheet[f'{cell}{num_cel}'].border = thin_border
                        num_cel += 1

                    sheet[f'C{num_cel}'] = f'="{node_alg_name}.{par}"'
                    sheet[f'D{num_cel}'] = f'="{num_par}"'
                    sheet[f'E{num_cel}'] = f'="{property_par[1]}  "'  # Русское наименование
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
                    for i in ('D', 'F', 'G'):
                        sheet[f'{i}{num_cel}'].alignment = Alignment(horizontal="center", vertical="center")
                    sheet.row_dimensions[num_cel].height = 20
                    num_cel += 1
                    num_par += 1
        # Прячем столбцы с привязками
        for col in ['A', 'B', 'C']:
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
