from my_func import is_f_ind, is_cor_chr
from string import Template
from copy import copy
import os
from algroritm import is_load_algoritm
import datetime
from time import sleep
# для тестирования новых возможностей
import xml.etree.ElementTree as ET
import lxml.etree


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
                      'auth_protocol': 'auth-protocol', 'priv_protocol': 'priv-protocol'}
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
                child_par = ET.SubElement(child_group, 'ct_object', name=f"{par}",
                                          base_type=f"Types.{tuple_par[0].replace('PLC_View', 'IOS_View')}",
                                          aspect="Types.IOS_Aspect",
                                          original=f"PLC_{cpu}_{objects[2]}.CPU.Tree.{plc_node_tree}.{par}",
                                          access_level="public")
                ET.SubElement(child_par, 'ct_init-ref',
                              ref="_PLC_View", target=f"PLC_{cpu}_{objects[2]}.CPU.Tree.{plc_node_tree}.{par}")
    return


def is_read_ai_ae_set(sheet):
    # return_sl = {cpu: {алг_пар: (русское имя, ед измер, короткое имя, количество знаков)}}
    return_sl = {}

    cells = sheet['A1': 'AG' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_unit = is_f_ind(cells[0], 'Единицы измерения')
    index_short_name = is_f_ind(cells[0], 'Короткое наименование')
    index_frag_dig = is_f_ind(cells[0], 'Количество знаков')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_res = is_f_ind(cells[0], 'Резервный')

    cells = sheet['A2': 'AG' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        if par[index_res].value == 'Нет':
            if par[index_cpu_name].value not in return_sl:
                # return_sl = {cpu: {алг_пар: (русское имя, ед измер, короткое имя, количество знаков)}}
                return_sl[par[index_cpu_name].value] = {}
            return_sl[par[index_cpu_name].value].update({par[index_alg_name].value.replace('|', '_'): (
                par[index_rus_name].value,
                par[index_unit].value,
                par[index_short_name].value,
                par[index_frag_dig].value)})

    return return_sl


def is_read_di(sheet):
    # return_sl_di = {cpu: {алг_пар: (русское имя, sColorOff, sColorOn)}}
    return_sl_di = {}

    # Словарь соответствия цветов и его идентификатора в Альфе
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    # Словарь соответствия типа сигнала(DI или DI_AI) и его ПЛК-Аспекта
    sl_plc_aspect = {'Да': 'Types.DI.DI_PLC_View', 'Нет': 'Types.DI.DI_PLC_View', 'AI': 'Types.DI_AI.DI_AI_PLC_View'}
    # Словарь предупреждений {CPU : {алг.имя : (рус.имя, тип наличия)}}
    sl_wrn_di = {}

    cells = sheet['A1': 'AC' + str(sheet.max_row)]
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

    cells = sheet['A2': 'AC' + str(sheet.max_row)]
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
                # return_sl_di = {cpu: {алг_пар: (русское имя, sColorOff, sColorOn)}}
                return_sl_di[par[index_cpu_name].value] = {}

            return_sl_di[par[index_cpu_name].value].update(
                {par[index_alg_name].value.replace('|', '_'): (
                    par[index_rus_name].value,
                    sl_color_di.get(par[index_color_off].fill.start_color.index, '404'),
                    sl_color_di.get(par[index_color_on].fill.start_color.index, '404'))})
            # Если есть предупреждение по дискрету и канал не переведён в резерв и не привязан к ИМ
            # то добавляем в словарь предупреждений по дискретам
            if 'Да' in par[index_wrn].value:
                cpu_name_par = par[index_cpu_name].value
                alg_par = par[index_alg_name].value.replace('|', '_')
                sl_wrn_di[cpu_name_par][alg_par] = (is_cor_chr(par[index_wrn_text].value), par[index_wrn].value)

    return return_sl_di, sl_wrn_di


def is_read_im(sheet, sheet_imao):
    # return_sl_im = {cpu: {алг_пар: (русское имя, StartView, Gender)}}
    return_sl_im = {}

    # Словарь соответствия типа ИМ и его ПЛК аспекта
    sl_im_plc = {'ИМ1Х0': 'IM1x0.IM1x0_PLC_View', 'ИМ1Х1': 'IM1x1.IM1x1_PLC_View', 'ИМ1Х2': 'IM1x2.IM1x2_PLC_View',
                 'ИМ2Х2': 'IM2x2.IM2x2_PLC_View', 'ИМ2Х4': 'IM2x2.IM2x4_PLC_View', 'ИМ1Х0и': 'IM1x0.IM1x0_PLC_View',
                 'ИМ1Х1и': 'IM1x1.IM1x1_PLC_View', 'ИМ1Х2и': 'IM1x2.IM1x2_PLC_View', 'ИМ2Х2с': 'IM2x2.IM2x2_PLC_View',
                 'ИМАО': 'IM_AO.IM_AO_PLC_View'}
    # Словарь соответствия рода ИМ и его идентификатора в Альфе
    sl_gender = {'С': '0', 'М': '1', 'Ж': '2'}

    cells = sheet['A1': 'T' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_type_im = is_f_ind(cells[0], 'Тип ИМ')
    index_gender = is_f_ind(cells[0], 'Род')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_work_time = is_f_ind(cells[0], 'Считать наработку')
    index_swap = is_f_ind(cells[0], 'Считать перестановки')

    cells = sheet['A2': 'T' + str(sheet.max_row)]
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
            # return_sl_im = {cpu: {алг_пар: (тип ИМа, русское имя, StartView, Gender)}}
            return_sl_im[par[index_cpu_name].value] = {}
        return_sl_im[par[index_cpu_name].value].update(
            {par[index_alg_name].value: (sl_im_plc.get(par[index_type_im].value),
                                         par[index_rus_name].value, par[19].value[0],
                                         sl_gender.get(par[index_gender].value))})

    # Обрабатываем ИМ АО
    cells = sheet_imao['A1': 'AA' + str(sheet.max_row)]

    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_type_im = is_f_ind(cells[0], 'Тип ИМ')
    index_yes_im = is_f_ind(cells[0], 'ИМ')
    index_gender = is_f_ind(cells[0], 'Род')
    index_res = is_f_ind(cells[0], 'Резервный')
    index_cpu_name = is_f_ind(cells[0], 'CPU')

    cells = sheet_imao['A2': 'AA' + str(sheet.max_row)]
    # Составляем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu_imao = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu_imao.add(par[index_cpu_name].value)
        if par[index_yes_im].value == 'Да' and par[index_res].value == 'Нет':
            if par[index_cpu_name].value not in return_sl_im:
                # return_sl_im = {cpu: {алг_пар: (тип ИМа, русское имя, StartView, Gender)}}
                return_sl_im[par[index_cpu_name].value] = {}
            return_sl_im[par[index_cpu_name].value].update(
                {par[index_alg_name].value: (sl_im_plc.get('ИМАО'),
                                             par[index_rus_name].value, par[index_type_im].value[0],
                                             sl_gender.get(par[index_gender].value))})

    return return_sl_im, sl_cnt


def is_read_create_diag(book, *sheets_signal):
    sheet_module = book['Модули']
    # Словарь возможных модулей со стартовым описанием каналов
    sl_modules = {
        'M547A': ['Резерв'] * 16,
        'M537V': ['Резерв'] * 8,
        'M557D': ['Резерв'] * 32,
        'M557O': ['Резерв'] * 32,
        'M932C_2N': ['Резерв'] * 8,
        'M903E': 'CPU', 'M991E': 'CPU', 'M915E': 'CPU', 'M501E': 'CPU',
        'M548A': ['Резерв'] * 16,
        'M538V': ['Резерв'] * 8,
        'M558D': ['Резерв'] * 32,
        'M558O': ['Резерв'] * 32,
        'M531I': ['Резерв'] * 8,
        'M543G': ['Резерв'] * 16,
        'M5571': ['Резерв'] * 32,
    }
    sl_type_modules = {
        'M903E': 'Types.DIAG_CPU.DIAG_CPU_M903E_PLC_View',
        'M991E': 'Types.DIAG_CPU.DIAG_CPU_M991E_PLC_View',
        'M547A': 'Types.DIAG_M547A.DIAG_M547A_PLC_View',
        'M548A': 'Types.DIAG_M548A.DIAG_M548A_PLC_View',
        'M537V': 'Types.DIAG_M537V.DIAG_M537V_PLC_View',
        'M538V': 'Types.DIAG_M538V.DIAG_M538V_PLC_View',
        'M932C_2N': 'Types.DIAG_M932C_2N.DIAG_M932C_2N_PLC_View',
        'M557D': 'Types.DIAG_M557D.DIAG_M557D_PLC_View',
        'M558D': 'Types.DIAG_M558D.DIAG_M558D_PLC_View',
        'M557O': 'Types.DIAG_M557O.DIAG_M557O_PLC_View',
        'M558O': 'Types.DIAG_M558O.DIAG_M558O_PLC_View',
        'M915E': 'Types.DIAG_CPU.DIAG_CPU_M915E_PLC_View',
        'M501E': 'Types.DIAG_CPU.DIAG_CPU_M501E_PLC_View',
        'M531I': 'Types.DIAG_M531I.DIAG_M531I_PLC_View',
        'M543G': 'Types.DIAG_M543G.DIAG_M543G_PLC_View'
    }
    cells = sheet_module['A1': 'G' + str(sheet_module.max_row)]
    type_module_index = is_f_ind(cells[0], 'Шифр модуля')
    name_module_index = is_f_ind(cells[0], 'Имя модуля')
    cpu_index = is_f_ind(cells[0], 'CPU')
    cells = sheet_module['A2': 'G' + str(sheet_module.max_row)]
    sl_modules_cpu = {}
    # словарь sl_modules_cpu {имя CPU: {имя модуля: (тип модуля, [каналы])}}
    for p in cells:
        if p[0].value is None:
            break
        aa = copy(sl_modules[p[type_module_index].value])
        if p[cpu_index].value not in sl_modules_cpu:
            sl_modules_cpu[p[cpu_index].value] = {}
        sl_modules_cpu[p[cpu_index].value].update({p[name_module_index].value: (p[type_module_index].value, aa)})

    # sl_for_diag - словарь для корректной педечачи для создания индексов
    sl_for_diag = {}
    for name_cpu, value in sl_modules_cpu.items():
        keys_sl_for_diag = [i if value[i][0] not in ('M903E', 'M991E', 'M915E', 'M501E') else 'CPU' for i in value]
        value_sl_for_diag = [value[i][0] if value[i][0] not in ('M903E', 'M991E', 'M915E', 'M501E')
                             else (i, value[i][0]) for i in value]
        sl_for_diag[name_cpu] = dict(zip(keys_sl_for_diag, value_sl_for_diag))

    # пробегаемся по листам, где могут быть указаны каналы модулей
    for jj in sheets_signal:
        sheet_run = book[jj]
        cells_run = sheet_run['A1': 'O' + str(sheet_run.max_row)]
        num_canal_index = is_f_ind(cells_run[0], 'Номер канала')
        no_stand_index = is_f_ind(cells_run[0], 'Нестандартный канал')
        cpu_par_index = is_f_ind(cells_run[0], 'CPU')
        name_module_par_index = is_f_ind(cells_run[0], 'Номер модуля')
        name_par_index = is_f_ind(cells_run[0], 'Наименование параметра')
        control_index = is_f_ind(cells_run[0], 'Контроль цепи')
        no_stand_kc_index = is_f_ind(cells_run[0], 'Нестандартный канал КЦ')
        name_module_par_kc_index = is_f_ind(cells_run[0], 'Номер модуля контроля')
        num_canal_kc_index = is_f_ind(cells_run[0], 'Номер канала контроля')
        cells_run = sheet_run['A2': 'O' + str(sheet_run.max_row)]
        # пробегаемся по параметрам на листе
        for par in cells_run:
            # если не указан НЕстандартный канал, то вносим в список
            if par[no_stand_index].value == 'Нет':
                tmp_ind = int(par[num_canal_index].value) - 1
                sl_modules_cpu[par[cpu_par_index].value][par[name_module_par_index].value][1][tmp_ind] = \
                    par[name_par_index].value
            # если выбран контроль цепи и контроль стандартный, то также добавляем в список
            if par[control_index].value == 'Да' and par[no_stand_kc_index].value == 'Нет':
                tmp_ind = int(par[num_canal_kc_index].value) - 1
                sl_modules_cpu[par[cpu_par_index].value][par[name_module_par_kc_index].value][1][tmp_ind] = \
                    f"КЦ: {par[name_par_index].value}"

    # sl_modules_cpu {имя CPU: {имя модуля: (тип модуля в студии, тип модуля, [каналы])}}
    return {cpu: {mod: (sl_type_modules.get(value[0], 'Types.').replace('Types.', ''), ) + value
                  for mod, value in sl_modules_cpu[cpu].items()}
            for cpu in sl_modules_cpu}, sl_for_diag


def is_create_net(sl_object_all, sheet_net):
    # Проработать в студии IOlogic - настройка в конфигураторе !!!
    cells = sheet_net['A1': 'K' + str(sheet_net.max_row)]

    index_rus_name = is_f_ind(cells[0], 'Наименование юнита')
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_object_name = is_f_ind(cells[0], 'Объект')
    index_type = is_f_ind(cells[0], 'Тип')
    index_ip = is_f_ind(cells[0], 'IP-адрес')
    index_ip_res = is_f_ind(cells[0], 'Резервный IP-адрес')
    index_option = is_f_ind(cells[0], 'Настройка')

    cells = sheet_net['A2': 'K' + str(sheet_net.max_row)]

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
                              file=f'SNMP\{sl_value["Type"]}_map.xml')
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
                            file_name_check=f'file_out_test_NET_{objects[0]}.omx-export',
                            new_data=multiple_replace_xml(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                              pretty_print=True, encoding='unicode')),
                            message_print=f'ТЕСТ Требуется заменить ПЛК-аспект сети объекта {objects[0]}')
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


