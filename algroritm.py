import openpyxl
import warnings
import os
import datetime

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

with open('Source_list_config.txt', 'r', encoding='UTF-8') as f:
    path_config = f.readline().strip()

print(datetime.datetime.now(), '- Начало сборки файлов')

file_config = 'UnimodCreate.xlsm'

# Ищем файл конфигуратора в указанном каталоге
for file in os.listdir(path_config):
    if file.endswith('.xlsm') or file.endswith('.xls'):
        file_config = file
        break

book = openpyxl.open(os.path.join(path_config, file_config))
sheet = book['Алгоритмы']
cells = sheet['A1': 'A' + str(sheet.max_row)]
sl_algoritm = {}

# заполняем sl_algoritm парами алг.имя команды: руское наименование команды
for p in cells:
    if p[0].value == 'Режим':
        cmd_eng, cmd_rus = (), ()
        jj = 7
        while jj != sheet.max_column and sheet[p[0].row][jj].value and sheet[p[0].row + 1][jj].value:
            cmd_rus += (sheet[p[0].row][jj].value,)
            cmd_eng += (sheet[p[0].row + 1][jj].value,)
            jj += 1
        sl_algoritm.update(dict(zip(cmd_eng, cmd_rus)))
j = 0
p = cells[0][0].value
while p != 'STOP':
    j += 1
    p = cells[j][0].value
    if p == 'Шаг':
        mod_name = sheet[j][1].value
        cpu_name = sheet[j][3].value
        print(cpu_name)
        while p is not None:
            j += 1
            p = cells[j][0].value
            # конструкции для условий перехода
            tuple_rus_step, tuple_eng_step = (), ()
            step_out_tmp = ()
            # конструкции для таймеров
            tuple_rus_step_timer, tuple_step_timer_value = (), ()
            step_timer_out_tmp = ()
            # конструкции для дополнительных параметров
            tuple_dop_par_rus = ()
            sl_dop_par_tmp = {}
            sl_dop_par_fragdigits_tmp = {}
            step_dop_par_out_tmp = ()
            step_dop_par_fragdigits_out_tmp = ()
            # конструкции для обратных таймеров
            sl_rev_timer_tmp = {}
            step_rev_timer_out_tmp = ()
            tuple_rev_timer_rus = ()
            if p is not None:
                # sheet[j + 1][4].value - русское условие
                # sheet[j + 1][3].value - алгоритмическое условие

                # если на шаге есть какое-то условие перехода(смотрим по русскому тексту), то обрабатываем
                if sheet[j + 1][4].value is not None:
                    # В данном виде в списках есть ИЛИ и OR. По ним делим в структуры
                    lst_rus_alg = sheet[j + 1][4].value.split('\n')
                    tuple_rus_step = ((lst_rus_alg[:lst_rus_alg.index('ИЛИ')] if 'ИЛИ' in lst_rus_alg else lst_rus_alg),
                                      (lst_rus_alg[lst_rus_alg.index('ИЛИ') + 1:] if 'ИЛИ' in lst_rus_alg else []))
                    # print(p, tuple_rus_step)
                    # print(p, [step for group_step in tuple_rus_step for step in group_step])
                    lst_eng_alg = [f"{i.strip(' AND')}" if i != 'OR' else 'OR'
                                   for i in sheet[j + 1][3].value.split('\n')]
                    tuple_eng_step = ((lst_eng_alg[:lst_eng_alg.index('OR')] if 'OR' in lst_eng_alg else lst_eng_alg),
                                      (lst_eng_alg[lst_eng_alg.index('OR') + 1:] if 'OR' in lst_eng_alg else []))
                    # print(p, tuple_eng_step)
                    # print(p, [step for group_step in tuple_eng_step for step in group_step])

                    # В данном виде в списках НЕТ ИЛИ и OR. Возможно, пригодится
                    # print(p, mod_name, [i for i in sheet[j + 1][4].value.split('\n') if i != 'ИЛИ'])
                    # print(p, [f"{mod_name}-{p}-{i.strip(' AND')}" for
                    # i in sheet[j + 1][3].value.split('\n') if i != 'OR'])

                # Если на шаге установлен какой-то таймер
                if sheet[j + 1][1].value is not None:
                    # print(p, float(sheet[j + 1][1].value), sheet[j + 1][2].value)
                    # добавляем текст таймера и текст выхода таймера в кортеж русских таймеров
                    tuple_rus_step_timer += ([sheet[j + 1][2].value], [sheet[j + 1][2].value + '-Вых'],)
                    # добавляем значение таймера в кортеж
                    tuple_step_timer_value += ([sheet[j + 1][1].value],)
                # Если на шаге не установлено таймера
                else:
                    # добавляем прочерк-текст таймера в кортеж русских таймеров
                    tuple_rus_step_timer += (['-'],)
                    # добавляем нулевое значение таймера в кортеж
                    tuple_step_timer_value += (['0.0'],)

                # Если на шаге указан дополнительный параметр(хотя бы один)
                if sheet[j + 1][5].value is not None and sheet[j + 1][5].value.replace('\n', ''):
                    # формируем словарь соответствий условие перехода: дополнительный параметр,
                    # чтобы правильно сформировать префиксы на конце
                    sl_dop_par_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'),
                                                   tuple(sheet[j + 1][5].value.split('\n')))))
                    # формируем словарь соответствий условие перехода: количество знаков после запятой,
                    # чтобы правильно сформировать префиксы на конце
                    tuple_tmp = [a[a.find('{')+1:a.find('}')] if '{' in a else '0'
                                 for a in sheet[j + 1][5].value.split('\n')]
                    sl_dop_par_fragdigits_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'), tuple_tmp)))

                # Если на шаге указан хотя бы один обратный таймер
                if sheet[j + 1][6].value is not None and sheet[j + 1][6].value.replace('\n', ''):
                    # формируем словарь соответствий условие перехода: обратный таймер,
                    # чтобы правильно сформировать префиксы на конце
                    sl_rev_timer_tmp.update(dict(zip(sheet[j + 1][4].value.split('\n'),
                                                     tuple(sheet[j + 1][6].value.split('\n')))))

            # Формируем алгоритмические имена шагов по правилам добавления префиксов на конце
            for a in range(len(tuple_rus_step)):
                for b in range(len(tuple_rus_step[a])):
                    step_out_tmp += (f"GRH|{mod_name}_Cmd_In_{p}_{a + 1}_{b + 1}",)
                    # если есть в словаре соответствий допонительных параметров
                    if sl_dop_par_tmp.get(tuple_rus_step[a][b]):
                        # то формируем кортеж алгоритмических имён
                        # дополнительных параметров по правилам добавления префиксов,
                        step_dop_par_out_tmp += (f"GRH|{mod_name}_Par_In_{p}_{a + 1}_{b + 1}",)
                        # также формируем кортеж с русским описанием дополнительных параметров
                        tuple_dop_par_rus += (f"Дополнительный параметр режима {mod_name} шага {p}",)
                        # также формируем кортеж с количеством знаков после запятой дополнительных параметров
                        step_dop_par_fragdigits_out_tmp += (sl_dop_par_fragdigits_tmp[tuple_rus_step[a][b]],)
                    # если есть в словаре соответствий обратных таймеров
                    if sl_rev_timer_tmp.get(tuple_rus_step[a][b]):
                        # формируем кортеж алгоритмических имён обратных таймеров
                        # по правилам добавления префиксов
                        step_rev_timer_out_tmp += (f"GRH|{mod_name}_Tmv_Rev_{p}_{a + 1}_{b + 1}",)
                        # также формируем кортеж с русским описанием обратных таймеров
                        tuple_rev_timer_rus += (f"Обратный таймер режима {mod_name} шага {p}",)

            # Формируем алгоритмические имена шагов для таймеров
            for a in range(len(tuple_step_timer_value)):
                # Если таймер ненулевой, то добавляем переменную для отображения
                if tuple_step_timer_value[a] != ['0.0']:
                    step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_In_{p}",)
                    step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_Out_{p}",)
                # Иначе просто добавляем переменную (возможно, незачем, но добавим!!!!!!!!!!!!!!!!!)
                else:
                    step_timer_out_tmp += (f"GRH|{mod_name}_Tmv_In_{p}",)

            # Если в шаге только одно условие, то "убиваем" два последние цифры иначе оставляем
            step_out_tmp = ((step_out_tmp[0][:-4],) if len(step_out_tmp) == 1 else step_out_tmp)

            # Если в словаре дополнительных параметров только один,
            # то "убиваем" два последние цифры иначе оставляем
            step_dop_par_out_tmp = ((step_dop_par_out_tmp[0][:-4],) if len(sl_dop_par_tmp) == 1
                                    else step_dop_par_out_tmp)

            # Если в словаре обратных таймеров только один,
            # то "убиваем" два последние цифры иначе оставляем
            step_rev_timer_out_tmp = ((step_rev_timer_out_tmp[0][:-4],) if len(sl_rev_timer_tmp) == 1
                                      else step_rev_timer_out_tmp)

            # Пока просто выводим в консоль для контроля, потом сформируем выход
            '''
            # Условия перехода
            print(f"{p} {[step for group_step in tuple_rus_step for step in group_step]}" if tuple_rus_step else '')
            print(f"{p} {step_out_tmp}" if step_out_tmp else '')
            print()
            # Таймера
            print(f"{p} {tuple_rus_step_timer}" if tuple_rus_step_timer else '')
            print(f"{p} {tuple_step_timer_value}" if tuple_step_timer_value else '')
            print(f"{p} {step_timer_out_tmp}" if step_timer_out_tmp else '')
            print()
            # Дополнительный параметры
            print(f"{p} {tuple_dop_par_rus}" if tuple_dop_par_rus else '')
            print(f"{p} {step_dop_par_out_tmp}" if step_dop_par_out_tmp else '')
            print(f"{p} {step_dop_par_fragdigits_out_tmp}" if step_dop_par_fragdigits_out_tmp else '')
            print()'''
            # Обратные таймера
            print(f"{p} {tuple_rev_timer_rus}" if tuple_rev_timer_rus else '')
            print(f"{p} {step_rev_timer_out_tmp}" if step_rev_timer_out_tmp else '')
            print()

        # print()
book.close()
