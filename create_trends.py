from my_func import is_f_ind, f_ind_json
from json import dumps as json_dumps
from func_for_v3 import check_diff_file
import os


def is_create_trends(book, sl_object_all, sl_cpu_spec, sl_all_drv):
    # ТРЕНДЫ- JSON

    # Определение объявленных мнемосхем с листа настроек
    sheet = book['Настройки']
    cells = sheet['A1': 'A' + str(sheet.max_row)]
    tuple_node_trends = tuple()
    for p in cells:
        if p[0].value == 'Наименование мнемосхемы':
            jj = 1
            while sheet[p[0].row][jj].value:
                tuple_node_trends += (sheet[p[0].row][jj].value,)
                jj += 1
    # print(tuple_node_trends)
    # Словарь соответствия листов конфигуратора и имени группы на трендах
    sl_group_trends = {
        'Измеряемые': ('Аналоговые входные', 'AI'),
        'Расчетные': ('Расчетные параметры', 'AE'),
        'Входные': ('Дискретные входные', 'DI'),
        'ИМ': ('Исполнительные механизмы', 'IM'),
        'ИМ(АО)': ('Исполнительные механизмы', 'IM'),
        'Драйвера': ('Сигналы от драйверов', 'System.DRV'),
        'Сигналы': ()
    }
    sl_brk_group_trends = {
        'Измеряемые': ('Отказы аналоговых входных', 'AI'),
        'Расчетные': ('Отказы расчетных параметров', 'AE'),
        'Входные': ('Отказы дискретных входных', 'DI')
    }
    sl_state_im_gender = {
        'Включить': {'М': 'Включен', 'Ж': 'Включена', 'С': 'Включено'},
        'Открыть': {'М': 'Открыт', 'Ж': 'Открыта', 'С': 'Открыто'},
        'Включить_off': {'М': 'Отключен', 'Ж': 'Отключена', 'С': 'Отключено'},
        'Открыть_off': {'М': 'Закрыт', 'Ж': 'Закрыта', 'С': 'Закрыто'}
    }
    sl_antonym = {
        'Открыть': 'Закрыть',
        'Включить': 'Отключить'
    }

    # Для каждого объекта, прочитанного ранее
    for obj in sl_object_all:
        lst_json = []
        # Для каждого листа конфигуратора в словаре групп для трендов(ключи словаря опрделили
        # по объявленным мнемосхемам)
        for list_config in sl_group_trends:
            # для каждой группы создаём словарь с пустыми словарями для каждого узла
            sl_node_trends = {node: {} for node in tuple_node_trends}
            # Создаём словарь возможных типов защит - используем при парсинге листа Сигналы и сборке аварий
            sl_node_alr = {}
            sl_node_modes = {}  # Словарь возможных режимов
            sl_node_drv = {}  # Словарь возможных драйверов
            # Выбираем  текущий лист в качестве активного
            sheet = book[list_config]
            # Устанавливаем Диапазон считывания для первой строки (узнать индексы столбцов)
            cells_name = sheet['A1': 'AG1']
            rus_par_ind = is_f_ind(cells_name[0], 'Наименование параметра')
            alg_name_ind = is_f_ind(cells_name[0], 'Алгоритмическое имя')
            eunit_ind = is_f_ind(cells_name[0], 'Единицы измерения')
            node_name_ind = is_f_ind(cells_name[0], 'Узел')
            eunit_drv_ind = is_f_ind(cells_name[0], 'Единица измерения')
            t_sig_drv_ind = is_f_ind(cells_name[0], 'Тип')
            cpu_par = is_f_ind(cells_name[0], 'CPU')
            name_drv_ind = is_f_ind(cells_name[0], 'Драйвер')

            # Устанавливаем диапазон для чтения параметров
            cells_read = sheet['A2': 'AG' + str(sheet.max_row)]
            # пробегаемся по параметрам листа
            for par in cells_read:
                # Если конец строки, то заканчиваем обработку ячеек
                if par[rus_par_ind].value is None:
                    break
                # при условии, что находимся на листе 'Измеряемые', 'Расчетные' или на Входные и сигнал не привязан к ИМ
                # и параметр принадлежит контроллеру объекта
                if (list_config in ('Измеряемые', 'Расчетные') or
                    list_config == 'Входные' and par[is_f_ind(cells_name[0], 'ИМ')].value == 'Нет') and \
                        par[cpu_par].value in sl_object_all[obj]:
                    # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                    sl_par_trends = {f_ind_json(par[rus_par_ind].value): (par[alg_name_ind].value.replace('|', '_') +
                                                                          '.Value',
                                                                          ('-' if list_config == 'Входные' else
                                                                           par[eunit_ind].value))}
                    # добавляем словарь параметра в словарь узла
                    sl_node_trends[par[node_name_ind].value].update(sl_par_trends)
                # при условии, что парсим лист ИМов
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('ИМ',) and par[cpu_par].value in sl_object_all[obj]:
                    # если 'ИМ1Х0', 'ИМ1Х0и'
                    if par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х0', 'ИМ1Х0и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                        sl_par_trends = \
                            {f'{f_ind_json(par[rus_par_ind].value)}. {move_}': (par[alg_name_ind].value + '.oOn', '-')}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ1Х1', 'ИМ1Х1и'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х1', 'ИМ1Х1и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'.oOn': move_, '.stOn': sl_state_im_gender[move_][gender_]}
                        for par_pref in sl_tmp:
                            # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                            sl_par_trends = \
                                {f"{f_ind_json(par[rus_par_ind].value)}. {sl_tmp[par_pref]}": (par[alg_name_ind].value +
                                                                                               par_pref, '-')}
                            # добавляем словарь параметра в словарь узла
                            sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ1Х2', 'ИМ1Х2и'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х2', 'ИМ1Х2и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'.oOn': move_, '.stOn': sl_state_im_gender[move_][gender_],
                                  '.stOff': sl_state_im_gender[move_ + '_off'][gender_]}
                        for par_pref in sl_tmp:
                            # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                            sl_par_trends = \
                                {f'{f_ind_json(par[rus_par_ind].value)}. {sl_tmp[par_pref]}': (par[alg_name_ind].value +
                                                                                               par_pref, '-')}
                            # добавляем словарь параметра в словарь узла
                            sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ2Х2', 'ИМ2Х2с', 'ИМ2Х4'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ2Х2', 'ИМ2Х2с', 'ИМ2Х4'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'.oOn': move_, '.oOff': sl_antonym[move_],
                                  '.stOn': sl_state_im_gender[move_][gender_],
                                  '.stOff': sl_state_im_gender[move_ + '_off'][gender_]}
                        for par_pref in sl_tmp:
                            # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                            sl_par_trends = \
                                {f'{f_ind_json(par[rus_par_ind].value)}. {sl_tmp[par_pref]}': (par[alg_name_ind].value +
                                                                                               par_pref, '-')}
                            # добавляем словарь параметра в словарь узла
                            sl_node_trends[par[node_name_ind].value].update(sl_par_trends)
                # при условии, что парсим лист ИМ(АО) и выделена как ИМ
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('ИМ(АО)',) and par[is_f_ind(cells_name[0], 'ИМ')].value == 'Да' and \
                        par[cpu_par].value in sl_object_all[obj]:
                    # sl_tmp  промежуточный словарь с возможными префиксами сигналов
                    sl_tmp = {'.Set': 'Задание', '.iPos': 'Положение'}
                    for par_pref in sl_tmp:
                        # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                        sl_par_trends = \
                            {f'{f_ind_json(par[rus_par_ind].value)}. {sl_tmp[par_pref]}': (par[alg_name_ind].value +
                                                                                           par_pref,
                                                                                           par[eunit_ind].value)}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                # при условии, что парсим лист Сигналы
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('Сигналы',) and par[cpu_par].value in sl_object_all[obj]:
                    type_protect = par[is_f_ind(cells_name[0], 'Тип защиты')].value
                    # Если увидели аварию
                    if type_protect in 'АОссАОбсВОссВОбсАОНО':
                        # создаём промежуточный словарь аварии {рус.имя: (алг.имя, единицы измерения - '-')}
                        sl_alr_trends = \
                            {f'{f_ind_json(par[rus_par_ind].value)}': (par[alg_name_ind].value.replace('|', '.') +
                                                                       '.Value', '-')}
                        # если в словаре аварий отсутвует такая авария, то создаём
                        if type_protect not in sl_node_alr:
                            sl_node_alr[type_protect] = sl_alr_trends
                        else:  # иначе обновляем словарь, который есть
                            sl_node_alr[type_protect].update(sl_alr_trends)
                    # Если увидели режим
                    elif type_protect in ('Режим',):
                        # то добавляем в словарь режимов с ключом рус имени аварии : (алг.имя, единицы измерения - '-')
                        sl_node_modes[f_ind_json(par[rus_par_ind].value)] = \
                            (par[alg_name_ind].value.replace('MOD|', '') + '.Value', '-')
                # при условии, что парсим лист Драйверов
                # и параметр принадлежит контроллеру объекта
                # и указанный драйвер переменной есть в объявленных
                elif list_config in ('Драйвера',) and par[cpu_par].value in sl_object_all[obj] \
                        and par[name_drv_ind].value in sl_all_drv:
                    sl_type_unit = {'BOOL': '-', 'INT': par[eunit_drv_ind].value, 'FLOAT': par[eunit_drv_ind].value,
                                    'IEC': '-', 'Daily': '-', 'IECB': '-', 'IECR': par[eunit_drv_ind].value}
                    drv_ = par[is_f_ind(cells_name[0], 'Драйвер')].value
                    # создаём промежуточный словарь сигнала драйвера {рус.имя: (алг.имя, единицы измерения - '-')}
                    sl_drv_trends = \
                        {f'{f_ind_json(par[rus_par_ind].value)}': (f'{drv_}.' + par[alg_name_ind].value + '.Value',
                                                                   sl_type_unit.get(par[t_sig_drv_ind].value, '-'))}
                    # если в словаре драйверов отсутвует такой драйвер, то создаём
                    if drv_ not in sl_node_drv:
                        sl_node_drv[drv_] = sl_drv_trends
                    else:  # иначе обновляем словарь, который есть
                        sl_node_drv[drv_].update(sl_drv_trends)
            # на этапе парсинга листа ИМАО добавляем в тренды АПР
            if list_config == 'ИМ(АО)':
                # создаём множество пересечений контроллеров АПР и контроллеров объекта
                # чтобы далее проверить, не пустое ли оно и в объект загрузить апр
                set_check_apr = set([key for key, value in sl_cpu_spec.items() if 'АПР' in value]) & \
                                set(sl_object_all[obj])
                if 'АПР' in [item for sublist in [i for i in sl_cpu_spec.values() if i] for item in sublist] and \
                        set_check_apr:
                    sl_tmp = {'Set': 'Задание', 'Pos': 'Положение'}
                    for par_pref in sl_tmp:
                        lst_json.append(
                            {"Signal": {"UserTree": f'Исполнительные механизмы/Главная/АПРК. {sl_tmp[par_pref]}',
                                        "OpcTag": f'{obj[0]}.APR.IM.{par_pref}',
                                        "EUnit": '%',
                                        "Description": f'АПРК. {sl_tmp[par_pref]}'}})
            # для каждого узла(мнемосхемы)...
            for node in sl_node_trends:
                # ...для каждого параметра по отсортированному словарю параметров в узле...
                for param in sorted(sl_node_trends[node]):
                    # ...собираем json
                    # print(node, param, sl_node_trends[node][param])
                    lst_json.append(
                        {"Signal": {"UserTree": f"{sl_group_trends[list_config][0]}/"
                                                f"{node.replace('/', '|')}/{param.replace('/', '|')}",
                                    "OpcTag":
                                        f'{obj[0]}.{sl_group_trends[list_config][1]}.{sl_node_trends[node][param][0]}',
                                    "EUnit": sl_node_trends[node][param][1],
                                    "Description": param}})

            # для каждого узла-драйвера в отсортированном словаре драйверов...
            for drv in sorted(sl_node_drv):
                # ... для каждого сигнала драйвера по отсортированному словарю сигналов в узле-драйвере
                for sig_drv in sorted(sl_node_drv[drv]):
                    # ...собираем json
                    # дополнительная проверка наличия драйвера в объявленных
                    if drv in sl_all_drv:
                        lst_json.append(
                            {"Signal": {"UserTree": f"{sl_group_trends['Драйвера'][0]}/"
                                                    f"{sl_all_drv[drv].replace('/', '|')}/{sig_drv.replace('/', '|')}",
                                        "OpcTag":
                                            f"{obj[0]}.{sl_group_trends['Драйвера'][1]}.{sl_node_drv[drv][sig_drv][0]}",
                                        "EUnit": sl_node_drv[drv][sig_drv][1],
                                        "Description": sig_drv}})

            # для каждого типа аварии в остортированном словаре типов аварий...
            for node in sorted(sl_node_alr):
                # ...для каждой аварии по отсортированному словарю аварий в узле(типе)...
                for alr in sorted(sl_node_alr[node]):
                    # ...собираем json
                    lst_json.append(
                        {"Signal": {"UserTree": f"Аварии/{node.replace('/', '|')}/"
                                                f"{node.replace('/', '|')}. {alr.replace('/', '|')}",
                                    "OpcTag":
                                        f"{obj[0]}.System.{sl_node_alr[node][alr][0]}",
                                    "EUnit": sl_node_alr[node][alr][1],
                                    "Description": f'{node}. {alr}'}})
            # для каждого режима в отсортированном словаре режимов
            for mode in sorted(sl_node_modes):
                # ...собираем json
                lst_json.append(
                    {"Signal": {"UserTree": f"Режимы/Режим {mode}",
                                "OpcTag":
                                    f"{obj[0]}.System.MODES.{sl_node_modes[mode][0]}",
                                "EUnit": sl_node_modes[mode][1],
                                "Description": mode}})

        # Добавление уставок на тренды
        # Выбираем лист уставок в качестве активного
        sheet = book['Уставки']
        # Устанавливаем Диапазон считывания для первой строки (узнать индексы столбцов)
        cells_name = sheet['A1': 'AG1']
        rus_par_ind = is_f_ind(cells_name[0], 'Наименование параметра')
        alg_name_ind = is_f_ind(cells_name[0], 'Алгоритмическое имя')
        eunit_ind = is_f_ind(cells_name[0], 'Единицы измерения')
        cpu_par = is_f_ind(cells_name[0], 'CPU')

        # Устанавливаем диапазон для чтения параметров
        cells_read = sheet['A2': 'AG' + str(sheet.max_row)]
        sl_node_set = {}
        # пробегаемся по параметрам листа
        for par in cells_read:
            # Если конец строки, то заканчиваем обработку ячеек
            if par[rus_par_ind].value is None:
                break
            # если параметр принадлежит контроллеру объекта
            if par[cpu_par].value in sl_object_all[obj]:
                # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                sl_node_set[par[rus_par_ind].value] = (par[alg_name_ind].value.replace('|', '_') + '.Value',
                                                       par[eunit_ind].value)
        # для каждой уставки в отсортированном словаре уставок
        for a_set_rus in sorted(sl_node_set):
            # ...собираем json
            lst_json.append(
                {"Signal": {"UserTree": f"Уставки/{a_set_rus.replace('/', '|')}",
                            "OpcTag":
                                f"{obj}.System.SET.{sl_node_set[a_set_rus][0]}",
                            "EUnit": sl_node_set[a_set_rus][1],
                            "Description": a_set_rus}})

        # Дополнительный перебор для сбора отказов
        for list_config in sl_brk_group_trends:
            # для каждой группы создаём словарь с пустыми словарями для каждого узла
            sl_node_trends = {node: {} for node in tuple_node_trends}
            # Выбираем  текущий лист в качестве активного
            sheet = book[list_config]
            # Устанавливаем Диапазон считывания для первой строки (узнать индексы столбцов)
            cells_name = sheet['A1': 'AG1']
            rus_par_ind = is_f_ind(cells_name[0], 'Наименование параметра')
            alg_name_ind = is_f_ind(cells_name[0], 'Алгоритмическое имя')
            # eunit_ind = is_f_ind(cells_name[0], 'Единицы измерения')
            node_name_ind = is_f_ind(cells_name[0], 'Узел')

            # Устанавливаем диапазон для чтения параметров
            cells_read = sheet['A2': 'AG' + str(sheet.max_row)]
            # пробегаемся по параметрам листа
            for par in cells_read:
                # Если конец строки, то заканчиваем обработку ячеек
                if par[rus_par_ind].value is None:
                    break
                # при условии, что находимся на листе 'Измеряемые', 'Расчетные' или на Входные и сигнал не привязан к ИМ
                # и параметр принадлежит контроллеру объекта
                if (list_config in ('Измеряемые', 'Расчетные') or list_config == 'Входные' and
                    par[is_f_ind(cells_name[0], 'ИМ')].value == 'Нет') and \
                        par[cpu_par].value in sl_object_all[obj]:
                    # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                    sl_par_trends = \
                        {f_ind_json(par[rus_par_ind].value): (par[alg_name_ind].value.replace('|', '_') + '.fValue',
                                                              '-')}
                    # добавляем словарь параметра в словарь узла
                    sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

            # для каждого узла(мнемосхемы)...
            for node in sl_node_trends:
                # ...для каждого параметра по отсортированному словарю параметров в узле...
                for param in sorted(sl_node_trends[node]):
                    # ...собираем json
                    lst_json.append(
                        {"Signal": {"UserTree": f"{sl_brk_group_trends[list_config][0]}/"
                                                f"{node.replace('/', '|')}/Отказ - {param.replace('/', '|')}",
                                    "OpcTag":
                                        f'{obj[0]}.{sl_brk_group_trends[list_config][1]}.'
                                        f'{sl_node_trends[node][param][0]}',
                                    "EUnit": sl_node_trends[node][param][1],
                                    "Description": f'Отказ - {param}'}})

        # Проверяем и перезаписываем файлы трендов в случае найденных отличий
        check_diff_file(check_path=os.path.join('File_for_Import', 'Trends'),
                        file_name_check=f'Tree{obj[0]}.json',
                        new_data=json_dumps({"UserTree": lst_json}, indent=1, ensure_ascii=False),
                        message_print=f'Требуется заменить файл Tree{obj[0]}.json - Групповые тренды')
