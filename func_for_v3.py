# from my_func import is_f_ind
from string import Template
from copy import copy
import os
from algroritm import is_load_algoritm
import datetime
from time import sleep
# для тестирования новых возможностей
import xml.etree.ElementTree as ET
import lxml.etree
from openpyxl.utils import get_column_letter


def multiple_replace_xml(target_str):
    replace_values = {'address_map': 'address-map', 'access_level': 'access-level', 'ct_object': 'ct:object',
                      'base_type': 'base-type', 'xmlns_dp': 'xmlns:dp', 'xmlns_trei': 'xmlns:trei',
                      'xmlns_ct': 'xmlns:ct', 'trei_': 'trei:', 'dp_application': 'dp:application',
                      'ct_init-ref': 'ct:init-ref', 'ct_parameter': 'ct:parameter', 'ct_subject-ref': 'ct:subject-ref',
                      'const_access': 'const-access', 'ct_bind': 'ct:bind', 'xmlns_r': 'xmlns:r',
                      'xmlns_snmp': 'xmlns:snmp', 'dp_computer': 'dp:computer',
                      'dp_ethernet-adapter': 'dp:ethernet-adapter', 'dp_external-runtime': 'dp:external-runtime',
                      'snmp_': 'snmp:', 'poll_port': 'poll-port', 'poll_password': 'poll-password',
                      'notification_port': 'notification-port', 'notification_password': 'notification-password',
                      'protocol_version': 'protocol-version', 'security_level': 'security-level',
                      'auth_protocol': 'auth-protocol', 'priv_protocol': 'priv-protocol',
                      'source_code': 'source-code', 'ct_trigger': 'ct:trigger', 'ct_handler': 'ct:handler',
                      'ct_formula': 'ct:formula'}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str


def add_xml_par_plc(name_group, sl_par, parent_node, sl_attr_par):
    # sl_par = {алг_пар: (тип параметра в студии, русское имя, ед измер, короткое имя, количество знаков)}
    # sl_attr_par - словарь атрибутов параметра {алг_пар: {тип атрибута: значение атрибута}}
    child_group = ET.SubElement(parent_node, 'ct_object',
                                name=(f'{name_group[0]}' if isinstance(name_group, tuple) else f"{name_group}"),
                                access_level="public")
    if isinstance(name_group, tuple):
        ET.SubElement(child_group, 'attribute', type='unit.System.Attributes.Description', value=f'{name_group[1]}')
    # Для каждого параметра в текущем контроллере
    # создаём конструкцию параметра
    for par, tuple_par in sl_par.items():
        child_par = ET.SubElement(child_group, 'ct_object', name=f"{par}",
                                  base_type=f"Types.{tuple_par[0]}",
                                  aspect="Types.PLC_Aspect", access_level="public")
        for type_attr, value in sl_attr_par[par].items():
            ET.SubElement(child_par, 'attribute', type=f"{type_attr}", value=f"{value}")
    return


def add_xml_par_ios(set_cpu_object, objects, name_group, sl_par, parent_node, plc_node_tree, sl_agreg):
    # ...то создаём узел AI в IOS-аспекте
    child_group = ET.SubElement(parent_node, 'ct_object', name=f'{name_group}', access_level="public")
    # ...добавляем агрегаторы
    for agreg, type_agreg in sl_agreg.items():
        ET.SubElement(child_group, 'ct_object', name=f'{agreg}', base_type=f"{type_agreg}",
                      aspect="Types.IOS_Aspect", access_level="public")
    # Для каждого контроллера в структуре анпаров...
    for cpu in sl_par:
        # Для каждого параметра...
        # Если перебираемый контроллер принадлежит объекту
        if cpu in set_cpu_object:
            # ...для каждого параметра контроллера...
            for par, tuple_par in sl_par[cpu].items():
                # ...создаём структуру параметра
                base_type = (f"Types.{tuple_par[0].replace('PLC_View', 'IOS_NotHistory_View')}"  #
                             if 'Сохраняемый - Нет' in tuple_par
                             else f"Types.{tuple_par[0].replace('PLC_View', 'IOS_View')}")
                aspect = ("Types.IOS_NotHistory_Aspect" if 'Сохраняемый - Нет' in tuple_par else "Types.IOS_Aspect")
                child_par = ET.SubElement(child_group, 'ct_object', name=f"{par}",
                                          base_type=base_type,
                                          aspect=aspect,
                                          original=f"PLC_{cpu}_{objects[2]}.CPU.Tree.{plc_node_tree}.{par}",
                                          access_level="public")
                ET.SubElement(child_par, 'ct_init-ref',
                              ref="_PLC_View", target=f"PLC_{cpu}_{objects[2]}.CPU.Tree.{plc_node_tree}.{par}")
                # Если 'AI', 'AE', 'SET', то добавляем Value с гистерезисом
                if name_group in ('AI', 'AE', 'SET'):
                    deadband_hist = 1/(10**int(tuple_par[5])) if tuple_par[5] != '' else 0.01
                    object_value = ET.SubElement(child_par, 'ct_parameter', name='Value', type='float32',
                                                 direction='out', access_level="public")
                    ET.SubElement(object_value, 'attribute', type="unit.Server.Attributes.History",
                                  value=f"Enable=\"True\" Deadband=\"{deadband_hist}\" ServerTime=\"False\"")
                    ET.SubElement(object_value, 'attribute', type="unit.System.Attributes.Description",
                                  value=f"@(object:unit.System.Attributes.Description)")
                    ET.SubElement(object_value, 'attribute', type="unit.Server.Attributes.Unit",
                                  value=f"@(object:Attributes.EUnit)")
                    ET.SubElement(child_par, 'ct_formula', source_code="_PLC_View.States.Value", target="Value")
                # Если ИМ АО, то добавляем Set и iPos с гистерезисом
                elif name_group in ('IM',) and 'IM_AO' in tuple_par[0]:
                    deadband_hist = 1/(10**int(tuple_par[6])) if tuple_par[6] != '' else 0.01
                    for sig, attr_sig in {'Set': ('Задание',), 'iPos': ('Положение',)}.items():
                        object_sig = ET.SubElement(child_par, 'ct_parameter', name=f'{sig}', type='float32',
                                                   direction='out', access_level="public")
                        ET.SubElement(object_sig, 'attribute', type="unit.System.Attributes.Description",
                                      value=f"{attr_sig[0]}")
                        ET.SubElement(object_sig, 'attribute', type="unit.Server.Attributes.Unit",
                                      value=f"@(object:Attributes.EUnit)")
                        ET.SubElement(object_sig, 'attribute', type="unit.Server.Attributes.History",
                                      value=f"Enable=\"True\" Deadband=\"{deadband_hist}\" ServerTime=\"False\"")
                        ET.SubElement(child_par, 'ct_formula', source_code=f"_PLC_View.States.{sig}", target=f"{sig}")
                # Если драйверный параметр, AI и сохраняем историю
                elif 'System.DRV' in plc_node_tree and 'DRV_AI_IOS_View' in base_type:
                    deadband_hist = 1/(10**int(tuple_par[8])) if tuple_par[8] != '' else 0.01
                    object_value = ET.SubElement(child_par, 'ct_parameter', name='Value', type='float32',
                                                 direction='out', access_level="public")
                    ET.SubElement(object_value, 'attribute', type="unit.Server.Attributes.History",
                                  value=f"Enable=\"True\" Deadband=\"{deadband_hist}\" ServerTime=\"False\"")
                    ET.SubElement(object_value, 'attribute', type="unit.System.Attributes.Description",
                                  value=f"@(object:unit.System.Attributes.Description)")
                    ET.SubElement(object_value, 'attribute', type="unit.Server.Attributes.Unit",
                                  value=f"@(object:Attributes.EUnit)")
                    ET.SubElement(child_par, 'ct_formula', source_code="_PLC_View.States.Value", target="Value")

    return


