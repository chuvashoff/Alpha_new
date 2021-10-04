from my_func import is_f_ind, is_cor_chr
from string import Template
from copy import copy
import os


def write_ai_ae(sheet, sl_object_all, tmp_object_aiaeset, tmp_ios, group_objects):
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
        set_par_cpu.add(par[index_cpu_name].value)

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')
                f.write(f'        <ct:object name="Agregator_Important_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_N_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        alg_par = par[index_alg_name].value.replace('|', '_')
        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект, если канал не резервный
            if par[index_res].value == 'Нет':
                with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_object_aiaeset).substitute(
                        object_name=alg_par,
                        object_type=f'Types.{group_objects}.{group_objects}_PLC_View',
                        object_aspect='Types.PLC_Aspect',
                        text_description=is_cor_chr(par[index_rus_name].value),
                        text_eunit=par[index_unit].value,
                        short_name=par[index_short_name].value,
                        text_fracdigits=par[index_frag_dig].value))
                # Записываем параметры в IOS-аспект, если канал не резервный
                group_objects_ios = (f'System.{group_objects}' if group_objects == 'SET' else group_objects)
                with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_ios).substitute(
                        object_name=alg_par,
                        object_type=f'Types.{group_objects}.{group_objects}_IOS_View',
                        object_aspect='Types.IOS_Aspect',
                        original_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}",
                        target_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}"))

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        # Если в контроллерах объекта есть параметры загруженного листа
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')


def write_di(sheet, sl_object_all, tmp_object_di, tmp_ios, group_objects):
    # Словарь соответствия цветов и его идентификатора в Альфе
    sl_color_di = {'FF969696': '0', 'FF00B050': '1', 'FFFFFF00': '2', 'FFFF0000': '3'}
    # Словарь соответствия типа сигнала(DI или DI_AI) и его ПЛК-Аспекта
    sl_plc_aspect = {'Да': 'Types.DI.DI_PLC_View', 'Нет': 'Types.DI.DI_PLC_View', 'AI': 'Types.DI_AI.DI_AI_PLC_View'}

    cells = sheet['A1': 'AC' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_im = is_f_ind(cells[0], 'ИМ')
    index_color_on = is_f_ind(cells[0], 'Цвет при наличии')
    index_color_off = is_f_ind(cells[0], 'Цвет при отсутствии')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_res = is_f_ind(cells[0], 'Резервный')
    index_control_cel = is_f_ind(cells[0], 'Контроль цепи')

    cells = sheet['A2': 'AC' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    set_par_cpu = set()
    for par in cells:
        set_par_cpu.add(par[index_cpu_name].value)

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')
                f.write(f'        <ct:object name="Agregator_Important_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_N_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        alg_par = par[index_alg_name].value.replace('|', '_')
        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект
            # при условии, что сигнал не переведён в резерв и не принадлежит ИМу
            if par[index_res].value == 'Нет' and par[index_im].value == 'Нет':
                with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_object_di).substitute(
                        object_name=alg_par,
                        object_type=sl_plc_aspect.get(par[index_control_cel].value),
                        object_aspect='Types.PLC_Aspect',
                        text_description=is_cor_chr(par[index_rus_name].value),
                        color_on=sl_color_di.get(par[index_color_on].value, '404'),
                        color_off=sl_color_di.get(par[index_color_off].value, '404')))
                # Записываем параметры в IOS-аспект
                with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_ios).substitute(object_name=alg_par,
                                                         object_type=f'Types.{group_objects}.{group_objects}_IOS_View',
                                                         object_aspect='Types.IOS_Aspect',
                                                         original_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                                                         f".CPU.Tree.{group_objects}.{alg_par}",
                                                         target_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                                                       f".CPU.Tree.{group_objects}.{alg_par}"))
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        # Если в контроллерах объекта есть параметры загруженного листа
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')


