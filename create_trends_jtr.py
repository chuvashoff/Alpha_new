from json import load as json_load, dumps as json_dumps
from func_for_v3 import check_diff_file, is_f_ind, f_ind_json
import os


# with open('trends_tree.sample.jtr', 'r', encoding='UTF-8') as f_s:
#     text_json_test = json_load(f_s)
#     sl_signal = text_json_test
#
# # print(sl_signal.keys())  # ['TreeDescription', 'PrototypesDictionary', 'LineStyleDictionary']
#
# print(sl_signal.get('LineStyleDictionary'))
#
# lst_LineStyleDictionary = list()
#
# '''
# {'id': ('sBndaH', 'sBndwH', 'sBndwL', 'sBndaL'),
#                             'visible': ('True',)*4,
#                             'title': ('Верхняя аварийная уставка', 'Верхняя предупредительная уставка',
#                                       'Нижняя предупредительная уставка', 'Нижняя аварийная уставка'),
#                             'style': ({'color': '0xffff0000', 'brushStyle': 2, 'thickness': 1},)*4}
# '''
#
# tuple_LineStyleDictionary = (('sBndaH', 'sBndwH', 'sBndwL', 'sBndaL'),
#                              ('True',)*4,
#                              ('Верхняя аварийная уставка', 'Верхняя предупредительная уставка',
#                               'Нижняя предупредительная уставка', 'Нижняя аварийная уставка'),
#                              ({'color': '0xffff0000', 'brushStyle': 2, 'thickness': 1},)*4)
#
# for num, sig in enumerate(tuple_LineStyleDictionary[0]):
#     keys = ('id', 'visible', 'title', 'style')
#     # print(dict(zip(keys, [tuple_LineStyleDictionary[i][num] for i in range(len(tuple_LineStyleDictionary[0]))])))
#     sl_tmp = dict(zip(keys, [tuple_LineStyleDictionary[i][num] for i in range(len(tuple_LineStyleDictionary[0]))]))
#     lst_LineStyleDictionary.append(sl_tmp)
#
# # Проверяем и перезаписываем файлы трендов в случае найденных отличий
# check_diff_file(check_path=os.path.join('File_for_Import', 'Trends'),
#                 file_name_check=f'Tree.jtr',
#                 new_data=json_dumps({"TreeDescription": list(), "PrototypesDictionary": list(), "LineStyleDictionary": lst_LineStyleDictionary }, indent=1, ensure_ascii=False),
#                 message_print=f'Требуется заменить файл Tree.jtr - Групповые тренды')


