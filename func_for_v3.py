from my_func import is_f_ind, is_cor_chr
from string import Template


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
                f.write(f'      <ct:object name="{group_objects}" aspect="Types.IOS_Aspect" access-level="public">\n')
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
                f.write(f'      <ct:object name="{group_objects}" aspect="Types.IOS_Aspect" access-level="public">\n')
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
    index_work_time = is_f_ind(cells[0], 'Считать наработку'),
    index_swap = is_f_ind(cells[0], 'Считать перестановки')

    cells = sheet['A2': 'T' + str(sheet.max_row)]
    # Составляем множество контроллеров, у которых есть данные параметры параметры
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
                f.write(f'      <ct:object name="{group_objects}" aspect="Types.IOS_Aspect" access-level="public">\n')
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
                f.write(f'      <ct:object name="{group_objects}" aspect="Types.IOS_Aspect" access-level="public">\n')
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