def write_im(sheet, sheet_imao, sl_object_all, tmp_object_im, tmp_ios, group_objects):
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
        set_par_cpu.add(par[index_cpu_name].value)
        # Если считаем наработку, то добавляем в словарь sl_cnt = {CPU: {алг.имя : русское имя}}
        if par[index_work_time].value == 'Да':
            if par[index_cpu_name].value not in sl_cnt:
                sl_cnt[par[index_cpu_name].value] = {par[index_alg_name].value + '_WorkTime': par[index_rus_name].value}
            else:
                sl_cnt[par[index_cpu_name].value].update(
                    {par[index_alg_name].value + '_WorkTime': par[index_rus_name].value})
        # Если считаем перестановки, то добавляем в словарь sl_cnt = {CPU: {алг.имя : русское имя}}
        if par[index_swap].value == 'Да':
            if par[index_cpu_name].value not in sl_cnt:
                sl_cnt[par[index_cpu_name].value] = {par[index_alg_name].value + '_Swap': par[index_rus_name].value}
            else:
                sl_cnt[par[index_cpu_name].value].update(
                    {par[index_alg_name].value + '_Swap': par[index_rus_name].value})

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')
                f.write(f'        <ct:object name="Agregator_Important_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_N_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        alg_par = par[index_alg_name].value
        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект
            with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_object_im).substitute(
                    object_name=alg_par,
                    object_type='Types.' + sl_im_plc.get(par[index_type_im].value),
                    object_aspect='Types.PLC_Aspect',
                    text_description=par[index_rus_name].value,
                    gender=sl_gender.get(par[index_gender].value),
                    start_view=par[19].value[0]))
            # Записываем параметры в IOS-аспект
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_ios).substitute(
                    object_name=alg_par,
                    object_type=f"Types.{sl_im_plc.get(par[index_type_im].value).replace('PLC_View', 'IOS_View')}",
                    object_aspect='Types.IOS_Aspect',
                    original_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                    f".CPU.Tree.{group_objects}.{alg_par}",
                    target_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                  f".CPU.Tree.{group_objects}.{alg_par}"))

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
        set_par_cpu_imao.add(par[index_cpu_name].value)

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu not in set_par_cpu and cpu in set_par_cpu_imao:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if not (set(sl_object_all[objects].keys()) & set_par_cpu) and \
                set(sl_object_all[objects].keys()) & set_par_cpu_imao:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')
                f.write(f'        <ct:object name="Agregator_Important_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_N_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        alg_par = par[index_alg_name].value
        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект
            # При условии, что это ИМ и не выделен как резервный
            if par[index_yes_im].value == 'Да' and par[index_res].value == 'Нет':
                with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_object_im).substitute(
                        object_name=alg_par,
                        object_type='Types.' + sl_im_plc.get('ИМАО'),
                        object_aspect='Types.PLC_Aspect',
                        text_description=par[index_rus_name].value,
                        gender=sl_gender.get(par[index_gender].value),
                        start_view=par[index_type_im].value[0]))
                # Записываем параметры в IOS-аспект
                with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(Template(tmp_ios).substitute(
                        object_name=alg_par,
                        object_type=f"Types.{sl_im_plc.get('ИМАО').replace('PLC_View', 'IOS_View')}",
                        object_aspect='Types.IOS_Aspect',
                        original_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                        f".CPU.Tree.{group_objects}.{alg_par}",
                        target_object=f"PLC_{cpu_name_par}_{objects[2]}"
                                      f".CPU.Tree.{group_objects}.{alg_par}"))
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu or cpu in set_par_cpu_imao:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        # Если в контроллерах объекта есть параметры загруженного листа
        if set(sl_object_all[objects].keys()) & set_par_cpu or set(sl_object_all[objects].keys()) & set_par_cpu_imao:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')
    return sl_cnt