def is_create_trends_jtr(book, sl_object_all, sl_cpu_spec, sl_all_drv, sl_for_diag, sl_need_add: dict[dict]):
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
        'ИМ': ('ИМ', 'IM'),
        'ИМ(АО)': ('Аналоговые ИМ', 'IM'),
        'Драйвера': ('Сигналы от драйверов', 'System.DRV'),
        'Сигналы': ()
    }
    # sl_brk_group_trends = {
    #     'Измеряемые': ('Отказы аналоговых входных', 'AI'),
    #     'Расчетные': ('Отказы расчетных параметров', 'AE'),
    #     'Входные': ('Отказы дискретных входных', 'DI')
    # }
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
    # print(sl_object_all)
    # Словарь модулей и сигналов, по которым нужны тренды диагностики по умолчанию,
    # в случае ошибок используется он
    sl_signal_module_default = {
        'M531I': {'Частота канала 1 модуля': ('Canal_01', 'Гц'), 'Частота канала 2 модуля': ('Canal_02', 'Гц'),
                  'Частота канала 3 модуля': ('Canal_03', 'Гц'), 'Частота канала 4 модуля': ('Canal_04', 'Гц'),
                  'Частота канала 5 модуля': ('Canal_05', 'Гц'), 'Частота канала 6 модуля': ('Canal_06', 'Гц'),
                  'Частота канала 7 модуля': ('Canal_07', 'Гц'), 'Частота канала 8 модуля': ('Canal_08', 'Гц'),
                  'Ошибка канала 1 модуля': ('Err_Canal_01', '-'), 'Ошибка канала 2 модуля': ('Err_Canal_02', '-'),
                  'Ошибка канала 3 модуля': ('Err_Canal_03', '-'), 'Ошибка канала 4 модуля': ('Err_Canal_04', '-'),
                  'Ошибка канала 5 модуля': ('Err_Canal_05', '-'), 'Ошибка канала 6 модуля': ('Err_Canal_06', '-'),
                  'Ошибка канала 7 модуля': ('Err_Canal_07', '-'), 'Ошибка канала 8 модуля': ('Err_Canal_08', '-')},

        'M532I': {'Частота канала 1 модуля': ('Canal_01', 'Гц'), 'Частота канала 2 модуля': ('Canal_02', 'Гц'),
                  'Частота канала 3 модуля': ('Canal_03', 'Гц'), 'Частота канала 4 модуля': ('Canal_04', 'Гц'),
                  'Частота канала 5 модуля': ('Canal_05', 'Гц'), 'Частота канала 6 модуля': ('Canal_06', 'Гц'),
                  'Частота канала 7 модуля': ('Canal_07', 'Гц'), 'Частота канала 8 модуля': ('Canal_08', 'Гц'),
                  'Ошибка канала 1 модуля': ('Err_Canal_01', '-'), 'Ошибка канала 2 модуля': ('Err_Canal_02', '-'),
                  'Ошибка канала 3 модуля': ('Err_Canal_03', '-'), 'Ошибка канала 4 модуля': ('Err_Canal_04', '-'),
                  'Ошибка канала 5 модуля': ('Err_Canal_05', '-'), 'Ошибка канала 6 модуля': ('Err_Canal_06', '-'),
                  'Ошибка канала 7 модуля': ('Err_Canal_07', '-'), 'Ошибка канала 8 модуля': ('Err_Canal_08', '-')},

        'M582IS': {'Частота канала 1 модуля': ('Canal_01', 'Гц'), 'Частота канала 2 модуля': ('Canal_02', 'Гц'),
                   'Частота канала 3 модуля': ('Canal_03', 'Гц'),
                   'Ошибка канала 1 модуля': ('Err_Canal_01', '-'), 'Ошибка канала 2 модуля': ('Err_Canal_02', '-'),
                   'Ошибка канала 3 модуля': ('Err_Canal_03', '-')},
        'M501E': {'Цикл контроллера': ('TCycle', 'с'), 'Максимальный цикл контроллера': ('TCycleMax', 'с'),
                  'Температура контроллера': ('CpuTemp', '°C')},
        'M903E': {'Цикл контроллера': ('TCycle', 'с'), 'Максимальный цикл контроллера': ('TCycleMax', 'с'),
                  'Температура контроллера': ('CpuTemp', '°C')},
    }

    # sl_signal_module = {}
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Trends', f'Diagnostic.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Trends', f'Diagnostic.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_signal_module = text_json
        else:
            print('Файл Systemach/Trends/Diagnostic.json не найден, '
                  'тренды диагностики железяк будут определены по умолчанию')
            sl_signal_module = sl_signal_module_default
    except (Exception, KeyError):
        print('Файл Systemach/Trends/Diagnostic.json заполнен некорректно, '
              'тренды диагностики железяк будут определены по умолчанию')
        sl_signal_module = sl_signal_module_default

    # sl_for_diag - словарь диагностики, ключ - cpu, значение - словарь: ключ - имя модуля, значение - тип модуля
    # в случае CPU - ключ - 'CPU', значение - кортеж (имя cpu,тип cpu)

    # В словаре sl_for_diag оставляем только те конструкции, где есть частотные модуля или модуль БЗА
    sl_for_diag = {cpu: {module_name: module_type for module_name, module_type in sl_modules.items()
                         if module_type in sl_signal_module or module_name == 'CPU'}  # ('M531I', 'M532I', 'M582IS')
                   for cpu, sl_modules in sl_for_diag.items()}
    # Приводим sl_for_diag к удобоваримому виду, чтобы было красиво
    # {'GTU': {'AD100': 'M501E', 'AD101': 'M531I', 'AD1': 'M582IS'}, 'GPA': {'AD200': 'M501E'}}
    for cpu in sl_for_diag:
        tmp_dic = {module_name if module_name != 'CPU' else sl_for_diag[cpu]['CPU'][0]: (module_type
                                                                                         if module_name != 'CPU' else
                                                                                         sl_for_diag[cpu]['CPU'][1])
                   for module_name, module_type in sl_for_diag[cpu].items()}
        sl_for_diag[cpu] = tmp_dic
    # оставляем в словаре только те элементы, которые не с пустыми значениями
    sl_for_diag = {i: j for i, j in sl_for_diag.items() if j}

    # Для каждого объекта, прочитанного ранее
    for obj in sl_object_all:
        lst_json = list()
        sl_for_json = {value[0] if len(value) > 1 else _: list() for _, value in sl_group_trends.items()}
        check_add_regnum = False
        # Для каждого листа конфигуратора в словаре групп для трендов(ключи словаря определили
        # по объявленным мнемосхемам)
        for list_config in sl_group_trends:
            # для каждой группы создаём словарь с пустыми словарями для каждого узла
            sl_node_trends = {node: {} for node in tuple_node_trends}
            # Создаём словарь возможных типов защит - используем при парсинге листа Сигналы и сборке аварий
            sl_node_alr = {}
            lst_node_modes = list()  # список возможных режимов
            sl_node_drv = {}  # Словарь возможных драйверов
            # Выбираем текущий лист в качестве активного
            sheet = book[list_config]
            # Устанавливаем Диапазон считывания для первой строки (узнать индексы столбцов)
            cells_name = sheet['A1': 'AZ1']
            rus_par_ind = is_f_ind(cells_name[0], 'Наименование параметра')
            alg_name_ind = is_f_ind(cells_name[0], 'Алгоритмическое имя')
            # eunit_ind = is_f_ind(cells_name[0], 'Единицы измерения')
            node_name_ind = is_f_ind(cells_name[0], 'Узел')
            eunit_drv_ind = is_f_ind(cells_name[0], 'Единица измерения')
            t_sig_drv_ind = is_f_ind(cells_name[0], 'Тип')
            cpu_par = is_f_ind(cells_name[0], 'CPU')
            name_drv_ind = is_f_ind(cells_name[0], 'Драйвер')
            reserve_par_ind = is_f_ind(cells_name[0], 'Резервный')
            index_save_history = is_f_ind(cells_name[0], 'Сохранять в истории')
            index_fast = is_f_ind(cells_name[0], 'Передача по МЭК')
            index_sBndaH = is_f_ind(cells_name[0], 'Верхняя аварийная уставка')
            index_sBndwH = is_f_ind(cells_name[0], "Верхняя предупредительная уставка")
            index_sBndwL = is_f_ind(cells_name[0], 'Нижняя предупредительная уставка')
            index_sBndaL = is_f_ind(cells_name[0], 'Нижняя аварийная уставка')

            # Устанавливаем диапазон для чтения параметров
            cells_read = sheet['A2': 'AZ' + str(sheet.max_row)]
            # пробегаемся по параметрам листа
            for par in cells_read:
                # Если конец строки, то заканчиваем обработку ячеек
                if par[rus_par_ind].value is None:
                    break
                # при условии, что находимся на листе 'Измеряемые', 'Расчетные' или на Входные и сигнал не привязан к ИМ
                # и параметр принадлежит контроллеру объекта и не переведено в резерв
                if (list_config in ('Измеряемые', 'Расчетные') or
                    list_config == 'Входные' and par[is_f_ind(cells_name[0], 'ИМ')].value == 'Нет') and \
                        par[cpu_par].value in sl_object_all[obj] and par[reserve_par_ind].value == 'Нет':
                    # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                    rus_name_par = par[rus_par_ind].value + '(С меткой времени ПЛК)' if par[index_fast].value == 'Да' \
                        else par[rus_par_ind].value
                    if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                        rus_name_par += ' (РЕЗЕРВ)'
                    # sl_par_trends = {f_ind_json(rus_name_par): (par[alg_name_ind].value.replace('|', '_') +
                    #                                             '.Value',
                    #                                             ('-' if list_config == 'Входные' else
                    #                                              par[eunit_ind].value))}
                    pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                    lst_children_par = list()
                    lst_levels = list()
                    data_type = 'bool'
                    # print(index_sBndaH, index_sBndwH, index_sBndwL, index_sBndaL)
                    if list_config in ('Измеряемые', 'Расчетные'):
                        data_type = 'float'
                        for i, teg in {index_sBndaH: 'sBndaH', index_sBndwH: 'sBndwH',
                                       index_sBndwL: 'sBndwL', index_sBndaL: 'sBndaL'}.items():
                            # print(par[i].value)
                            if par[i].value == 'Да':
                                lst_levels.append({'tag': f"{pref_tag}.{par[alg_name_ind].value.replace('|', '_')}.{teg}",
                                                   'lineStyleId': teg})
                    dict_child = {'name': 'Value',
                                  "description": f'{f_ind_json(rus_name_par)}',
                                  'tag': f"{pref_tag}.{par[alg_name_ind].value.replace('|', '_')}.Value",
                                  'dataType': data_type}
                    if lst_levels:
                        dict_child.update({'levels': lst_levels})
                    # Добавляем отказы
                    dict_f_child = {'name': 'fValue',
                                    "description": f'Отказ - {f_ind_json(rus_name_par)}',
                                    'tag': f"{pref_tag}.{par[alg_name_ind].value.replace('|', '_')}.fValue",
                                    'dataType': 'bool'}
                    lst_children_par.append(dict_child)
                    lst_children_par.append(dict_f_child)
                    sl_par_trends = {f_ind_json(rus_name_par): (par[alg_name_ind].value.replace('|', '_'), lst_children_par)}

                    # добавляем словарь параметра в словарь узла
                    sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                # при условии, что парсим лист ИМов
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('ИМ',) and par[cpu_par].value in sl_object_all[obj]:
                    # если 'ИМ1Х0', 'ИМ1Х0и'
                    if par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х0', 'ИМ1Х0и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                        rus_name_par = par[rus_par_ind].value
                        if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                            rus_name_par += ' (РЕЗЕРВ)'
                        pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                        lst_children_par = list()
                        dict_child = {'name': 'oOn',
                                      "description": f'{f_ind_json(rus_name_par)}. {move_}',
                                      'tag': f"{pref_tag}.{par[alg_name_ind].value}.oOn",
                                      'dataType': 'bool'}
                        lst_children_par.append(dict_child)
                        sl_par_trends = {f'{f_ind_json(rus_name_par)}': (f"{par[alg_name_ind].value}", lst_children_par)}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ1Х1', 'ИМ1Х1и'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х1', 'ИМ1Х1и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'oOn': move_, 'stOn': sl_state_im_gender[move_][gender_]}
                        rus_name_par = par[rus_par_ind].value
                        if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                            rus_name_par += ' (РЕЗЕРВ)'
                        pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                        lst_children_par = list()
                        for postf, movef in sl_tmp.items():
                            dict_child = {'name': postf,
                                          "description": f"{f_ind_json(rus_name_par)}. {movef}",
                                          'tag': f"{pref_tag}.{par[alg_name_ind].value}.{postf}",
                                          'dataType': 'bool'}
                            lst_children_par.append(dict_child)
                        sl_par_trends = {
                            f'{f_ind_json(rus_name_par)}': (f"{par[alg_name_ind].value}", lst_children_par)}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ1Х2', 'ИМ1Х2и'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ1Х2', 'ИМ1Х2и'):
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'oOn': move_, 'stOn': sl_state_im_gender[move_][gender_],
                                  'stOff': sl_state_im_gender[move_ + '_off'][gender_]}
                        rus_name_par = par[rus_par_ind].value
                        if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                            rus_name_par += ' (РЕЗЕРВ)'
                        pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                        lst_children_par = list()
                        for postf, movef in sl_tmp.items():
                            dict_child = {'name': postf,
                                          "description": f"{f_ind_json(rus_name_par)}. {movef}",
                                          'tag': f"{pref_tag}.{par[alg_name_ind].value}.{postf}",
                                          'dataType': 'bool'}
                            lst_children_par.append(dict_child)
                        sl_par_trends = {
                            f'{f_ind_json(rus_name_par)}': (f"{par[alg_name_ind].value}", lst_children_par)}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                    # если 'ИМ2Х2', 'ИМ2Х2с', 'ИМ2Х4'
                    elif par[is_f_ind(cells_name[0], 'Тип ИМ')].value in ('ИМ2Х2', 'ИМ2Х2с', 'ИМ2Х4', 'ИМ2Х2ПЧ'):
                        t_im = par[is_f_ind(cells_name[0], 'Тип ИМ')].value
                        move_ = par[is_f_ind(cells_name[0], 'Вкл./откр.')].value  # определяем тип открытия
                        gender_ = par[is_f_ind(cells_name[0], 'Род')].value  # определяем род ИМ
                        # создаём промежуточный словарь с возможными префиксами сигналов
                        sl_tmp = {'oOn': 'Включить через ПЧ' if t_im == 'ИМ2Х2ПЧ' else move_,
                                  'oOff': 'Включить через байпас' if t_im == 'ИМ2Х2ПЧ' else sl_antonym[move_],
                                  'stOn': 'Включен через ПЧ' if t_im == 'ИМ2Х2ПЧ'
                                  else sl_state_im_gender[move_][gender_],
                                  'stOff': 'Включен через байпас' if t_im == 'ИМ2Х2ПЧ'
                                  else sl_state_im_gender[move_ + '_off'][gender_]}
                        rus_name_par = par[rus_par_ind].value
                        if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                            rus_name_par += ' (РЕЗЕРВ)'
                        pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                        lst_children_par = list()
                        for postf, movef in sl_tmp.items():
                            dict_child = {'name': postf,
                                          "description": f"{f_ind_json(rus_name_par)}. {movef}",
                                          'tag': f"{pref_tag}.{par[alg_name_ind].value}.{postf}",
                                          'dataType': 'bool'}
                            lst_children_par.append(dict_child)
                        sl_par_trends = {
                            f'{f_ind_json(rus_name_par)}': (f"{par[alg_name_ind].value}", lst_children_par)}
                        # добавляем словарь параметра в словарь узла
                        sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                # при условии, что парсим лист ИМ(АО) и выделена как ИМ
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('ИМ(АО)',) and par[is_f_ind(cells_name[0], 'ИМ')].value == 'Да' and \
                        par[cpu_par].value in sl_object_all[obj]:
                    # sl_tmp промежуточный словарь с возможными префиксами сигналов
                    sl_tmp = {'Set': 'Задание', 'iPos': 'Положение'}
                    rus_name_par = par[rus_par_ind].value
                    if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                        rus_name_par += ' (РЕЗЕРВ)'
                    pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"
                    lst_children_par = list()
                    for postf, movef in sl_tmp.items():
                        dict_child = {'name': postf,
                                      "description": f"{f_ind_json(rus_name_par)}. {movef}",
                                      'tag': f"{pref_tag}.{par[alg_name_ind].value}.{postf}",
                                      'dataType': 'float'}
                        lst_children_par.append(dict_child)
                    sl_par_trends = {
                        f'{f_ind_json(rus_name_par)}': (f"{par[alg_name_ind].value}", lst_children_par)}
                    # добавляем словарь параметра в словарь узла
                    sl_node_trends[par[node_name_ind].value].update(sl_par_trends)

                # при условии, что парсим лист Сигналы
                # и параметр принадлежит контроллеру объекта
                elif list_config in ('Сигналы',) and par[cpu_par].value in sl_object_all[obj]:
                    type_protect = par[is_f_ind(cells_name[0], 'Тип защиты')].value
                    # Если увидели аварию
                    if type_protect in 'АОссАОбсВОссВОбсАОНО':
                        pref_tag = f"{obj[0]}.System.ALR"
                        alg_name = par[alg_name_ind].value.replace('ALR|','')
                        # lst_children_par = list()
                        dict_child = {'name': alg_name,
                                      "description": f'{f_ind_json(par[rus_par_ind].value)}',
                                      'tag': f"{pref_tag}.{alg_name}.Value",
                                      'dataType': 'bool'}
                        # lst_children_par.append(dict_child)
                        # если в словаре аварий отсутствует такая авария, то создаём
                        if type_protect not in sl_node_alr:
                            sl_node_alr[type_protect] = [dict_child, ]
                        else:  # иначе обновляем словарь, который есть
                            sl_node_alr[type_protect].append(dict_child)
                    # Если увидели режим
                    elif type_protect in ('Режим',):
                        pref_tag = f"{obj[0]}.System.MODES"
                        alg_name = par[alg_name_ind].value.replace('MOD|', '')
                        if not check_add_regnum:
                            dict_child_r = {'name': 'regNum',
                                            "description": f'Номер режима',
                                            'tag': f"{pref_tag}.regNum.Value",
                                            'dataType': 'int4'}
                            if dict_child_r not in lst_node_modes:
                                lst_node_modes.append(dict_child_r)
                            check_add_regnum = True
                        dict_child = {'name': alg_name,
                                      "description": f'Режим {f_ind_json(par[rus_par_ind].value)}',
                                      'tag': f"{pref_tag}.{alg_name}.Value",
                                      'dataType': 'bool'}
                        if dict_child not in lst_node_modes:
                            lst_node_modes.append(dict_child)

                # при условии, что парсим лист Драйверов
                # и параметр принадлежит контроллеру объекта
                # и указанный драйвер переменной есть в объявленных
                elif list_config in ('Драйвера',) and par[cpu_par].value in sl_object_all[obj] \
                        and par[name_drv_ind].value in sl_all_drv and par[index_save_history].value == 'Да':
                    sl_type_unit = {'BOOL': '-',
                                    'INT': par[eunit_drv_ind].value,
                                    'FLOAT': par[eunit_drv_ind].value,
                                    'IEC': '-', 'Daily': '-',
                                    'IECB': '-',
                                    'IECR': par[eunit_drv_ind].value,
                                    'INT (с имитацией)': par[eunit_drv_ind].value,
                                    'FLOAT (с имитацией)': par[eunit_drv_ind].value}
                    sl_data_type = dict(zip(sl_type_unit.keys(), ('bool', 'int4', 'float', 'float', 'bool', 'float', 'int4', 'float')))
                    drv_ = par[is_f_ind(cells_name[0], 'Драйвер')].value
                    # создаём промежуточный словарь сигнала драйвера {рус.имя: (алг.имя, единицы измерения - '-')}
                    rus_name_sig = par[rus_par_ind].value + '(С меткой времени ПЛК)' \
                        if 'IEC' in par[t_sig_drv_ind].value else par[rus_par_ind].value
                    if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                        rus_name_sig += ' (РЕЗЕРВ)'
                    pref_tag = f"{obj[0]}.{sl_group_trends[list_config][1]}"

                    dict_child = {'name': f'{drv_}-{par[alg_name_ind].value}',
                                  "description": f'{f_ind_json(rus_name_sig)}',
                                  'tag': f"{pref_tag}.{drv_}.{par[alg_name_ind].value}.Value",
                                  'dataType': sl_data_type.get(par[t_sig_drv_ind].value, 'float')}

                    # sl_drv_trends = \
                    #     {f'{f_ind_json(rus_name_sig)}': (f'{pref_tag}.{drv_}.' + par[alg_name_ind].value + '.Value',
                    #                                      sl_type_unit.get(par[t_sig_drv_ind].value, '-'))}
                    # sl_drv_trends = {f'{f_ind_json(rus_name_sig)}': dict_child}
                    # если в словаре драйверов отсутствует такой драйвер, то создаём
                    if drv_ not in sl_node_drv:
                        sl_node_drv[drv_] = [dict_child,]
                        # sl_node_drv[drv_] = sl_drv_trends
                    else:  # иначе обновляем словарь, который есть
                        sl_node_drv[drv_].append(dict_child)
                        # sl_node_drv[drv_].update(sl_drv_trends)

            # на этапе парсинга листа ИМАО добавляем в тренды АПР
            # if list_config == 'ИМ(АО)':
            #     # создаём множество пересечений контроллеров АПР и контроллеров объекта
            #     # чтобы далее проверить, не пустое ли оно и в объект загрузить апр
            #     set_check_apr = set([key for key, value in sl_cpu_spec.items() if 'АПР' in value]) & \
            #                     set(sl_object_all[obj])
            #     if 'АПР' in [item for sublist in [i for i in sl_cpu_spec.values() if i] for item in sublist] and \
            #             set_check_apr:
            #         sl_tmp = {'Set': 'Задание', 'Pos': 'Положение'}
            #         child_sig_apr = list()
            #         for par_pref in sl_tmp:
            #             dict_child = {'name': f'АПРК-{par_pref}',
            #                           "description": f"АПРК. {sl_tmp.get(par_pref, '')}",
            #                           'tag': f'{obj[0]}.APR.IM.{par_pref}',
            #                           'dataType': 'float'}
            #             child_sig_apr.append(dict_child)
            #         if sl_for_json.get('АПР'):
            #             sl_for_json['АПР'].append({'name': 'АПРК', 'children': child_sig_apr})
            #         else:
            #             sl_for_json['АПР'] = [{'name': 'АПРК', 'children': child_sig_apr},]

            # sl_par_trends = {f_ind_json(rus_name_par): (ar[alg_name_ind].value.replace('|', '_'), lst_children_par)}
            # sl_node_trends[par[node_name_ind].value].update(sl_par_trends)
            # для каждого узла(мнемосхемы)...
            for node in sl_node_trends:
                # if sl_node_trends.get(node):
                #     print(obj, node)
                # print(node, sl_node_trends[node])
                # ...для каждого параметра по отсортированному словарю параметров в узле...
                lst_tmp_node = list()
                for param in sorted(sl_node_trends[node]):
                    lst_tmp_node.append({'name': sl_node_trends[node][param][0], "description": param,
                                         'children': sl_node_trends[node][param][1]})
                if lst_tmp_node:
                    # lst_json.append({'name': node, 'children': lst_tmp_node})
                    sl_for_json[sl_group_trends[list_config][0]].append({'name': node, "description": node, 'children': lst_tmp_node})

            sl_for_json["Аварии"] = list()
            # для каждого типа аварии в отсортированном словаре типов аварий...
            for node_alr in sorted(sl_node_alr):
                sl_for_json["Аварии"].append({'name': node_alr, "description": node_alr, 'children': sl_node_alr[node_alr]})
            sl_for_json["Режимы"] = lst_node_modes

            # sl_for_json["Сигналы от драйверов"] = list()
            for drv in sorted(sl_node_drv):
                drv_rus_name = sl_all_drv.get(drv, 'Неизвестный драйвер')
                sl_for_json["Сигналы от драйверов"].append({'name': drv_rus_name, "description": drv_rus_name, 'children': sl_node_drv[drv]})
            # print(sl_for_json["Сигналы от драйверов"])

            # if sl_node_drv:
            #     print(sl_node_drv)
            #     print(sl_all_drv)
            # for drv in sorted(sl_node_drv):
            #     for sig_drv in sorted(sl_node_drv[drv]):
            #         if sl_node_drv.get(drv):
            #             pass

        # Добавляем АПР
        # создаём множество пересечений контроллеров АПР и контроллеров объекта
        # чтобы далее проверить, не пустое ли оно и в объект загрузить апр
        set_check_apr = set([key for key, value in sl_cpu_spec.items() if 'АПР' in value]) & \
                        set(sl_object_all[obj])
        if 'АПР' in [item for sublist in [i for i in sl_cpu_spec.values() if i] for item in sublist] and \
                set_check_apr:
            sl_tmp = {'Set': 'Задание', 'Pos': 'Положение'}
            sl_for_json['АПР'] = list()
            lst_tunings = list()
            if os.path.exists(os.path.join('Template_Alpha', 'APR', 'Tun_APR.txt')):
                with open(os.path.join('Template_Alpha', 'APR', f'Tun_APR.txt'), 'r',
                          encoding='UTF-8') as f_sar:
                    for line in f_sar:
                        if '#' in line:
                            continue
                        if not line.strip():
                            break
                        line = line.strip().split(';')
                        tag = line[0]
                        descr = line[1]
                        full_tag = f'{obj[0]}.APR.Tuning.{tag}.Value'
                        dict_child = {'name': descr,
                                      "description": descr,
                                      'tag': full_tag,
                                      'dataType': 'float'}
                        lst_tunings.append(dict_child)
            sl_for_json["АПР"].append({'name': f"Настройки АПР", "description": "Настройки АПР", 'children': lst_tunings})
            child_sig_apr = list()
            for par_pref in sl_tmp:
                dict_child = {'name': f'АПРК-{par_pref}',
                              "description": f"АПРК, {sl_tmp.get(par_pref, '')}",
                              'tag': f'{obj[0]}.APR.IM.{par_pref}',
                              'dataType': 'float'}
                child_sig_apr.append(dict_child)
            sl_for_json['АПР'].append({'name': 'АПРК', "description": "АПРК", 'children': child_sig_apr})
        #
        # Добавляем САР
        # Для каждого контроллера объекта...
        if 'САР' in ['САР' for i in set(sl_object_all[obj].keys()) & set(sl_cpu_spec.keys()) if
                     'САР' in sl_cpu_spec[i]]:
            sl_for_json["САР"] = list()
            lst_tunings = list()
            if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'Tun_SAR.txt')):
                with open(os.path.join('Template_Alpha', 'SAR', f'Tun_SAR.txt'), 'r',
                          encoding='UTF-8') as f_sar:
                    for line in f_sar:
                        if '#' in line:
                            continue
                        if not line.strip():
                            break
                        line = line.strip().split(';')
                        tag = line[0]
                        descr = line[3]
                        full_tag = f'{obj[0]}.SAR.Tuning.{tag}.Value'
                        dict_child = {'name': descr,
                                      "description": descr,
                                      'tag': full_tag,
                                      'dataType': 'float'}
                        lst_tunings.append(dict_child)
            sl_for_json["САР"].append({'name': f"Настройки САР", "description": "Настройки САР", 'children': lst_tunings})
            lst_khr = list()
            for pref_tag, descr_tag in {'Set': 'Задание', 'Pos': 'Положение'}.items():
                dict_child = {'name': f'КХР, {descr_tag}',
                              "description": f'КХР, {descr_tag}',
                              'tag': f'{obj[0]}.SAR.IM.KHR.{pref_tag}',
                              'dataType': 'float'}
                lst_khr.append(dict_child)
            sl_for_json["САР"].append({'name': f"КХР", "description": "КХР", 'children': lst_khr})
        #

        # Добавление уставок на тренды.
        # Выбираем лист уставок в качестве активного
        sheet = book['Уставки']
        # Устанавливаем Диапазон считывания для первой строки (узнать индексы столбцов)
        cells_name = sheet['A1': 'AG1']
        rus_par_ind = is_f_ind(cells_name[0], 'Наименование параметра')
        alg_name_ind = is_f_ind(cells_name[0], 'Алгоритмическое имя')
        eunit_ind = is_f_ind(cells_name[0], 'Единицы измерения')
        cpu_par = is_f_ind(cells_name[0], 'CPU')
        reserve_par_ind = is_f_ind(cells_name[0], 'Резервный')
        index_fast = is_f_ind(cells_name[0], 'Передача по МЭК')
        index_node = is_f_ind(cells_name[0], 'Узел')

        # Устанавливаем диапазон для чтения параметров
        cells_read = sheet['A2': 'AG' + str(sheet.max_row)]
        sl_node_set = {}
        # пробегаемся по параметрам листа
        for par in cells_read:
            # Если конец строки, то заканчиваем обработку ячеек
            if par[rus_par_ind].value is None:
                break
            # если параметр принадлежит контроллеру объекта и не переведено в резерв
            if par[cpu_par].value in sl_object_all[obj] and par[reserve_par_ind].value == 'Нет':
                # создаём промежуточный словарь {рус.имя: (алг.имя, единицы измерения)}
                rus_name_par = par[rus_par_ind].value + '(С меткой времени ПЛК)' if par[index_fast].value == 'Да' \
                    else par[rus_par_ind].value
                if par[cpu_par].comment and f'{obj[1]}(нет)' in par[cpu_par].comment.text.split(';'):
                    rus_name_par += ' (РЕЗЕРВ)'
                name_node = par[index_node].value
                dict_child = {'name': f'{rus_name_par}',
                              "description": f"{rus_name_par}",
                              'tag': f"{obj[0]}.System.SET.{par[alg_name_ind].value.replace('|', '_') + '.Value'}",
                              'dataType': 'float'}
                if name_node not in sl_node_set:
                    sl_node_set[name_node] = [dict_child,]
                else:
                    sl_node_set[name_node].append(dict_child)

        sl_for_json["Уставки"] = list()
        # для каждой узла уставок в отсортированном словаре уставок
        for node_set in sorted(sl_node_set):
            sl_for_json["Уставки"].append({'name': node_set, "description": node_set, 'children': sl_node_set[node_set]})

        # print(sl_need_add)
        sl_for_json["Дополнительные параметры"] = list()
        # Добавляем дополнительные параметры если в объекте есть контроллеры с данными параметрами
        for _, pars in {c: p for c, p in sl_need_add.items() if c in set(sl_object_all[obj].keys())}.items():
            for p, param_p in pars.items():
                data_type = 'bool' if 'bool' in param_p[0].lower() else 'float'
                dict_child = {'name': f'{param_p[1]}',
                              "description": f"{param_p[1]}",
                              'tag': f"{obj[0]}.System.Pars.{p}.Value",
                              'dataType': data_type}
                sl_for_json["Дополнительные параметры"].append(dict_child)

        # Добавляем на тренды диагностику по интересным модулям
        # Если в словаре диагностики интересных модулей есть устройства объекта...
        if set(sl_object_all[obj].keys()) & set(sl_for_diag.keys()):
            sl_for_json["Диагностика"] = list()
            # Для каждого контроллера объекта...
            for cpu in sl_object_all[obj]:
                # ...для каждого спец модуля контроллера (частотный или бза)
                # при этом проверяем, что у контроллера вообще есть такие модуля, если нет, то перебора не будет
                for spec_module_name in sl_for_diag.get(cpu, {}):
                    lst_spec_module = list()
                    # узнаём тип текущего перебираемого модуля
                    type_module = sl_for_diag[cpu][spec_module_name]
                    # для сигналов модуля, описанных в словаре sl_signal_module добавляем тренды
                    for signal in sl_signal_module.get(type_module, ''):
                        try:
                            data_type_sig = sl_signal_module[type_module][signal][2]
                        except IndexError:
                            data_type_sig = 'float'
                        # print(f"{spec_module_name} ({type_module})", signal, data_type_sig)
                        tegg = f'{obj[0]}.Diag.HW.{spec_module_name}.{sl_signal_module[type_module][signal][0]}'
                        dict_child = {'name': f'{signal} {spec_module_name} ({type_module})',
                                      "description": f'{signal} {spec_module_name} ({type_module})',
                                      'tag': tegg,
                                      'dataType': data_type_sig}
                        lst_spec_module.append(dict_child)
                    sl_for_json["Диагностика"].append({'name': f"{spec_module_name} ({type_module})",
                                                      "description": f"{spec_module_name} ({type_module})",
                                                       'children': lst_spec_module})
        #

        # {'id': ('sBndaH', 'sBndwH', 'sBndwL', 'sBndaL'),
        #                             'visible': ('True',)*4,
        #                             'title': ('Верхняя аварийная уставка', 'Верхняя предупредительная уставка',
        #                                       'Нижняя предупредительная уставка', 'Нижняя аварийная уставка'),
        #                             'style': ({'color': '0xffff0000', 'brushStyle': 2, 'thickness': 1},)*4}
        # '''
        #
        tuple_LineStyleDictionary = (('sBndaH', 'sBndwH', 'sBndwL', 'sBndaL'),
                                     (False,)*4,
                                     ('Верхняя аварийная уставка', 'Верхняя предупредительная уставка',
                                      'Нижняя предупредительная уставка', 'Нижняя аварийная уставка'),
                                     ({'color': '0xffff0000', 'brushStyle': 2, "isHistorized": False, 'thickness': 1},
                                      {'color': '0xffffff00', 'brushStyle': 2, "isHistorized": False, 'thickness': 1},
                                      {'color': '0xffffff00', 'brushStyle': 2, "isHistorized": False, 'thickness': 1},
                                      {'color': '0xffff0000', 'brushStyle': 2, "isHistorized": False, 'thickness': 1}))
        #
        lst_LineStyleDictionary = list()
        for num, sig in enumerate(tuple_LineStyleDictionary[0]):
            keys = ('id', 'visible', 'title', 'style')
            # print(dict(zip(keys, [tuple_LineStyleDictionary[i][num] for i in range(len(tuple_LineStyleDictionary[0]))])))
            sl_tmp = dict(zip(keys, [tuple_LineStyleDictionary[i][num] for i in range(len(tuple_LineStyleDictionary[0]))]))
            lst_LineStyleDictionary.append(sl_tmp)
        #
        # # Проверяем и перезаписываем файлы трендов в случае найденных отличий
        # check_diff_file(check_path=os.path.join('File_for_Import', 'Trends'),
        #                 file_name_check=f'Tree.jtr',
        #                 new_data=json_dumps({"TreeDescription": list(), "PrototypesDictionary": list(), "LineStyleDictionary": lst_LineStyleDictionary }, indent=1, ensure_ascii=False),
        #                 message_print=f'Требуется заменить файл Tree.jtr - Групповые тренды')


        for group, children in sl_for_json.items():
            if children:
                lst_json.append({'name': group, 'description': group, 'children': children})
        # Проверяем и перезаписываем файлы трендов в случае найденных отличий
        check_diff_file(
            check_path=os.path.join('File_for_Import', 'Trends', 'jtr'),
            file_name_check=f'Tree{obj[0]}.jtr',
            new_data=json_dumps({"TreeDescription": lst_json, "LineStyleDictionary": lst_LineStyleDictionary},
                                indent=1, ensure_ascii=False),
            message_print=f'Требуется заменить файл Tree{obj[0]}.jtr - Групповые тренды')