def is_read_btn(sheet):
    # return_sl = {cpu: {алг_пар: (русское имя, )}}
    return_sl = {}
    cells = sheet['A1': 'C' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')

    cells = sheet['A2': 'C' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
        if par[index_cpu_name].value not in return_sl:
            # return_sl = {cpu: {алг_пар: (русское имя, ед измер, короткое имя, количество знаков)}}
            return_sl[par[index_cpu_name].value] = {}
        return_sl[par[index_cpu_name].value].update({
            'BTN_' + par[index_alg_name].value[par[index_alg_name].value.find('|')+1:]: (par[index_rus_name].value,)})

    return return_sl


def is_read_pz(sheet):

    cells = sheet['A1': 'N' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')

    cells = sheet['A2': 'N' + str(sheet.max_row)]

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
            else:
                tmp_eunit = par[index_unit].value
            # В словарь Защит соответсвтующего контроллера добавляем [алг имя, рус. имя, единицы измерения]
            sl_pz[cpu_name_par] += ([par[index_alg_name].value, par[index_rus_name].value, tmp_eunit],)

    # В словаре защит алгоритмическое имя меняем на A+ номер
    num_pz = 0
    for plc in sl_pz:
        for protect in range(len(sl_pz[plc])):
            sl_pz[plc][protect][0] = 'A' + str(num_pz).zfill(3)
            num_pz += 1

    # Из функции возвращаем словарь, в котором ключ - cpu, значение - кортеж алг. имён A+000 и т.д.
    return_sl_pz = {key: tuple([prot[0] for prot in value]) for key, value in sl_pz.items()}
    # sl_pz_xml = {cpu: {алг_имя(A000): (рус.имя, ед измерения)}}
    sl_pz_xml = {cpu: dict(zip(return_sl_pz[cpu], [tuple(val[1:]) for val in value])) for cpu, value in sl_pz.items()}
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
    cells = sheet['A1': 'N' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')

    cells = sheet['A2': 'N' + str(sheet.max_row)]

    for par in cells:
        if par[index_rus_name].value is None:
            break
        # Если тип защиты есть в словаре типовых сигналов:
        protect = par[index_type_protect].value
        if protect in sl_signal_type:
            if par[index_cpu_name].value not in sl_signal_type[protect]:
                sl_signal_type[protect][par[index_cpu_name].value] = {}
            tuple_update = (f"{protect.replace(' (без условий)','')}. {par[index_rus_name].value}"
                            if protect in 'АОссАОбсВОссВОбс' or 'АС' in protect
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
    return return_ts, return_ppu, return_alr, return_alg, return_wrn, return_modes


def is_read_drv(sheet, sl_all_drv):
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    sl_type_drv = {
        'FLOAT': 'Types.DRV_AI.DRV_AI_PLC_View',
        'INT': 'Types.DRV_INT.DRV_INT_PLC_View',
        'BOOL': 'Types.DRV_DI.DRV_DI_PLC_View'
    }

    cells = sheet['A1': 'N' + str(sheet.max_row)]

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

    cells = sheet['A2': 'N' + str(sheet.max_row)]
    # return_sl_cpu_drv = {cpu: {(Драйвер, рус имя драйвера):
    # {алг.пар: (Тип переменной, рус имя, тип сообщения, цвет отключения, цвет включения, ед.измер, кол-во знаков) }}}
    return_sl_cpu_drv = {}
    # sl_cpu_drv_signal = {cpu: {Драйвер: (кортеж переменных)}}
    sl_cpu_drv_signal = {}
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        if par[0].value is None:
            break
        set_par_cpu.add(par[index_cpu_name].value)
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

        type_sig_in_tuple = sl_type_drv.get(par[index_type_sig].value, 'Types.').replace('Types.', '')
        type_msg_in_tuple = (par[index_type_msg].value if par[index_type_sig].value == 'BOOL' else '-')
        c_off_in_tuple = (sl_color_di.get(par[index_color_off].fill.start_color.index)
                          if par[index_type_sig].value == 'BOOL' else '0')
        c_on_in_tuple = (sl_color_di.get(par[index_color_on].fill.start_color.index)
                         if par[index_type_sig].value == 'BOOL' else '0')
        unit_in_tuple = (par[index_unit].value if par[index_type_sig].value != 'BOOL' else '-')
        fracdig_in_tuple = (par[index_fracdig].value if par[index_type_sig].value == 'FLOAT' else '0')

        tuple_par = (type_sig_in_tuple, par[index_rus_name].value, type_msg_in_tuple,
                     c_off_in_tuple, c_on_in_tuple, unit_in_tuple, fracdig_in_tuple)

        return_sl_cpu_drv[par[index_cpu_name].value][(par[index_drv].value, sl_all_drv.get(par[index_drv].value))][
            par[index_alg_name].value] = tuple_par

    return sl_cpu_drv_signal, return_sl_cpu_drv


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

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # ...заполняем общий словарь по контроллерам
            sl_alg_in_cpu[cpu] = is_load_algoritm(controller=cpu, cells=cells, sheet=sheet)

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
                  for alg_par, val in value.items()} for cpu, value in sl_alg_in_cpu.items() if value}


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