def is_create_objects_diag(sl):
    # Считываем файлы-шаблоны для диагностики модулей
    with open(os.path.join('Template', 'Temp_m547a'), 'r', encoding='UTF-8') as f:
        tmp_m547a = f.read()
    with open(os.path.join('Template', 'Temp_m537v_m932c_2n'), 'r', encoding='UTF-8') as f:
        tmp_m537v = f.read()
    with open(os.path.join('Template', 'Temp_m557d_m557o'), 'r', encoding='UTF-8') as f:
        tmp_m557d = f.read()
    with open(os.path.join('Template', 'Temp_cpu'), 'r', encoding='UTF-8') as f:
        template_text_cpu = f.read()

    sl_modules_temp = {
        'M547A': tmp_m547a,
        'M537V': tmp_m537v,
        'M557D': tmp_m557d,
        'M557O': tmp_m557d,
        'M932C_2N': tmp_m537v,
        'M548A': tmp_m547a,
        'M538V': tmp_m537v,
        'M558D': tmp_m557d,
        'M558O': tmp_m557d,
        'M531I': tmp_m537v,
        'M543G': tmp_m547a
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
    tmp_line_object = ''
    for key, value in sl.items():
        if value[0] in ('M903E', 'M991E', 'M915E', 'M501E'):
            tmp_line_object += Template(template_text_cpu).substitute(object_name=key,
                                                                      object_type=sl_type_modules[value[0]],
                                                                      object_aspect='Types.PLC_Aspect',
                                                                      text_description=f'Диагностика мастер-модуля '
                                                                                       f'{key} ({value[0]})',
                                                                      short_name=key)
        elif value[0] in ('M547A', 'M548A', 'M543G'):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля '
                                                                                               f'{key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7],
                                                                              Channel_9=value[1][8],
                                                                              Channel_10=value[1][9],
                                                                              Channel_11=value[1][10],
                                                                              Channel_12=value[1][11],
                                                                              Channel_13=value[1][12],
                                                                              Channel_14=value[1][13],
                                                                              Channel_15=value[1][14],
                                                                              Channel_16=value[1][15])
        elif value[0] in ('M537V', 'M932C_2N', 'M538V', 'M531I'):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля '
                                                                                               f'{key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7])
        elif value[0] in ('M557D', 'M557O', 'M558D', 'M558O'):
            tmp_line_object += Template(sl_modules_temp[value[0]]).substitute(object_name=key,
                                                                              object_type=sl_type_modules[value[0]],
                                                                              object_aspect='Types.PLC_Aspect',
                                                                              text_description=f'Диагностика модуля '
                                                                                               f'{key} ({value[0]})',
                                                                              short_name=key,
                                                                              Channel_1=value[1][0],
                                                                              Channel_2=value[1][1],
                                                                              Channel_3=value[1][2],
                                                                              Channel_4=value[1][3],
                                                                              Channel_5=value[1][4],
                                                                              Channel_6=value[1][5],
                                                                              Channel_7=value[1][6],
                                                                              Channel_8=value[1][7],
                                                                              Channel_9=value[1][8],
                                                                              Channel_10=value[1][9],
                                                                              Channel_11=value[1][10],
                                                                              Channel_12=value[1][11],
                                                                              Channel_13=value[1][12],
                                                                              Channel_14=value[1][13],
                                                                              Channel_15=value[1][14],
                                                                              Channel_16=value[1][15],
                                                                              Channel_17=value[1][16],
                                                                              Channel_18=value[1][17],
                                                                              Channel_19=value[1][18],
                                                                              Channel_20=value[1][19],
                                                                              Channel_21=value[1][20],
                                                                              Channel_22=value[1][21],
                                                                              Channel_23=value[1][22],
                                                                              Channel_24=value[1][23],
                                                                              Channel_25=value[1][24],
                                                                              Channel_26=value[1][25],
                                                                              Channel_27=value[1][26],
                                                                              Channel_28=value[1][27],
                                                                              Channel_29=value[1][28],
                                                                              Channel_30=value[1][29],
                                                                              Channel_31=value[1][30],
                                                                              Channel_32=value[1][31])
    return tmp_line_object.rstrip()


