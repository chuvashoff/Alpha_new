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

    cells = sheet['A2': 'AG' + str(sheet.max_row)]
    # Соствялем множество контроллеров, у которых есть измеряемые параметры
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
            with open(f'file_out_plc_{cpu_name_par}_{objects[2]}.omx-export', 'a',
                      encoding='UTF-8') as f:
                f.write(Template(tmp_object_aiaeset).substitute(object_name=alg_par,
                                                                object_type=f'Types.{group_objects}.'
                                                                            f'{group_objects}_PLC_View',
                                                                object_aspect='Types.PLC_Aspect',
                                                                text_description=is_cor_chr(par[index_rus_name].value),
                                                                text_eunit=par[index_unit].value,
                                                                short_name=par[index_short_name].value,
                                                                text_fracdigits=par[index_frag_dig].value))
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