def is_read_ai_ae_set(sheet, type_signal):
    # return_sl = {cpu: {алг_пар: (тип параметра в студии, русское имя, ед измер, короткое имя, количество знаков,
    # количество знаков для истории)}}
    return_sl = {}
    # return_sl_sday = {cpu: {Перфискспапки.alg_par: русское имя}}
    return_sl_sday = {}
    # return_sl_mnemo = {узел: список параметров узла}
    return_sl_mnemo = {}
    sl_plc_aspect = {'AI': 'AI.AI_PLC_View', 'AE': 'AE.AE_PLC_View', 'SET': 'SET.SET_PLC_View'}
    # print('Зашли в фукнкцию, максимальное чилсло колонок - ', sheet.max_column)
    cells = sheet['A1': get_column_letter(100) + str(100)]  # sheet.max_column
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_unit = is_f_ind(cells[0], 'Единицы измерения')
    index_short_name = is_f_ind(cells[0], 'Короткое наименование')
    index_frag_dig = is_f_ind(cells[0], 'Количество знаков')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_res = is_f_ind(cells[0], 'Резервный')
    index_node_mnemo = is_f_ind(cells[0], 'Узел')
    index_sday = is_f_ind(cells[0], 'Используется в ведомости')

    cells = sheet['A2': get_column_letter(100) + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        if par[index_res].value == 'Нет':
            if par[index_cpu_name].value not in return_sl:
                # return_sl = {cpu: {алг_пар: (русское имя, ед измер, короткое имя, количество знаков,
                # количество знаков для истории)}}
                return_sl[par[index_cpu_name].value] = {}

            if par[index_sday].value == 'Да':
                if par[index_cpu_name].value not in return_sl_sday:
                    return_sl_sday[par[index_cpu_name].value] = {}
                return_sl_sday[par[index_cpu_name].value].update(
                    {f"{type_signal}.{par[index_alg_name].value.replace('|', '_')}": par[index_rus_name].value})

            frag_dig_hist = ''.join([i for i
                                     in str(par[index_frag_dig].comment)[:str(par[index_frag_dig].comment).find('by')]
                                     if i.isdigit()]) if par[index_frag_dig].comment else par[index_frag_dig].value

            return_sl[par[index_cpu_name].value].update({par[index_alg_name].value.replace('|', '_'): (
                sl_plc_aspect.get(type_signal, 'Пустой тип'),
                par[index_rus_name].value,
                par[index_unit].value,
                par[index_short_name].value,
                par[index_frag_dig].value,
                frag_dig_hist)})
            # Если не парсим уставки, то заполняем словарь для мнемосхемы
            if 'SP|' not in par[index_alg_name].value and par[index_node_mnemo].value not in return_sl_mnemo:
                return_sl_mnemo[par[index_node_mnemo].value] = list()
            if 'SP|' not in par[index_alg_name].value:
                return_sl_mnemo[par[index_node_mnemo].value].append(par[index_alg_name].value.replace('|', '_'))

    return return_sl, return_sl_mnemo, return_sl_sday


def is_read_di(sheet):
    # return_sl_di = {cpu: {алг_пар: (тип параметра в студии, русское имя, sColorOff, sColorOn)}}
    return_sl_di = {}
    # return_sl_mnemo = {узел: список параметров узла}
    return_sl_mnemo = {}

    # Словарь соответствия цветов и его идентификатора в Альфе
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    # Словарь соответствия типа сигнала(DI или DI_AI) и его ПЛК-Аспекта
    sl_plc_aspect = {'Да': 'DI.DI_PLC_View', 'Нет': 'DI.DI_PLC_View', 'AI': 'DI_AI.DI_AI_PLC_View'}
    # Словарь предупреждений {CPU : {алг.имя : (рус.имя, тип наличия)}}
    sl_wrn_di = {}

    cells = sheet['A1': get_column_letter(100) + str(100)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_im = is_f_ind(cells[0], 'ИМ')
    index_color_on = is_f_ind(cells[0], 'Цвет при наличии')
    index_color_off = is_f_ind(cells[0], 'Цвет при отсутствии')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_res = is_f_ind(cells[0], 'Резервный')
    index_control_cel = is_f_ind(cells[0], 'Контроль цепи')
    index_wrn = is_f_ind(cells[0], 'Предупреждение')
    index_wrn_text = is_f_ind(cells[0], 'Текст предупреждения')
    index_node_mnemo = is_f_ind(cells[0], 'Узел')

    cells = sheet['A2': get_column_letter(100) + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        if par[index_cpu_name].value not in sl_wrn_di:
            sl_wrn_di[par[index_cpu_name].value] = {}
        if par[index_res].value == 'Нет' and par[index_im].value == 'Нет':
            if par[index_cpu_name].value not in return_sl_di:
                # return_sl_di = {cpu: {алг_пар: (тип параметра в студии, русское имя, sColorOff, sColorOn)}}
                return_sl_di[par[index_cpu_name].value] = {}

            return_sl_di[par[index_cpu_name].value].update(
                {par[index_alg_name].value.replace('|', '_'): (
                    sl_plc_aspect.get(par[index_control_cel].value),
                    par[index_rus_name].value,
                    sl_color_di.get(par[index_color_off].fill.start_color.index, '404'),
                    sl_color_di.get(par[index_color_on].fill.start_color.index, '404'))})

            # Если есть предупреждение по дискрету и канал не переведён в резерв и не привязан к ИМ
            # то добавляем в словарь предупреждений по дискретам
            if 'Да' in par[index_wrn].value:
                cpu_name_par = par[index_cpu_name].value
                alg_par = par[index_alg_name].value.replace('|', '_')
                sl_wrn_di[cpu_name_par][alg_par] = (par[index_wrn_text].value, par[index_wrn].value)

            if par[index_node_mnemo].value not in return_sl_mnemo:
                return_sl_mnemo[par[index_node_mnemo].value] = list()
            return_sl_mnemo[par[index_node_mnemo].value].append(par[index_alg_name].value.replace('|', '_'))

    return return_sl_di, sl_wrn_di, return_sl_mnemo


def is_read_im(sheet, sheet_imao):
    # return_sl_im = {cpu: {алг_пар: (русское имя, StartView, Gender, ед измер, количество знаков(для д.ИМ=0),
    # количество знаков для истории)}}
    return_sl_im = {}

    sl_im_plc = {}
    # Словарь соответствия типа ИМ и его ПЛК аспекта
    if os.path.exists(os.path.join('Template_Alpha', 'Systemach', f'dict_im')):
        with open(os.path.join('Template_Alpha', 'Systemach', f'dict_im'), 'r', encoding='UTF-8') as f_signal:
            for line in f_signal:
                if '#' in line:
                    continue
                if not line.strip():
                    break
                line = line.strip()
                lst_line = [i.strip() for i in line.split(':')]
                sl_im_plc[lst_line[0]] = lst_line[1]
    else:
        print(f'Не найден файл сигналов Template_Alpha/Systemach/dict_im, стуртуры ИМ добавлены не будут')
    # sl_im_plc = {'ИМ1Х0': 'IM1x0.IM1x0_PLC_View', 'ИМ1Х1': 'IM1x1.IM1x1_PLC_View', 'ИМ1Х2': 'IM1x2.IM1x2_PLC_View',
    #              'ИМ2Х2': 'IM2x2.IM2x2_PLC_View', 'ИМ2Х4': 'IM2x2.IM2x4_PLC_View',
    #              'ИМ1Х0и': 'IM1x0inv.IM1x0inv_PLC_View', 'ИМ1Х1и': 'IM1x1inv.IM1x1inv_PLC_View',
    #              'ИМ1Х2и': 'IM1x2inv.IM1x2inv_PLC_View',
    #              'ИМ2Х2с': 'IM2x2.IM2x2_PLC_View',
    #              'ИМАО': 'IM_AO.IM_AO_PLC_View', 'ИМ2Х2ПЧ': 'IM2x2PCH.IM2x2PCH_PLC_View'}

    # Словарь соответствия рода ИМ и его идентификатора в Альфе
    sl_gender = {'С': '0', 'М': '1', 'Ж': '2'}

    cells = sheet['A1': get_column_letter(200) + str(200)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_type_im = is_f_ind(cells[0], 'Тип ИМ')
    index_gender = is_f_ind(cells[0], 'Род')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_work_time = is_f_ind(cells[0], 'Считать наработку')
    index_swap = is_f_ind(cells[0], 'Считать перестановки')
    index_start_view = is_f_ind(cells[0], 'Тип ИМ', target_count=2)

    cells = sheet['A2': get_column_letter(200) + str(sheet.max_row)]
    # Составляем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    sl_cnt = {}
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        # Если считаем наработку, то добавляем в словарь sl_cnt = {CPU: {алг.имя : русское имя}}
        if par[index_work_time].value == 'Да':
            if par[index_cpu_name].value not in sl_cnt:
                sl_cnt[par[index_cpu_name].value] = {}
            sl_cnt[par[index_cpu_name].value].update(
                {par[index_alg_name].value + '_WorkTime': par[index_rus_name].value})
        # Если считаем перестановки, то добавляем в словарь sl_cnt = {CPU: {алг.имя : русское имя}}
        if par[index_swap].value == 'Да':
            if par[index_cpu_name].value not in sl_cnt:
                sl_cnt[par[index_cpu_name].value] = {}
            sl_cnt[par[index_cpu_name].value].update(
                {par[index_alg_name].value + '_Swap': par[index_rus_name].value})

        if par[index_cpu_name].value not in return_sl_im:
            # return_sl_im = {cpu: {алг_пар: (тип ИМа, русское имя, StartView, Gender, ед измер(для д.ИМ='-'),
            # количество знаков(для д.ИМ=0), количество знаков для истории)}}
            return_sl_im[par[index_cpu_name].value] = {}
        if par[index_type_im].value in sl_im_plc:
            return_sl_im[par[index_cpu_name].value].update(
                {par[index_alg_name].value: (sl_im_plc.get(par[index_type_im].value),
                                             par[index_rus_name].value,
                                             ''.join([i for i in par[index_start_view].value if i.isdigit()]),
                                             sl_gender.get(par[index_gender].value),
                                             '-',
                                             '0',
                                             '0')})

    # Обрабатываем ИМ АО
    cells = sheet_imao['A1': get_column_letter(200) + str(200)]

    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_start_view = is_f_ind(cells[0], 'Тип ИМ')
    index_yes_im = is_f_ind(cells[0], 'ИМ')
    index_gender = is_f_ind(cells[0], 'Род')
    index_res = is_f_ind(cells[0], 'Резервный')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_frag_dig = is_f_ind(cells[0], 'Количество знаков')
    index_unit = is_f_ind(cells[0], 'Единицы измерения')

    cells = sheet_imao['A2': get_column_letter(200) + str(sheet.max_row)]
    # Составляем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu_imao = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu_imao.add(par[index_cpu_name].value)
        if par[index_yes_im].value == 'Да' and par[index_res].value == 'Нет':
            if par[index_cpu_name].value not in return_sl_im:
                # return_sl_im = {cpu: {алг_пар: (тип ИМа, русское имя, StartView, Gender, ед измер, количество знаков,
                # количество знаков для истории)}}
                return_sl_im[par[index_cpu_name].value] = {}
            frag_dig_hist = ''.join([i for i
                                     in str(par[index_frag_dig].comment)[:str(par[index_frag_dig].comment).find('by')]
                                     if i.isdigit()]) if par[index_frag_dig].comment else par[index_frag_dig].value
            if 'ИМАО' in sl_im_plc:
                return_sl_im[par[index_cpu_name].value].update(
                    {par[index_alg_name].value: (sl_im_plc.get('ИМАО'),
                                                 par[index_rus_name].value,
                                                 ''.join([i for i in par[index_start_view].value if i.isdigit()]),
                                                 sl_gender.get(par[index_gender].value),
                                                 par[index_unit].value,
                                                 par[index_frag_dig].value,
                                                 frag_dig_hist)})

    return return_sl_im, sl_cnt


def is_read_create_diag(book, name_prj, *sheets_signal):
    sheet_module = book['Модули']
    # Словарь возможных модулей со стартовым описанием каналов
    sl_modules_channel = {}
    if os.path.exists(os.path.join('Template_Alpha', 'Systemach', f'dict_module_channel')):
        with open(os.path.join('Template_Alpha', 'Systemach', f'dict_module_channel'), 'r', encoding='UTF-8') as f_sig:
            for line in f_sig:
                if '#' in line:
                    continue
                if not line.strip():
                    break
                line = line.strip()
                lst_line = [i.strip() for i in line.split(':')]
                if '*' in lst_line[1]:
                    tm = [i.strip() for i in lst_line[1].split('*')]
                    sl_modules_channel[lst_line[0]] = [tm[0]] * int(tm[1])
                else:
                    sl_modules_channel[lst_line[0]] = lst_line[1]
    else:
        print(f'Не найден файл сигналов Template_Alpha/Systemach/dict_module_channel, '
              f'стуртуры модулей добавлены не будут')
    # sl_modules = {
    #     'M547A': ['Резерв'] * 16,
    #     'M537V': ['Резерв'] * 8,
    #     'M557D': ['Резерв'] * 32,
    #     'M557O': ['Резерв'] * 32,
    #     'M932C_2N': ['Резерв'] * 8,
    #     'M903E': 'CPU', 'M991E': 'CPU', 'M915E': 'CPU', 'M501E': 'CPU', 'M991S': 'CPU',
    #     'M548A': ['Резерв'] * 16,
    #     'M538V': ['Резерв'] * 8,
    #     'M558D': ['Резерв'] * 32,
    #     'M558O': ['Резерв'] * 32,
    #     'M531I': ['Резерв'] * 8,
    #     'M543G': ['Резерв'] * 16,
    #     'M5571': ['Резерв'] * 32,
    #     'M532U': ['Резерв'] * 8,  # Добавлено в тестовом режиме для Игринской!!!
    #     'M582IS': ['Резерв'] * 3,  # Добавлено в тестовом режиме для Игринской!!!
    # }
    sl_type_modules = {}
    tuple_cpu_name = tuple()
    if os.path.exists(os.path.join('Template_Alpha', 'Systemach', f'dict_module')):
        with open(os.path.join('Template_Alpha', 'Systemach', f'dict_module'), 'r', encoding='UTF-8') as f_signal:
            for line in f_signal:
                if '#' in line:
                    continue
                if not line.strip():
                    break
                line = line.strip()
                lst_line = [i.strip() for i in line.split(':')]
                sl_type_modules[lst_line[0]] = lst_line[1]
                if 'CPU' in lst_line[1]:
                    tuple_cpu_name += (lst_line[0],)
    else:
        print(f'Не найден файл сигналов Template_Alpha/Systemach/dict_module, стуртуры модулей добавлены не будут')

    # sl_type_modules = {
    #     'M903E': 'Types.DIAG_CPU.DIAG_CPU_M903E_PLC_View',
    #     'M991E': 'Types.DIAG_CPU.DIAG_CPU_M991E_PLC_View',
    #     'M991S': 'Types.DIAG_CPU.DIAG_CPU_M991E_PLC_View',
    #     'M547A': 'Types.DIAG_M547A.DIAG_M547A_PLC_View',
    #     'M548A': 'Types.DIAG_M548A.DIAG_M548A_PLC_View',
    #     'M537V': 'Types.DIAG_M537V.DIAG_M537V_PLC_View',
    #     'M538V': 'Types.DIAG_M538V.DIAG_M538V_PLC_View',
    #     'M932C_2N': 'Types.DIAG_M932C_2N.DIAG_M932C_2N_PLC_View',
    #     'M557D': 'Types.DIAG_M557D.DIAG_M557D_PLC_View',
    #     'M558D': 'Types.DIAG_M558D.DIAG_M558D_PLC_View',
    #     'M557O': 'Types.DIAG_M557O.DIAG_M557O_PLC_View',
    #     'M558O': 'Types.DIAG_M558O.DIAG_M558O_PLC_View',
    #     'M915E': 'Types.DIAG_CPU.DIAG_CPU_M915E_PLC_View',
    #     'M501E': 'Types.DIAG_CPU.DIAG_CPU_M501E_PLC_View',
    #     'M531I': 'Types.DIAG_M531I.DIAG_M531I_PLC_View',
    #     'M543G': 'Types.DIAG_M543G.DIAG_M543G_PLC_View',
    #     'M532U': 'Types.DIAG_M532U_test.DIAG_M532U_test_PLC_View',  # Добавлено в тестовом режиме для Игринской!!!
    #     'M582IS': 'Types.DIAG_M582IS_test.DIAG_M582IS_test_PLC_View',  # Добавлено в тестовом режиме для Игринской!!!
    # }
    cells = sheet_module['A1': get_column_letter(50) + str(50)]
    type_module_index = is_f_ind(cells[0], 'Шифр модуля')
    name_module_index = is_f_ind(cells[0], 'Имя модуля')
    cpu_index = is_f_ind(cells[0], 'CPU')
    cells = sheet_module['A2': get_column_letter(50) + str(sheet_module.max_row)]
    sl_modules_cpu = {}
    # словарь sl_modules_cpu {имя CPU: {имя модуля: (тип модуля, [каналы])}}
    for p in cells:
        if p[0].value is None:
            break
        if sl_modules_channel.get(p[type_module_index].value):
            aa = copy(sl_modules_channel[p[type_module_index].value])
            if p[cpu_index].value not in sl_modules_cpu:
                sl_modules_cpu[p[cpu_index].value] = {}
            sl_modules_cpu[p[cpu_index].value].update({p[name_module_index].value: (p[type_module_index].value, aa)})
    # В тестовом режиме для игринской добавляем два новых модуля в GTU жёстко!!!
    if 'Игринская' in name_prj:
        if sl_modules_channel.get('M532U') and sl_modules_channel.get('M582IS'):
            aa = copy(sl_modules_channel['M532U'])
            sl_modules_cpu['GTU'].update({'AD102': ('M532U', aa)})
            aa = copy(sl_modules_channel['M582IS'])
            sl_modules_cpu['GTU'].update({'AD1': ('M582IS', aa)})

    # sl_for_diag - словарь для корректной педечачи для создания индексов
    sl_for_diag = {}
    for name_cpu, value in sl_modules_cpu.items():
        keys_sl_for_diag = [i if value[i][0] not in tuple_cpu_name
                            else 'CPU' for i in value]
        value_sl_for_diag = [value[i][0] if value[i][0] not in tuple_cpu_name
                             else (i, value[i][0]) for i in value]
        sl_for_diag[name_cpu] = dict(zip(keys_sl_for_diag, value_sl_for_diag))

    # пробегаемся по листам, где могут быть указаны каналы модулей
    for jj in sheets_signal:
        sheet_run = book[jj]
        cells_run = sheet_run['A1': 'O' + str(sheet_run.max_column)]
        num_canal_index = is_f_ind(cells_run[0], 'Номер канала')
        no_stand_index = is_f_ind(cells_run[0], 'Нестандартный канал')
        cpu_par_index = is_f_ind(cells_run[0], 'CPU')
        name_module_par_index = is_f_ind(cells_run[0], 'Номер модуля')
        name_par_index = is_f_ind(cells_run[0], 'Наименование параметра')
        control_index = is_f_ind(cells_run[0], 'Контроль цепи')
        no_stand_kc_index = is_f_ind(cells_run[0], 'Нестандартный канал КЦ')
        name_module_par_kc_index = is_f_ind(cells_run[0], 'Номер модуля контроля')
        num_canal_kc_index = is_f_ind(cells_run[0], 'Номер канала контроля')
        reserve_par_index = is_f_ind(cells_run[0], 'Резервный')
        cells_run = sheet_run['A2': 'O' + str(sheet_run.max_row)]
        # пробегаемся по параметрам на листе
        for par in cells_run:
            # Если сигнал не резернвый...
            if par[reserve_par_index].value == 'Нет':
                # если не указан НЕстандартный канал, то вносим в список
                if par[no_stand_index].value == 'Нет':
                    tmp_ind = int(par[num_canal_index].value) - 1
                    if sl_modules_cpu.get(par[cpu_par_index].value) and \
                            sl_modules_cpu[par[cpu_par_index].value].get(par[name_module_par_index].value):
                        sl_modules_cpu[par[cpu_par_index].value][par[name_module_par_index].value][1][tmp_ind] = \
                            par[name_par_index].value
                # если выбран контроль цепи и контроль стандартный, то также добавляем в список
                if par[control_index].value == 'Да' and par[no_stand_kc_index].value == 'Нет':
                    tmp_ind = int(par[num_canal_kc_index].value) - 1
                    if sl_modules_cpu.get(par[cpu_par_index].value) and \
                            sl_modules_cpu[par[cpu_par_index].value].get(par[name_module_par_index].value):
                        sl_modules_cpu[par[cpu_par_index].value][par[name_module_par_kc_index].value][1][tmp_ind] = \
                            f"КЦ: {par[name_par_index].value}"

    # sl_modules_cpu {имя CPU: {имя модуля: (тип модуля в студии, тип модуля, [каналы])}}
    return {cpu: {mod: (sl_type_modules.get(value[0], 'Types.').replace('Types.', ''), ) + value
                  for mod, value in sl_modules_cpu[cpu].items() if sl_type_modules.get(value[0])}
            for cpu in sl_modules_cpu}, sl_for_diag


def is_create_net(sl_object_all, sheet_net):
    # Проработать в студии IOlogic - настройка в конфигураторе !!!
    cells = sheet_net['A1': get_column_letter(60) + str(60)]

    index_rus_name = is_f_ind(cells[0], 'Наименование юнита')
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_object_name = is_f_ind(cells[0], 'Объект')
    index_type = is_f_ind(cells[0], 'Тип')
    index_ip = is_f_ind(cells[0], 'IP-адрес')
    index_ip_res = is_f_ind(cells[0], 'Резервный IP-адрес')
    index_option = is_f_ind(cells[0], 'Настройка')

    cells = sheet_net['A2': get_column_letter(60) + str(sheet_net.max_row)]

    tuple_net_res = ('SWITCH_TREI_S34X',)
    tuple_net_with_option = ('IOLOGIC_MOXA_E2242',)

    # return_sl_net = {Объект: {алг.имя: {параметры столбцов: значение}}}
    return_sl_net = {}
    for par in cells:
        if par[0].value is None:
            break
        if par[index_object_name].value not in return_sl_net:
            return_sl_net[par[index_object_name].value] = {}
        return_sl_net[par[index_object_name].value].update({par[index_alg_name].value: {
            'Unit': par[index_rus_name].value,
            'Type': par[index_type].value,
            'IP': '.'.join([a.lstrip('0') for a in par[index_ip].value.split('.')]),
            'IP_res': ('.'.join([a.lstrip('0') for a in par[index_ip_res].value.split('.')])
                       if par[index_type].value in tuple_net_res else ''),
            'Option': (par[index_option].value if par[index_type].value in tuple_net_with_option else '')}})

    # Для каждого объекта
    for objects in sl_object_all:
        # Если нашли объект в словаре
        if objects[0] in return_sl_net:
            root_plc_aspect = ET.Element('omx', xmlns="system", xmlns_dp="automation.deployment",
                                         xmlns_snmp="automation.snmp", xmlns_ct="automation.control")
            for alg, sl_value in return_sl_net[objects[0]].items():
                child_alg = ET.SubElement(root_plc_aspect, 'dp_computer', name=f"{objects[0]}_{alg}")
                ET.SubElement(child_alg, 'dp_ethernet-adapter', name="Eth1", address=sl_value['IP'])
                if sl_value['IP_res']:
                    ET.SubElement(child_alg, 'dp_ethernet-adapter', name="Eth2", address=sl_value['IP_res'])
                child_runtime = ET.SubElement(child_alg, 'dp_external-runtime', name="Runtime")
                ET.SubElement(child_runtime, 'snmp_snmp-agent', name="SnmpAgent",
                              poll_port="161", poll_password="public", notification_port="162",
                              notification_password="public", protocol_version="Snmp_v1",
                              security_level="NoAuthNoPriv", auth_protocol="MD5", priv_protocol="AES",
                              address_map="Application.SnmpLinkMap")
                child_app = ET.SubElement(child_runtime, 'dp_application-object', name="Application",
                                          access_level="public")
                ET.SubElement(child_app, 'snmp_snmp-link-map', name="SnmpLinkMap",
                              file='SNMP\\' + f'{sl_value["Type"]}_map.xml')
                child_data = ET.SubElement(child_app, 'ct_object', name="Data", access_level="public")
                child_data_app = ET.SubElement(child_data, 'ct_object', name="Data",
                                               base_type=f"Types.SNMP_Switch.{sl_value['Type']}_PLC_View",
                                               aspect="Types.PLC_Aspect",
                                               access_level="public")
                ET.SubElement(child_data_app, 'attribute', type="unit.System.Attributes.Description",
                              value=f"{sl_value['Unit']}")

            # Нормируем и записываем IOS-аспект
            temp = ET.tostring(root_plc_aspect).decode('UTF-8')

            check_diff_file(check_path=os.path.join('File_for_Import', 'PLC_Aspect_importDomain'),
                            file_name_check=f'file_out_NET_{objects[0]}.omx-export',
                            new_data=multiple_replace_xml(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                              pretty_print=True, encoding='unicode')),
                            message_print=f'Требуется заменить ПЛК-аспект сети объекта {objects[0]}')
    return return_sl_net


def is_create_service_signal(sl_object_all):
    sl_num_eth = {1: 'Основная сеть', 2: 'Резервная сеть'}
    # Новая часть
    root_aspect = ET.Element('omx', xmlns="system", xmlns_ct="automation.control", xmlns_r="automation.reference")
    child_service = ET.SubElement(root_aspect, 'ct_object', name='Service', access_level="public")
    ET.SubElement(child_service, 'attribute', type="unit.Server.Attributes.Replicate", value="false")
    child_modules = ET.SubElement(child_service, 'ct_object', name='Modules', access_level="public")
    child_unet = ET.SubElement(child_modules, 'ct_object', name='UNET Client', access_level="public")
    ET.SubElement(child_unet, 'attribute', type="unit.System.Attributes.Comment", value="для диагностики связи с ПЛК")

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            child_plc = ET.SubElement(child_unet, 'ct_object', name=f'PLC_{cpu}_{objects[2]}', access_level="public")
            for numeth in range(1, 3):
                child_eth = ET.SubElement(child_plc, 'ct_object', name=f'CPU_Eth{numeth}', access_level="public")
                ET.SubElement(child_eth, 'ct_parameter', name='IsConnected',
                              type='bool', direction='out', access_level="public")
                ET.SubElement(child_eth, 'attribute', type='unit.System.Attributes.Comment',
                              value=f"{sl_num_eth.get(numeth)}")

    # Нормируем и записываем IOS-аспект
    temp = ET.tostring(root_aspect).decode('UTF-8')

    check_diff_file(check_path=os.path.join('File_for_Import', 'IOS_Aspect_in_ApplicationServer'),
                    file_name_check=f'Service_signal.omx-export',
                    new_data=multiple_replace_xml(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                      pretty_print=True, encoding='unicode')),
                    message_print=f'Требуется заменить сервисные сигналы (файл Service_signal.omx-export)')

    return


# Функция создания узла SYS
def is_create_sys(sl_object_all: dict, name_prj: str):
    root_aspect = ET.Element('omx', xmlns="system", xmlns_ct="automation.control", xmlns_r="automation.reference")
    child_sys = ET.SubElement(root_aspect, 'ct_object', name='SYS', access_level="public")
    ET.SubElement(child_sys, 'attribute', type="unit.System.Attributes.Description", value="Система")

    child_message = ET.SubElement(child_sys, 'ct_object', name='Message', access_level="public")
    ET.SubElement(child_message, 'attribute', type="unit.System.Attributes.Comment",
                  value="Для глобальных сообщений оператора")
    child_cmd = ET.SubElement(child_message, 'ct_parameter', name='cmd_operator', type="bool", direction="out",
                              access_level="public")
    ET.SubElement(child_cmd, 'attribute', type='unit.Server.Attributes.Alarm',
                  value=f'{{"Condition":{{"IsEnabled":"true",'
                        f'"Subconditions":[{{"AckStrategy":0,'
                        f'"Message":"___",'
                        f'"Severity":10,"Type":2}},'
                        f'{{"AckStrategy":0,"IsEnabled":true,'
                        f'"Message":"___",'
                        f'"Severity":10,"Type":3}}],'
                        f'"Type":2}}}}')
    ET.SubElement(child_cmd, 'attribute', type="unit.System.Attributes.InitialValue", value="false")
    ET.SubElement(child_cmd, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")

    child_msg = ET.SubElement(child_message, 'ct_parameter', name='msg_operator', type="string", direction="out",
                              access_level="public")
    ET.SubElement(child_msg, 'attribute', type="unit.System.Attributes.InitialValue", value="Действие оператора")
    ET.SubElement(child_msg, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")

    child_handler = ET.SubElement(child_message, 'ct_handler', name='Handler',
                                  source_code="cmd_operator.Messages.Selected.Message = msg_operator.Value;")
    ET.SubElement(child_handler, 'ct_trigger', on='cmd_operator', cause="message-prepare")

    child_objname = ET.SubElement(child_sys, 'ct_parameter', name='ObjNam', type="string", direction="out",
                                  access_level="public")
    ET.SubElement(child_objname, 'attribute', type="unit.System.Attributes.InitialValue",
                  value=f"{';'.join([obj[1] for obj in sl_object_all])}")
    ET.SubElement(child_objname, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")
    ET.SubElement(child_objname, 'attribute', type="unit.Server.Attributes.Replicate", value="false")

    child_objalg = ET.SubElement(child_sys, 'ct_parameter', name='ObjAlg', type="string", direction="out",
                                 access_level="public")
    ET.SubElement(child_objalg, 'attribute', type="unit.System.Attributes.InitialValue",
                  value=f"{';'.join([obj[0] for obj in sl_object_all])}")
    ET.SubElement(child_objalg, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")
    ET.SubElement(child_objalg, 'attribute', type="unit.Server.Attributes.Replicate", value="false")

    child_objnum = ET.SubElement(child_sys, 'ct_parameter', name='ObjNum', type="string", direction="out",
                                 access_level="public")
    ET.SubElement(child_objnum, 'attribute', type="unit.System.Attributes.InitialValue", value=f"{len(sl_object_all)}")
    ET.SubElement(child_objnum, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")
    ET.SubElement(child_objnum, 'attribute', type="unit.Server.Attributes.Replicate", value="false")

    child_systemname = ET.SubElement(child_sys, 'ct_parameter', name='SystemName', type="string", direction="out",
                                     access_level="public")
    ET.SubElement(child_systemname, 'attribute', type="unit.System.Attributes.InitialValue",
                  value=f"{name_prj}")
    ET.SubElement(child_systemname, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")
    ET.SubElement(child_systemname, 'attribute', type="unit.Server.Attributes.Replicate", value="false")

    child_ap_activity_switch = ET.SubElement(child_sys, 'ct_parameter', name='AP_activity_switch',
                                             type="bool", direction="out", access_level="public")
    ET.SubElement(child_ap_activity_switch, 'attribute', type="unit.System.Attributes.InitialValue",
                  value="false")
    ET.SubElement(child_ap_activity_switch, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")

    child_control = ET.SubElement(child_sys, 'ct_object', name='ZControlForAAP', access_level="public")
    child_ready = ET.SubElement(child_control, 'ct_parameter', name='Ready',
                                type="bool", direction="out", access_level="public")
    ET.SubElement(child_ready, 'attribute', type="unit.System.Attributes.InitialValue", value="true")
    ET.SubElement(child_ready, 'attribute', type="unit.Server.Attributes.InitialQuality", value="216")

    # Нормируем и записываем IOS-аспект
    temp = ET.tostring(root_aspect).decode('UTF-8')

    check_diff_file(check_path=os.path.join('File_for_Import', 'IOS_Aspect_in_ApplicationServer'),
                    file_name_check=f'SYS_object.omx-export',
                    new_data=multiple_replace_xml(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                      pretty_print=True, encoding='unicode')),
                    message_print=f'Требуется заменить объект SYS (файл SYS_object.omx-export)')
    return


def is_read_btn(sheet):
    # return_sl = {cpu: {алг_пар: (Тип кнопки в студии, русское имя, )}}
    return_sl = {}
    cells = sheet['A1': get_column_letter(50) + str(50)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')

    cells = sheet['A2': get_column_letter(50) + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        if par[index_cpu_name].value not in return_sl:
            # return_sl = {cpu: {алг_пар: (Тип кнопки в студии, русское имя, )}}
            return_sl[par[index_cpu_name].value] = {}
        return_sl[par[index_cpu_name].value].update({
            'BTN_' + par[index_alg_name].value[par[index_alg_name].value.find('|')+1:]: (
                'BTN.BTN_PLC_View',
                par[index_rus_name].value)
        })

    return return_sl


def is_read_pz(sheet, sl_ai: dict, sl_ae: dict):

    cells = sheet['A1': get_column_letter(50) + str(50)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')
    index_cond = is_f_ind(cells[0], 'Условия защиты')

    cells = sheet['A2': get_column_letter(50) + str(sheet.max_row)]

    # Словарь Защит, в котором ключ - cpu, значение - кортеж списков [алг имя, рус. имя, единицы измерения]
    sl_pz = {}
    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        if par[index_type_protect].value not in 'АОссАОбсВОссВОбсАОНО':
            continue
        else:
            # Если в словарь защит нет инфы по контроллеру, то добавляем пустой кортеж
            if cpu_name_par not in sl_pz:
                sl_pz[cpu_name_par] = ()
            # Далее узнаём единицы измерения защиты
            if par[index_unit].value == '-999.0':
                tmp_eunit = str(par[index_unit].comment)[str(par[index_unit].comment).find(' ') + 1:
                                                         str(par[index_unit].comment).find('by')]
                # Для каждого слова в условии защиты ищем первую BND| и определяем по словарям
                # AI, и AE какие единицы измерения писать, на тот случай, если комменты не правдивы
                for word in par[index_cond].value.split():
                    if 'BND|' in word:
                        check = word[word.find('|')+1:word.rfind('_')]
                        if f'AI_{check}' in sl_ai.get(cpu_name_par, {}):
                            tmp_eunit = sl_ai[cpu_name_par][f'AI_{check}']
                        elif f'AE_{check}' in sl_ae.get(cpu_name_par, {}):
                            tmp_eunit = sl_ae[cpu_name_par][f'AE_{check}']
                        break
            else:
                tmp_eunit = par[index_unit].value
            # В словарь Защит соответсвтующего контроллера добавляем [алг имя, рус. имя, единицы измерения]
            rus_name = f'{par[index_type_protect].value}. {par[index_rus_name].value}'
            sl_pz[cpu_name_par] += ([par[index_alg_name].value, rus_name, tmp_eunit],)

    # В словаре защит алгоритмическое имя меняем на A+ номер
    num_pz = 0
    for plc in sl_pz:
        for protect in range(len(sl_pz[plc])):
            sl_pz[plc][protect][0] = 'A' + str(num_pz).zfill(3)
            num_pz += 1

    # Из функции возвращаем словарь, в котором ключ - cpu, значение - кортеж алг. имён A+000 и т.д.
    return_sl_pz = {key: tuple([prot[0] for prot in value]) for key, value in sl_pz.items()}
    # sl_pz_xml = {cpu: {алг_имя(A000): (тип защиты в студии, рус.имя, ед измерения)}}
    sl_pz_xml = {cpu: dict(zip(return_sl_pz[cpu], [('PZ.PZ_PLC_View',) + tuple(val[1:]) for val in value]))
                 for cpu, value in sl_pz.items()}
    return return_sl_pz, sl_pz_xml


def is_read_signals(sheet, sl_wrn_di):
    return_wrn = {}
    return_ts = {}
    return_ppu = {}
    return_alr = {}
    return_modes = {}
    return_alg = {}
    sl_signal_type = {
        'ТС': return_ts,
        'ТС (без условий)': return_ts,
        'ГР': return_ppu,
        'ХР': return_ppu,
        'АОсс': return_alr,
        'АО': return_alr,
        'НО': return_alr,
        'АОбс': return_alr,
        'ВОсс': return_alr,
        'ВОбс': return_alr,
        'АС (без условий)': return_alr,
        'BOOL': return_alg,
        'INT': return_alg,
        'FLOAT': return_alg,
        'ПС': return_wrn,
        'ПС (без условий)': return_wrn,
        'Режим': return_modes
    }
    sl_type_wrn = {
        'Да (по наличию)': 'WRN_On.WRN_On_PLC_View',
        'Да (по отсутствию)': 'WRN_Off.WRN_Off_PLC_View'
    }
    cells = sheet['A1': get_column_letter(50) + str(50)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')

    cells = sheet['A2': get_column_letter(50) + str(sheet.max_row)]

    for par in cells:
        if par[index_rus_name].value is None:
            break
        # Если тип защиты есть в словаре типовых сигналов:
        protect = par[index_type_protect].value
        if protect in sl_signal_type:
            if par[index_cpu_name].value not in sl_signal_type[protect]:
                sl_signal_type[protect][par[index_cpu_name].value] = {}
            tuple_update = (f"{protect.replace(' (без условий)','')}. {par[index_rus_name].value}"
                            if protect in 'АОссАОбсВОссВОбсАОНО' or 'АС' in protect
                            else par[index_rus_name].value, )
            if protect in ('BOOL', 'INT', 'FLOAT'):
                tuple_update = (f'ALG.ALG_{protect}_PLC_View',) + tuple_update
            elif 'ПС' in protect:
                tuple_update += ('Да (по наличию)',)
            key_update = ('_'.join(par[index_alg_name].value.split('|')) if protect in ('BOOL', 'INT', 'FLOAT')
                          else par[index_alg_name].value[par[index_alg_name].value.find('|') + 1:])
            if 'Режим' in protect:
                sl_signal_type[protect][par[index_cpu_name].value].update(
                    {'regNum': ('MODES.regNum_PLC_View', 'Номер режима')})
                tuple_update = ('MODES.MODES_PLC_View', f'Режим "{par[index_rus_name].value}"')
            sl_signal_type[protect][par[index_cpu_name].value].update({key_update: tuple_update})

        '''
        пока оставил данный кусок кода как наследие от старого кода, возможно подскажет     
        elif par[type_protect].value in 'АОссАОбсВОссВОбсАОНО' or 'АС' in par[type_protect].value:
            if 'АС' in par[type_protect].value:
                tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = ('АС. ' +
                                                                                    is_cor_chr(par[par_name].value),
                                                                                    'АС')
            else:
                tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = (par[type_protect].value + '. ' +
                                                                                    is_cor_chr(par[par_name].value),
                                                                                    'Защита')
        '''
    # Есть более изящное решение, если приравнять сразу return_wrn = sl_wrn_di в самом начале, но нужно проверить!!!
    for cpu in return_wrn:
        if cpu in sl_wrn_di:
            return_wrn[cpu].update(sl_wrn_di[cpu])
    return_wrn = {cpu: {alg: (sl_type_wrn.get(val[1]), val[0])
                        for alg, val in value.items()} for cpu, value in return_wrn.items()}

    # пробегаемся по словарям в приведённом ниже списке и добавляем в кортежи параметров соответствующие типы
    # да, немного костыль, но красивый
    for change_return in [(return_ts, 'TS.TS_PLC_View'),
                          (return_ppu, 'PPU.PPU_PLC_View'),
                          (return_alr, 'ALR.ALR_PLC_View')]:
        for cpu, sl_par in change_return[0].items():
            for par in sl_par:
                sl_par[par] = (change_return[1],) + sl_par[par]

    return return_ts, return_ppu, return_alr, return_alg, return_wrn, return_modes


def is_read_drv(sheet, sl_all_drv):
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    # sl_type_drv = {
    #     'FLOAT': 'Types.DRV_AI.DRV_AI_PLC_View',
    #     'INT': 'Types.DRV_INT.DRV_INT_PLC_View',
    #     'BOOL': 'Types.DRV_DI.DRV_DI_PLC_View',
    #     'IEC': 'Types.DRV_AI.DRV_AI_PLC_View',
    #     'IECR': 'Types.DRV_AI.DRV_AI_PLC_View',
    #     'IECB': 'Types.DRV_DI.DRV_DI_PLC_View'
    # }
    sl_type_drv = {}
    if os.path.exists(os.path.join('Template_Alpha', 'Systemach', f'dict_type_drv')):
        with open(os.path.join('Template_Alpha', 'Systemach', f'dict_type_drv'), 'r', encoding='UTF-8') as f_signal:
            for line in f_signal:
                if '#' in line:
                    continue
                if not line.strip():
                    break
                line = line.strip()
                lst_line = [i.strip() for i in line.split(':')]
                sl_type_drv[lst_line[0]] = lst_line[1]
    else:
        print(f'Не найден файл сигналов Template_Alpha/Systemach/dict_type_drv, стуртуры модулей добавлены не будут')

    cells = sheet['A1': get_column_letter(50) + str(50)]

    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_unit = is_f_ind(cells[0], 'Единица измерения')
    index_type_sig = is_f_ind(cells[0], 'Тип')
    index_type_msg = is_f_ind(cells[0], 'Тип сообщения')
    index_color_on = is_f_ind(cells[0], 'Цвет при наличии')
    index_color_off = is_f_ind(cells[0], 'Цвет при отсутствии')
    index_fracdig = is_f_ind(cells[0], 'Число знаков')
    index_drv = is_f_ind(cells[0], 'Драйвер')
    index_save_history = is_f_ind(cells[0], 'Сохранять в истории')

    cells = sheet['A2': get_column_letter(50) + str(sheet.max_row)]
    # return_sl_cpu_drv = {cpu: {(Драйвер, рус имя драйвера):
    # {алг.пар: (Тип переменной в студии, рус имя, тип сообщения, цвет отключения, цвет включения,
    # ед.измер, кол-во знаков, Сохраняемый - Да/Нет, кол-во знаков для истории) }}}
    return_sl_cpu_drv = {}
    # return_ios_drv = {(Драйвер, рус имя драйвера): {cpu:
    # {алг.пар: (Тип переменной в студии, рус имя, тип сообщения, цвет отключения, цвет включения,
    # ед.измер, кол-во знаков) }}}
    return_ios_drv = {}
    # sl_cpu_drv_signal = {cpu: {Драйвер: (кортеж переменных)}}
    sl_cpu_drv_signal = {}
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        # Если указанный драйвер есть в словаре объявленных драйверов, то обрабатываем
        if par[index_drv].value in sl_all_drv:
            set_par_cpu.add(par[index_cpu_name].value)
            # Получаем тип переменной (нужно для удобного отсечения и дальнейшего использования)
            type_sig_par = par[index_type_sig].value.replace(' (с имитацией)', '')  # учесть тип имитации!!!

            # Если в словаре sl_cpu_drv_signal нет инфы по cpu, то создаём для него внутренний пустой словарь
            if par[index_cpu_name].value not in sl_cpu_drv_signal:
                sl_cpu_drv_signal[par[index_cpu_name].value] = {}
            # Если в sl_cpu_drv_signal[cpu] нет инфы по драйверу, то создаём для него внутренний кортеж
            if par[index_drv].value not in sl_cpu_drv_signal[par[index_cpu_name].value]:
                sl_cpu_drv_signal[par[index_cpu_name].value][par[index_drv].value] = ()
            sl_cpu_drv_signal[par[index_cpu_name].value][par[index_drv].value] += (par[index_alg_name].value,)

            if par[index_cpu_name].value not in return_sl_cpu_drv:
                return_sl_cpu_drv[par[index_cpu_name].value] = {}

            if (par[index_drv].value, sl_all_drv.get(par[index_drv].value)) \
                    not in return_sl_cpu_drv[par[index_cpu_name].value]:
                return_sl_cpu_drv[par[index_cpu_name].value][(par[index_drv].value,
                                                              sl_all_drv.get(par[index_drv].value))] = {}
            if (par[index_drv].value, sl_all_drv.get(par[index_drv].value)) not in return_ios_drv:
                return_ios_drv[(par[index_drv].value, sl_all_drv.get(par[index_drv].value))] = {}

            if par[index_cpu_name].value \
                    not in return_ios_drv[(par[index_drv].value, sl_all_drv.get(par[index_drv].value))]:
                return_ios_drv[(par[index_drv].value,
                                sl_all_drv.get(par[index_drv].value))][par[index_cpu_name].value] = {}

            type_sig_in_tuple = sl_type_drv.get(type_sig_par, 'Types.').replace('Types.', '')
            type_msg_in_tuple = (par[index_type_msg].value if type_sig_par == 'BOOL' else '-')
            c_off_in_tuple = (sl_color_di.get(par[index_color_off].fill.start_color.index)
                              if type_sig_par == 'BOOL' else '0')
            c_on_in_tuple = (sl_color_di.get(par[index_color_on].fill.start_color.index)
                             if type_sig_par == 'BOOL' else '0')
            unit_in_tuple = (par[index_unit].value if type_sig_par != 'BOOL' else '-')
            fracdig_in_tuple = (par[index_fracdig].value if type_sig_par in ('FLOAT', 'IECR', 'IEC') else '0')
            history_in_tuple = f'Сохраняемый - {par[index_save_history].value}'
            frag_dig_hist_in_tuple = ''.join(
                [i for i in str(par[index_fracdig].comment)[:str(par[index_fracdig].comment).find('by')]
                 if i.isdigit()]) if par[index_fracdig].comment else par[index_fracdig].value

            tuple_par = (type_sig_in_tuple, par[index_rus_name].value, type_msg_in_tuple,
                         c_off_in_tuple, c_on_in_tuple, unit_in_tuple, fracdig_in_tuple, history_in_tuple,
                         frag_dig_hist_in_tuple)

            return_sl_cpu_drv[par[index_cpu_name].value][(par[index_drv].value, sl_all_drv.get(par[index_drv].value))][
                par[index_alg_name].value] = tuple_par

            return_ios_drv[(par[index_drv].value,
                            sl_all_drv.get(par[index_drv].value))][par[index_cpu_name].value][
                par[index_alg_name].value] = tuple_par

    return sl_cpu_drv_signal, return_sl_cpu_drv, return_ios_drv


def is_read_create_grh(sheet, sl_object_all):
    # Считываем файл-шаблон для дополнительных параметров алгоритма (нужен fracdig)

    # Словарь типов ПЛК-аспектов для алгоритмических переменных
    sl_type_alogritm = {
        'BOOL': 'Types.GRH.GRH_BOOL_PLC_View',
        'INT': 'Types.GRH.GRH_INT_PLC_View',
        'FLOAT': 'Types.GRH.GRH_FLOAT_PLC_View'
    }
    cells = sheet['A1': 'A' + str(sheet.max_row)]

    # словарь по cpu sl_alg_in_cpu = {cpu: sl_algoritm}
    sl_alg_in_cpu = {}
    # словарь команд по cpu sl_command_in_cpu = {cpu: sl_command}
    # sl_command = {(Режим_alg, русское имя режима): {номер шага: {команда_alg: русский текст команды}}}
    sl_command_in_cpu = {}

    # словарь режимов(в том числе и подрежимов),
    # sl_mod_cpu = {cpu: кортеж режимов(в том числе и подрежимов)-(содержит кортеж (алг, рус)}
    sl_mod_cpu = {}

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # ...заполняем общий словарь по контроллерам
            sl_alg_in_cpu[cpu], sl_command_in_cpu[cpu], sl_mod_cpu[cpu] = is_load_algoritm(
                controller=cpu, cells=cells, sheet=sheet)

    # Из функции возвращаяем словарь где ключ - cpu, а значение - кортеж переменных GRH
    # Также возвращаем словарь вида {cpu: {алг_пар: (тип переменной в студии, русское имя,
    # количество знаков, если есть)}}
    sl_ = dict(zip(sl_alg_in_cpu.keys(), [tuple(value.keys()) for value in sl_alg_in_cpu.values()]))
    # {cpu: {alg_par.replace('GRH|', ''): (
    #         sl_type_alogritm[val[1]].lstrip('Types.'), val[0]) for alg_par, val in value.items()}
    #         for cpu, value in sl_alg_in_cpu.items() if value}
    return {key: value for key, value in sl_.items() if value}, \
           {cpu: {alg_par.split('|')[1]: (sl_type_alogritm.get(val[1]).replace('Types.', ''), val[0]) +
                                         (tuple(val[2]) if len(val) == 3 else tuple())
                  for alg_par, val in value.items()}
            for cpu, value in sl_alg_in_cpu.items() if value}, \
           {key: value for key, value in sl_command_in_cpu.items() if value}, sl_mod_cpu


def check_diff_file(check_path, file_name_check, new_data, message_print):
    # Если в целевой(указанной) папке уже есть формируемый файл
    if os.path.exists(os.path.join(check_path, file_name_check)):
        # считываем имеющейся файл
        with open(os.path.join(check_path, file_name_check), 'r', encoding='UTF-8') as f_check:
            old_data = f_check.read()
        # Если отличаются
        if new_data != old_data:
            # Если нет папки Old, то создаём её
            if not os.path.exists(os.path.join(check_path, 'Old')):
                os.mkdir(os.path.join(check_path, 'Old'))
            # Переносим старую файл в папку Old
            os.replace(os.path.join(check_path, file_name_check),
                       os.path.join(check_path, 'Old', file_name_check))
            sleep(0.5)
            # Записываем новый файл
            with open(os.path.join(check_path, file_name_check), 'w', encoding='UTF-8') as f_wr:
                f_wr.write(new_data)
            # пишем, что надо заменить
            print(message_print)
            with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
                f_change.write(f'{datetime.datetime.now()} - {message_print}\n')
    # Если в целевой(указанной) папке нет формируемого файла, то создаём его и пишем, что заменить
    else:
        with open(os.path.join(check_path, file_name_check), 'w', encoding='UTF-8') as f_wr:
            f_wr.write(new_data)
        print(message_print)
        with open('Required_change.txt', 'a', encoding='UTF-8') as f_change:
            f_change.write(f'{datetime.datetime.now()} - {message_print}\n')


# Функция для индексов
# Функция получения алгоритмического имени в нижнем регистре (вместе с разделителем |, если такой есть)
# из строки в словаре Трея
def get_variable_lower(line):
    line = line.split(',')
    if isinstance(line[0], str):
        var = ''.join([i for i in line[0] if i not in '#'])
        return var.lower()
    else:
        return 'Странная переменная'


# Функция для индексов
# Функция получения алгоритмического имени (вместе с разделителем |, если такой есть)
# из строки в словаре Трея
def get_variable(line):
    line = line.split(',')
    if isinstance(line[0], str):
        var = ''.join([i for i in line[0] if i not in '#'])
        return var
    else:
        return 'Странная переменная'


# Функция для замены нескольких значений
def multiple_replace(target_str):
    replace_values = {'\n': ' ', '_x000D_': ''}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str


# функция для поиска индекса нужного столбца
def is_f_ind(cell, name_col, target_count=1):
    count = 1
    for i in range(len(cell)):
        if cell[i].value is None:
            continue
        if multiple_replace(cell[i].value) == name_col:
            if count == target_count:
                return i
            else:
                count += 1
    return 0


def f_ind_json(target_str):
    replace_values = {'\"': '', '\'': ''}
    # получаем заменяемое: подставляемое из словаря в цикле
    for i, j in replace_values.items():
        # меняем все target_str на подставляемое
        target_str = target_str.replace(i, j)
    return target_str