def write_diag(book, sl_object_all, tmp_ios, *sheets_signal):
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
    sl_type_modules_ios = {
        'M903E': 'Types.DIAG_CPU.DIAG_CPU_M903E_IOS_View',
        'M991E': 'Types.DIAG_CPU.DIAG_CPU_M991E_IOS_View',
        'M547A': 'Types.DIAG_M547A.DIAG_M547A_IOS_View',
        'M548A': 'Types.DIAG_M548A.DIAG_M548A_IOS_View',
        'M537V': 'Types.DIAG_M537V.DIAG_M537V_IOS_View',
        'M538V': 'Types.DIAG_M538V.DIAG_M538V_IOS_View',
        'M932C_2N': 'Types.DIAG_M932C_2N.DIAG_M932C_2N_IOS_View',
        'M557D': 'Types.DIAG_M557D.DIAG_M557D_IOS_View',
        'M558D': 'Types.DIAG_M558D.DIAG_M558D_IOS_View',
        'M557O': 'Types.DIAG_M557O.DIAG_M557O_IOS_View',
        'M558O': 'Types.DIAG_M558O.DIAG_M558O_IOS_View',
        'M915E': 'Types.DIAG_CPU.DIAG_CPU_M915E_IOS_View',
        'M501E': 'Types.DIAG_CPU.DIAG_CPU_M501E_IOS_View',
        'M531I': 'Types.DIAG_M531I.DIAG_M531I_IOS_View',
        'M543G': 'Types.DIAG_M543G.DIAG_M543G_IOS_View'
    }
    cells = sheet_module['A1': 'G' + str(sheet_module.max_row)]
    type_module_index = is_f_ind(cells[0], 'Шифр модуля')
    name_module_index = is_f_ind(cells[0], 'Имя модуля')
    cpu_index = is_f_ind(cells[0], 'CPU')
    cells = sheet_module['A2': 'G' + str(sheet_module.max_row)]
    sl_modules_cpu = {}
    # словарь sl_modules_cpu {имя CPU: (имя модуля, [каналы])}
    for p in cells:
        if p[0].value is None:
            break
        aa = copy(sl_modules[p[type_module_index].value])
        if p[cpu_index].value not in sl_modules_cpu:
            sl_modules_cpu[p[cpu_index].value] = {p[name_module_index].value: (p[type_module_index].value, aa)}
        else:
            sl_modules_cpu[p[cpu_index].value].update({p[name_module_index].value: (p[type_module_index].value, aa)})

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
                    is_cor_chr(par[name_par_index].value)
            # если выбран контроль цепи и контроль стандартный, то также добавляем в список
            if par[control_index].value == 'Да' and par[no_stand_kc_index].value == 'Нет':
                tmp_ind = int(par[num_canal_kc_index].value) - 1
                sl_modules_cpu[par[cpu_par_index].value][par[name_module_par_kc_index].value][1][tmp_ind] = \
                    f"КЦ: {is_cor_chr(par[name_par_index].value)}"

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('        <ct:object name="Diag" access-level="public" >\n')
                f.write('          <ct:object name="HW" access-level="public" >\n')

        # Записываем стартовую информацию IOS-аспекта для диагностики
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            # узел Diag
            f.write(f'      <ct:object name="Diag" access-level="public">\n')
            f.write(f'        <ct:object name="Agregator_Important_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'        <ct:object name="Agregator_N_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            # подузел HW
            f.write(f'        <ct:object name="HW" access-level="public">\n')
            f.write(f'          <ct:object name="Agregator_Important_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'          <ct:object name="Agregator_LessImportant_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'          <ct:object name="Agregator_N_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
            f.write(f'          <ct:object name="Agregator_Repair_IOS" '
                    f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                    f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    '''
    for cpu in sl_modules_cpu:
        print(is_create_objects_diag(sl=sl_modules_cpu[cpu]))
    '''
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем модуля в ПЛК-аспект
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(is_create_objects_diag(sl=sl_modules_cpu[cpu]) + '\n')
            # Записываем параметры в IOS-аспект
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                for module in sl_modules_cpu[cpu]:
                    f.write(Template(tmp_ios).substitute(
                        object_name=module,
                        object_type=sl_type_modules_ios[sl_modules_cpu[cpu][module][0]],
                        object_aspect='Types.IOS_Aspect',
                        original_object=f"PLC_{cpu}_{objects[2]}.CPU.Tree.Diag.HW.{module}",
                        target_object=f"PLC_{cpu}_{objects[2]}.CPU.Tree.Diag.HW.{module}"))

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                # Закрываем узел HW
                f.write('          </ct:object>\n')
                # Закрываем узел Diag
                f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            # Закрываем узел HW
            f.write('        </ct:object>\n')
            # Закрываем узел Diag
            f.write('      </ct:object>\n')


def write_btn(sheet, sl_object_all, tmp_object_btn_cnt_sig, tmp_ios, group_objects):
    cells = sheet['A1': 'C' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')

    cells = sheet['A2': 'C' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры
    set_par_cpu = set()
    for par in cells:
        set_par_cpu.add(par[index_cpu_name].value)

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')

    # Для каждого параметра на листе ...
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        alg_par = 'BTN_' + par[index_alg_name].value[par[index_alg_name].value.find('|')+1:]
        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект, если канал не резервный
            with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_object_btn_cnt_sig).substitute(
                    object_name=alg_par,
                    object_type='Types.BTN.BTN_PLC_View',
                    object_aspect='Types.PLC_Aspect',
                    text_description=is_cor_chr(par[index_rus_name].value)))
            # Записываем параметры в IOS-аспект, если канал не резервный
            group_objects_ios = f'System.{group_objects}'
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_ios).substitute(
                    object_name=alg_par,
                    object_type=f'Types.{group_objects}.{group_objects}_IOS_View',
                    object_aspect='Types.IOS_Aspect',
                    original_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}",
                    target_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}"))

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        # Если в контроллерах объекта есть параметры загруженного листа
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')


def write_pz(sheet, sl_object_all, tmp_object_pz, tmp_ios, group_objects):
    cells = sheet['A1': 'N' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')

    cells = sheet['A2': 'N' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть данные параметры
    set_par_cpu = set()
    for par in cells:
        set_par_cpu.add(par[index_cpu_name].value)

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Записываем стартовую информацию группы параметров
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{group_objects}" access-level="public" >\n')
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{group_objects}" access-level="public">\n')
                f.write(f'        <ct:object name="Agregator_Important_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Important_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_LessImportant_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_LessImportant_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_N_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_N_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')
                f.write(f'        <ct:object name="Agregator_Repair_IOS" '
                        f'base-type="Types.MSG_Agregator.Agregator_Repair_IOS" '
                        f'aspect="Types.IOS_Aspect" access-level="public"/>\n')

    # Для каждого параметра на листе ...
    num_pz = 0
    for par in cells:
        # Узнаём к какому контроллеру принадлежит параметр
        cpu_name_par = par[index_cpu_name].value
        # Если встретили пустую строку, то прервываем
        if cpu_name_par is None:
            break
        if par[index_type_protect].value not in 'АОссАОбсВОссВОбсАОНО':
            continue
        else:
            if par[index_unit].value == '-999.0':
                tmp_eunit = str(par[index_unit].comment)[str(par[index_unit].comment).find(' ')+1:
                                                         str(par[index_unit].comment).find('by')]
            else:
                tmp_eunit = par[index_unit].value
        alg_par = 'A' + str(num_pz).zfill(3)

        # ...для каждого объекта...
        for objects in sl_object_all:
            # Записываем параметры в нужный файл PLC-аспект, если канал не резервный
            with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_object_pz).substitute(
                    object_name=alg_par,
                    object_type='Types.PZ.PZ_PLC_View',
                    object_aspect='Types.PLC_Aspect',
                    text_description=is_cor_chr(par[index_rus_name].value),
                    text_eunit=tmp_eunit.strip()))
            # Записываем параметры в IOS-аспект
            group_objects_ios = f'System.{group_objects}'
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(Template(tmp_ios).substitute(
                    object_name=alg_par,
                    object_type=f'Types.{group_objects}.{group_objects}_IOS_View',
                    object_aspect='Types.IOS_Aspect',
                    original_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}",
                    target_object=f"PLC_{cpu_name_par}_{objects[2]}.CPU.Tree.{group_objects_ios}.{alg_par}"))
        num_pz += 1

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов
            # При условии, что у данного котроллера есть параметры загруженного листа
            if cpu in set_par_cpu:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a',
                          encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем в IOS-аспекте
        # Если в контроллерах объекта есть параметры загруженного листа
        if set(sl_object_all[objects].keys()) & set_par_cpu:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')


def write_cnt(sl_cnt, sl_object_all, tmp_object_btn_cnt_sig, tmp_ios, group_objects):
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # В ПЛК-аспекте открываем узел CNT
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('        <ct:object name="СNT" access-level="public" >\n')
                for nar in sl_cnt[cpu]:
                    f.write(Template(tmp_object_btn_cnt_sig).substitute(
                        object_name=nar,
                        object_type='Types.CNT.CNT_PLC_View',
                        object_aspect='Types.PLC_Aspect',
                        text_description=is_cor_chr(sl_cnt[cpu][nar])))
        # В IOS-аспекте открываем узел CNT
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            f.write('      <ct:object name="CNT" access-level="public" >\n')
            for cpu_nar in sl_cnt:
                for nar in sl_cnt[cpu_nar]:
                    f.write(Template(tmp_ios).substitute(
                        object_name=nar,
                        object_type=f'Types.{group_objects}.{group_objects}_IOS_View',
                        object_aspect='Types.IOS_Aspect',
                        original_object=f"PLC_{cpu_nar}_{objects[2]}.CPU.Tree.System.СNT.{nar}",
                        target_object=f"PLC_{cpu_nar}_{objects[2]}.CPU.Tree.System.СNT.{nar}"))

    # Закрываем группу наработок
    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем узел CNT в ПЛК-аспекте
            with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('        </ct:object>\n')
        # Закрываем узел CNT в IOS-аспекте
        with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
            f.write('      </ct:object>\n')


def is_read_sig(controller, cell, alg_name, par_name, type_protect, cpu, return_par):
    tmp_wrn = {}
    tmp_ts = {}
    tmp_ppu = {}
    tmp_alr = {}
    tmp_modes = {}
    tmp_alg = {}
    for par in cell:
        if par[par_name].value is None:
            break
        if par[cpu].value == controller:
            if 'ПС' in par[type_protect].value:
                tmp_wrn[par[alg_name].value[par[alg_name].value.find('|')+1:]] = (is_cor_chr(par[par_name].value),
                                                                                  'Да (по наличию)')
            elif par[type_protect].value in 'АОссАОбсВОссВОбсАОНО' or 'АС' in par[type_protect].value:
                if 'АС' in par[type_protect].value:
                    tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = ('АС. ' +
                                                                                        is_cor_chr(par[par_name].value),
                                                                                        'АС')
                else:
                    tmp_alr[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = (par[type_protect].value + '. ' +
                                                                                        is_cor_chr(par[par_name].value),
                                                                                        'Защита')
            elif 'ТС' in par[type_protect].value:
                tmp_ts[par[alg_name].value[par[alg_name].value.find('|')+1:]] = (is_cor_chr(par[par_name].value), 'ТС')
            elif par[type_protect].value in ('ГР', 'ХР'):
                tmp_ppu[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = (is_cor_chr(par[par_name].value),
                                                                                    'ППУ')
            elif 'Режим' in par[type_protect].value:
                tmp_modes[par[alg_name].value[par[alg_name].value.find('|') + 1:]] = ('Режим &quot;' +
                                                                                      is_cor_chr(par[par_name].value) +
                                                                                      '&quot;', 'Режим')
                tmp_modes['regNum'] = ['Номер режима', 'Номер режима']
            elif par[type_protect].value in ['BOOL', 'INT', 'FLOAT']:
                tmp_alg['_'.join(par[alg_name].value.split('|'))] = (is_cor_chr(par[par_name].value),
                                                                     'ALG_' + par[type_protect].value)
    if return_par == 'WRN':
        return tmp_wrn
    elif return_par == 'TS':
        return tmp_ts
    elif return_par == 'PPU':
        return tmp_ppu
    elif return_par == 'ALR':
        return tmp_alr
    elif return_par == 'MODES':
        return tmp_modes
    elif return_par == 'ALG':
        return tmp_alg


def write_one_signal(write_par, sl_object_all, cells, index_alg_name, index_rus_name, index_type_protect,
                     index_cpu_name, tmp_object_btn_cnt_sig, tmp_ios, sl_type_sig, sl_set_par_cpu):
    # Словарь соответствия английского и русского наименования группы сигналов
    sl_rus_ = {'TS': 'ТС', 'PPU': 'ППУ'}
    # Для каждого объекта...
    for objects in sl_object_all:
        # Записываем стартовую информацию IOS-аспекта для группы параметров
        # При условии, что есть пересечение между множеством контроллеров с параметрами и контроллеров в данном объекте,
        # то есть наличие данные параметров у объектов
        if set(sl_object_all[objects].keys()) & sl_set_par_cpu[sl_rus_[write_par]]:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write(f'      <ct:object name="{write_par}" access-level="public">\n')

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # ...вызываем функцию чтения параметров-сигналов
            tmp_sig = is_read_sig(return_par=write_par,
                                  controller=cpu,
                                  cell=cells, alg_name=index_alg_name,
                                  par_name=index_rus_name,
                                  type_protect=index_type_protect,
                                  cpu=index_cpu_name)
            # Если в котроллере есть сигналы...
            if tmp_sig:
                # ...то открываем группу сигналов в ПЛК-аспекте
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write(f'        <ct:object name="{write_par}" access-level="public" >\n')
                    # для каждого сигнала в текущем контроллере прописываем структуру ПЛК-аспекта
                    for sig, value in tmp_sig.items():
                        f.write(Template(tmp_object_btn_cnt_sig).substitute(object_name=sig,
                                                                            object_type=sl_type_sig[value[1]],
                                                                            object_aspect='Types.PLC_Aspect',
                                                                            text_description=value[0]))

                # В IOS-аспекте
                with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                    for sig, value in tmp_sig.items():
                        f.write(Template(tmp_ios).substitute(
                            object_name=sig,
                            object_type=sl_type_sig[value[1]].replace('PLC_View', 'IOS_View'),
                            object_aspect='Types.IOS_Aspect',
                            original_object=f"PLC_{cpu}_{objects[2]}.CPU.Tree.System.{write_par}.{sig}",
                            target_object=f"PLC_{cpu}_{objects[2]}.CPU.Tree.System.{write_par}.{sig}"))

    # Для каждого объекта...
    for objects in sl_object_all:
        # ...для каждого контроллера...
        for cpu in sl_object_all[objects]:
            # Закрываем группу объектов в ПЛК-аспекте
            # При условии, что у данного котроллера есть нужные сигналы
            if set(sl_object_all[objects].keys()) & sl_set_par_cpu[sl_rus_[write_par]]:
                with open(f'file_out_plc_{cpu}_{objects[2]}.omx-export', 'a', encoding='UTF-8') as f:
                    f.write('        </ct:object>\n')
        # Закрываем группу в IOS-аспекте
        if set(sl_object_all[objects].keys()) & sl_set_par_cpu[sl_rus_[write_par]]:
            with open(f'file_out_IOS_inApp_{objects[0]}.omx-export', 'a', encoding='UTF-8') as f:
                f.write('      </ct:object>\n')


def write_signal(sheet, sl_object_all, tmp_object_btn_cnt_sig, tmp_ios):
    # Словарь типов ПЛК-аспектов для сигналов
    sl_type_sig = {
        'Да (по наличию)': 'Types.WRN_On.WRN_On_PLC_View',
        'Да (по отсутствию)': 'Types.WRN_Off.WRN_Off_PLC_View',
        'ТС': 'Types.TS.TS_PLC_View',
        'ППУ': 'Types.PPU.PPU_PLC_View',
        'Защита': 'Types.ALR.ALR_PLC_View',
        'АС': 'Types.ALR.ALR_PLC_View',
        'Режим': 'Types.MODES.MODES_PLC_View',
        'Номер режима': 'Types.MODES.regNum_PLC_View',
        'ALG_BOOL': 'Types.ALG.ALG_BOOL_PLC_View',
        'ALG_INT': 'Types.ALG.ALG_INT_PLC_View',
        'ALG_FLOAT': 'Types.ALG.ALG_FLOAT_PLC_View'
    }
    cells = sheet['A1': 'N' + str(sheet.max_row)]
    index_alg_name = is_f_ind(cells[0], 'Алгоритмическое имя')
    index_rus_name = is_f_ind(cells[0], 'Наименование параметра')
    index_cpu_name = is_f_ind(cells[0], 'CPU')
    index_type_protect = is_f_ind(cells[0], 'Тип защиты')
    index_unit = is_f_ind(cells[0], 'Единица измерения')

    cells = sheet['A2': 'N' + str(sheet.max_row)]

    # Соствялем множество контроллеров, у которых есть данные параметры параметры
    # Составляем словарь, где ключ - возможный тип сигнала(защиты), а значение - множество контроллеров
    # Для защит ХР ГР объединяем в ППУ
    sl_set_par_cpu = {}
    for par in cells:
        if par[index_type_protect].value not in sl_set_par_cpu:
            if par[index_type_protect].value in ('ХР', 'ГР'):
                sl_set_par_cpu['ППУ'] = set()
            else:
                sl_set_par_cpu[par[index_type_protect].value] = set()
        if par[index_type_protect].value in ('ХР', 'ГР'):
            sl_set_par_cpu['ППУ'].add(par[index_cpu_name].value)
        else:
            sl_set_par_cpu[par[index_type_protect].value].add(par[index_cpu_name].value)

    write_one_signal(write_par='TS', sl_object_all=sl_object_all, cells=cells,
                     index_alg_name=index_alg_name, index_rus_name=index_rus_name,
                     index_type_protect=index_type_protect, index_cpu_name=index_cpu_name,
                     tmp_object_btn_cnt_sig=tmp_object_btn_cnt_sig,
                     tmp_ios=tmp_ios, sl_type_sig=sl_type_sig, sl_set_par_cpu=sl_set_par_cpu)

    write_one_signal(write_par='PPU', sl_object_all=sl_object_all, cells=cells,
                     index_alg_name=index_alg_name, index_rus_name=index_rus_name,
                     index_type_protect=index_type_protect, index_cpu_name=index_cpu_name,
                     tmp_object_btn_cnt_sig=tmp_object_btn_cnt_sig,
                     tmp_ios=tmp_ios, sl_type_sig=sl_type_sig, sl_set_par_cpu=sl_set_par_cpu)

