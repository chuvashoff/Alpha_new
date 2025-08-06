# import os
import os.path
import re
# import difflib
# from string import Template
# from my_func import *
import string
import sys

from func_for_v3 import *


def create_sl(text, str_check, str_check_block, par_config):
    sl_tmp = {}
    str_ch = str_check.replace('_', '|')
    for i in text:  # and str_check.replace('_', '|') not in i:
        if (str_check in i or str_ch in i) and '//' not in i and '(' not in i:
            if 'FAST|' in i and str_check_block in i:
                sl_tmp[i[:i.find(':=')].strip()] = int(i[i.rfind('[') + 1:i.rfind(']')])
            elif str_ch in i and str_check_block in i and not (f'B{str_ch}' in i or f'{str_ch}Brk' in i) \
                    and i.find('[') > i.find(':='):
                sl_tmp[i[:i.find(':=')].strip().replace('|', '_')] = int(i[i.rfind('[') + 1:i.rfind(']')])

    sl_tmp = {key: value for key, value in sl_tmp.items() if f'FAST|{key}' not in sl_tmp}
    # В словаре sl_tmp лежит индекс массива: алг имя (в том числе FAST|+)
    sl_tmp = {value: key for key, value in sl_tmp.items() if key.replace('FAST|', '') in par_config}
    return sl_tmp


def create_sl_im(text, par_config):
    sl_tmp = {}
    cnt_set = set()
    for i in text:
        if 'IM|' in i and '//' not in i and '[' in i and ':=' in i:
            a = i.split(':=')[0].strip()
            par_im = a[a.find('|')+1:a.rfind('_')]
            if par_im in par_config:
                sl_tmp[int(i[i.rfind('[') + 1:i.rfind(']')])] = par_im
        if '//' not in i and ('WorkTime' in i or 'Swap' in i):
            for word in i.split():
                word = word.strip()
                if 'WorkTime' in word or 'Swap' in word:
                    par_cnt = word.replace('IM|', '')
                    if par_cnt.replace('_Swap', '').replace('_WorkTime', '') in par_config:
                        cnt_set.add(word.replace('IM|', ''))
    # В словаре sl_tmp лежит индекс массива: алг имя; в cnt_set лежат используемые наработки
    return sl_tmp, cnt_set


def create_sl_pz(text):
    tmp_set = set()
    for i in text:
        if 'FAST|ALR_' in i and '//' not in i:
            a = i.split(':=')[0].strip()
            tmp_set.add(a[a.find('_') + 1:])
    # в множестве tmp_set лежат используемые аварии
    return tmp_set


def create_group_par(sl_global_par, sl_local_par, sl_global_fast, template_arc_index, template_no_arc_index,
                     pref_par, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global_par.items():
        tmp_i = int(key[key.find('[')+1:key.find(']')])
        tmp_sub_name = key[:key.find('[')]
        if tmp_i not in sl_local_par:
            continue
        if 'FAST|' in sl_local_par[tmp_i] and re.fullmatch(r'Value', key[:key.find('[')]):
            value[0] = sl_global_fast[sl_local_par[tmp_i]]
            a = sl_local_par[tmp_i][sl_local_par[tmp_i].find('|')+1:]
            temp = template_arc_index
            pref_arc = 'Arc'
        else:
            a = sl_local_par[tmp_i][sl_local_par[tmp_i].find('|')+1:]
            temp = template_no_arc_index
            pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(temp).substitute(name_signal=f'{pref_par}.{a}.{tmp_sub_name}', type_signal=sl_type[value[1]],
                                           index=value[0], data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_im(sl_global_im, sl_local_im, sl_global_fast, template_arc_index, template_no_arc_index, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global_im.items():
        tmp_i = int(key[key.find('[') + 1:key.find(']')])
        tmp_sub_name = key[:key.find('[')]
        if tmp_i not in sl_local_im:
            continue
        if f'FAST|IM_{sl_local_im[tmp_i]}_{tmp_sub_name}' in sl_global_fast:
            value[0] = sl_global_fast[f'FAST|IM_{sl_local_im[tmp_i]}_{tmp_sub_name}']
            a = sl_local_im[tmp_i]
            temp = template_arc_index
            pref_arc = 'Arc'
        elif f'FAST|AO_{sl_local_im[tmp_i]}_{tmp_sub_name}' in sl_global_fast:
            value[0] = sl_global_fast[f'FAST|AO_{sl_local_im[tmp_i]}_{tmp_sub_name}']
            a = sl_local_im[tmp_i]
            temp = template_arc_index
            pref_arc = 'Arc'
        else:
            a = sl_local_im[tmp_i]
            temp = template_no_arc_index
            pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(temp).substitute(name_signal=f'IM.{a}.{tmp_sub_name}', type_signal=sl_type[value[1]],
                                           index=value[0], data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_btn(sl_global_btn, sl_local_btn, template_no_arc_index, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global_btn.items():
        tmp_i = int(key[key.find('[') + 1:key.find(']')])
        tmp_sub_name = key[:key.find('[')]
        if tmp_i not in sl_local_btn:
            continue
        a = sl_local_btn[tmp_i]
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'System.BTN.{a}.{tmp_sub_name}',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_system_sig(sub_name, sl_global_sig, template_no_arc_index, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete',
        'M': 'Analog'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool',
        'M': 'String'
    }
    s_out = ''
    for key, value in sl_global_sig.items():
        a = key
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'  # для проекта Бованенково убрать '.Value'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'System.{sub_name}.{a}.Value',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_tr(sl_global, template_no_arc_index, pref_par, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global.items():
        a = key
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'{pref_par}.{a}',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_sar(sl_global, template_no_arc_index, pref_par, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global.items():
        a = key
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'{pref_par}.{a}',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_apr(sl_global, sl_global_fast, template_no_arc_index, template_arc_index, pref_par, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global.items():
        if f"FAST|AO_APR_{key[key.find('.')+1:]}" in sl_global_fast:
            value[0] = sl_global_fast[f"FAST|AO_APR_{key[key.find('.')+1:]}"]
            a = key
            temp = template_arc_index
            pref_arc = 'Arc'
        else:
            a = key
            temp = template_no_arc_index
            pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(temp).substitute(name_signal=f'{pref_par}.{a}',
                                           type_signal=sl_type[value[1]], index=value[0],
                                           data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_alr(sl_global_fast_alr, template_arc_index, source):
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global_fast_alr.items():
        a = key
        pref_arc = 'Arc'  # для проекта Бованенково убрать '.Value'
        s_out += Template(template_arc_index).substitute(name_signal=f'System.ALR.{a}.Value',
                                                         type_signal=sl_type[value[1]], index=value[0],
                                                         data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_pz(sl_global_pz, lst_pz, tuple_anum, template_no_arc_index, source):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    sl_pz_i = {}
    for i in range(len(sl_global_pz)//len(lst_pz)):
        lst_tmp = []  # В lst_tmp кладём списки [инд. переменной, тип] в соответствии с lst_pz -нужные подимена
        for j in lst_pz:
            lst_tmp.append(sl_global_pz[f'{j}[{i}]'])
        sl_pz_i[i] = dict(zip(lst_pz, lst_tmp))  # {индекс массива: {подимя: [инд. переменной, тип ]}}

    sl_pz = dict(zip(tuple_anum, sl_pz_i.values()))  # {Имя переменной(A000): {подимя: [инд. переменной, тип ]}}
    for key, value in sl_pz.items():
        for key_subname, value_subname in value.items():
            pref_arc = f'NoArc{sl_data_cat[value_subname[1]]}'
            s_out += Template(template_no_arc_index).substitute(name_signal=f'System.PZ.{key}.{key_subname}',
                                                                type_signal=sl_type[value_subname[1]],
                                                                index=value_subname[0],
                                                                data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_diag(diag_sl, template_no_arc_index, source, template_arc_index, sl_global_fast):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in diag_sl.items():
        module = key[0]
        signal = key[1]
        # if module in ('BR1', 'BR2'):
        #     print(module, signal, sl_global_fast)
        if f'FAST|{signal}' in sl_global_fast:
            temp = template_arc_index
            pref_arc = 'Arc'
            index = sl_global_fast[f'FAST|{signal}']
        else:
            temp = template_no_arc_index
            pref_arc = f'NoArc{sl_data_cat[value[1]]}'
            index = value[0]
        s_out += Template(temp).substitute(name_signal=f'Diag.HW.{module}.{signal}',
                                           type_signal=sl_type[value[1]], index=index,
                                           data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_drv(drv_sl, template_no_arc_index, source, sl_global_fast, template_arc_index, sl_drv_iec,
                     sl_global_drv_imit):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in drv_sl.items():
        name_drv = key[0]
        name_signal = key[1]
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'System.DRV.{name_drv}.{name_signal}.Value',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    # Для каждого параметра IEC в словаре IEC от драйверов...
    for iec_par, type_iec_par in sl_drv_iec.items():
        # ...при условии, что параметр есть в словаре FAST, то есть можно определить его индекс
        if f'FAST|{iec_par}' in sl_global_fast:
            s_out += Template(template_arc_index).substitute(name_signal=f'System.DRV.IEC.{iec_par}.Value',
                                                             type_signal=sl_type[type_iec_par],
                                                             index=sl_global_fast[f'FAST|{iec_par}'],
                                                             data_category=f'DataCategory_{source}_Arc')
    for key, value in sl_global_drv_imit.items():
        name_drv = key[0]
        post_signal = key[1] if key[1] else 'Value'
        name_signal = key[2]
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(
            name_signal=f'System.DRV.{name_drv}.{name_signal}.{post_signal}',
            type_signal=sl_type[value[1]], index=value[0],
            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_index(tuple_all_cpu, sl_sig_alg, sl_sig_mod, sl_sig_ppu, sl_sig_ts, sl_sig_wrn, sl_pz, sl_cpu_spec,
                 sl_for_diag, sl_cpu_drv_signal, sl_grh, sl_sig_alr, choice_tr, sl_cpu_drv_iec,
                 sl_ai_config, sl_ae_config, sl_di_config, sl_set_config, sl_btn_config, sl_im_config, sl_cpu_path,
                 buff_size, sl_cpu_drv_signal_with_imit, sl_cpu_cdo, sl_cpu_res: dict, sl_add_cpu_mko: dict,
                 sl_pru_config: dict, sl_need_add_pars: dict, sl_cpu_type_im: dict, sl_need_add_pars_struct: dict):

    tmp_ind_arc = '  <item Binding="Introduced">\n' \
                  '    <node-path>$name_signal</node-path>\n' \
                  '    <protocoltype>$type_signal</protocoltype>\n' \
                  '    <index>$index</index>\n' \
                  f'    <buffer-length>{buff_size}</buffer-length>\n' \
                  '    <archivation-period>1</archivation-period>\n' \
                  '    <category>$data_category</category>\n' \
                  '  </item>\n'
    tmp_ind_no_arc = '  <item Binding="Introduced">\n' \
                     '    <node-path>$name_signal</node-path>\n' \
                     '    <protocoltype>$type_signal</protocoltype>\n' \
                     '    <index>$index</index>\n' \
                     '    <category>$data_category</category>\n' \
                     '  </item>\n'
    dict_signal = dict()

    for file_signal in os.listdir(os.path.join('Template_Alpha', 'Systemach')):
        if file_signal.startswith('Signal_') and os.path.isfile(os.path.join('Template_Alpha', 'Systemach', file_signal)):
            #print(file_signal.replace('Signal_', 'lst_'))
            name_lst = file_signal.replace('Signal_', '').lower()
            if name_lst not in dict_signal:
                dict_signal[name_lst] = tuple()
            with open(os.path.join('Template_Alpha', 'Systemach', f'{file_signal}'), 'r', encoding='UTF-8') as f_signal:
                for line in f_signal:
                    if '#' in line:
                        continue
                    if not line.strip():
                        break
                    dict_signal[name_lst] += (line.strip(),)
    # lst_ae = tuple()
    # lst_ai = tuple()
    # lst_di = tuple()
    # lst_ai_di = tuple()
    # lst_im1x0 = tuple()
    # lst_im1x1 = tuple()
    # lst_im1x2 = tuple()
    # lst_im1x2pz = tuple()
    # lst_im2x2 = tuple()
    # lst_im_ao = tuple()
    # lst_btn = tuple()
    # lst_pz = tuple()
    # lst_set = tuple()
    # for file in ('Signal_ae', 'Signal_ai', 'Signal_di', 'Signal_ai_di', 'Signal_im1x0', 'Signal_im1x1', 'Signal_im1x2',
    #              'Signal_im2x2', 'Signal_imao', 'Signal_btn', 'Signal_pz', 'Signal_set', 'Signal_im1x2pz'):
    #     if os.path.exists(os.path.join('Template_Alpha', 'Systemach', f'{file}')):
    #         with open(os.path.join('Template_Alpha', 'Systemach', f'{file}'), 'r', encoding='UTF-8') as f_signal:
    #             for line in f_signal:
    #                 if '#' in line:
    #                     continue
    #                 if not line.strip():
    #                     break
    #                 if file == 'Signal_ae':
    #                     lst_ae += (line.strip(),)
    #                 elif file == 'Signal_ai':
    #                     lst_ai += (line.strip(),)
    #                 elif file == 'Signal_di':
    #                     lst_di += (line.strip(),)
    #                 elif file == 'Signal_ai_di':
    #                     lst_ai_di += (line.strip(),)
    #                 elif file == 'Signal_im1x0':
    #                     lst_im1x0 += (line.strip(),)
    #                 elif file == 'Signal_im1x1':
    #                     lst_im1x1 += (line.strip(),)
    #                 elif file == 'Signal_im1x2':
    #                     lst_im1x2 += (line.strip(),)
    #                 elif file == 'Signal_im1x2pz':
    #                     lst_im1x2pz += (line.strip(),)
    #                 elif file == 'Signal_im2x2':
    #                     lst_im2x2 += (line.strip(),)
    #                 elif file == 'Signal_imao':
    #                     lst_im_ao += (line.strip(),)
    #                 elif file == 'Signal_btn':
    #                     lst_btn += (line.strip(),)
    #                 elif file == 'Signal_pz':
    #                     lst_pz += (line.strip(),)
    #                 elif file == 'Signal_set':
    #                     lst_set += (line.strip(),)
    #     else:
    #         print(f'Не найден файл сигналов Template_Alpha/Systemach/{file}, '
    #               'сигналы в карту адресов добавлены не будут')

    sl_module_diag_sig = {}
    sl_module_diag_sig_conform = {}
    #   os.path.dirname(sys.argv[0])
    if os.path.exists(os.path.join(os.path.abspath(os.curdir), 'Template_Alpha', 'Systemach', 'Module_diag_signal')):
        for file in os.listdir(os.path.join(os.path.abspath(os.curdir), 'Template_Alpha',
                                            'Systemach', 'Module_diag_signal')):
            sl_module_diag_sig[file] = tuple()
            sl_module_diag_sig_conform[file] = {}
            with open(os.path.join('Template_Alpha', 'Systemach', 'Module_diag_signal', file),
                      'r', encoding='UTF-8') as f_signal:
                for line in f_signal:
                    if '#' in line:
                        continue
                    if not line.strip():
                        break
                    if ':' not in line.strip():
                        sl_module_diag_sig[file] += (line.strip(),)
                    else:
                        s = line.strip()
                        key = s[:s.find(':')].strip()
                        value = s[s.find(':')+1:].strip()
                        sl_module_diag_sig[file] += (key,)
                        sl_module_diag_sig_conform[file].update({key: value})
    else:
        print(f'Не найдена папка сигналов модулей Template_Alpha/Systemach/Module_diag_signal, '
              'сигналы модулей не будут добавлены в карту адресов')

    sl_diag_cpu_sig = {}
    # print(sl_module_diag_sig_conform)
    #  os.path.dirname(sys.argv[0])

    for file in os.listdir(os.path.join(os.path.abspath(os.curdir), 'Template_Alpha', 'Systemach', 'cpu')):
        if file.startswith('Signal_cpu_'):
            name_cpu = file.replace('Signal_cpu_', '')
            sl_diag_cpu_sig[name_cpu] = {}
            with open(os.path.join(os.path.abspath(os.curdir), 'Template_Alpha', 'Systemach', 'cpu', file), 'r',
                      encoding='UTF-8') as f_signal:
                for line in f_signal:
                    if '#' in line:
                        continue
                    if not line.strip():
                        break
                    key = line[:line.find(':')].strip()
                    value = line[line.find(':')+1:].strip()
                    sl_diag_cpu_sig[name_cpu].update({key: value})

    progress_index = len(sl_cpu_path)
    progress_bar = ' ' * 100
    progress_percent = 0
    for cpu, path in sl_cpu_path.items():
        # Если нет папки контроллера, то сообщаем об этом юзеру и идём дальше
        if path is None or not path:
            print(f"НЕ УКАЗАНА ПАПКА ПРОЕКТА КОНТРОЛЛЕРА {cpu}, КАРТА АДРЕСОВ НЕ БУДЕТ ОБНОВЛЕНА")
            continue
        if not os.path.exists(path):
            print(f"НЕ НАЙДЕНА ПАПКА ПРОЕКТА КОНТРОЛЛЕРА {cpu}, КАРТА АДРЕСОВ НЕ БУДЕТ ОБНОВЛЕНА")
            continue
        else:
            line_source = [cpu.strip(), path.strip()]
            if cpu not in tuple_all_cpu:
                continue
            sl_global_ai, sl_tmp_ai = {}, {}
            sl_global_ae, sl_tmp_ae = {}, {}
            sl_global_di, sl_tmp_di, sl_wrn_di = {}, {}, {}  # sl_wrn_di - для сбора ПС по Дискретам
            sl_global_ai_di, sl_tmp_ai_di = {}, {}
            sl_global_im1x0, sl_tmp_im1x0 = {}, {}
            sl_global_im1x1, sl_tmp_im1x1 = {}, {}
            sl_global_im1x2, sl_tmp_im1x2 = {}, {}
            sl_global_im1x2pz, sl_tmp_im1x2pz = {}, {}
            sl_global_im2x2, sl_tmp_im2x2 = {}, {}
            sl_global_im_ao, sl_tmp_im_ao = {}, {}
            sl_global_btn, sl_tmp_btn = {}, {}
            sl_global_set, sl_tmp_set = {}, {}
            sl_global_cnt = {}
            set_all_im = set()  # sl_all_im - для ИМ с наработками
            set_cnt_im1x0, set_cnt_im1x1, set_cnt_im1x2, set_cnt_im2x2 = set(), set(), set(), set()
            set_cnt_im1x2pz = set()
            sl_global_fast_alr = {}
            set_tmp_alr = set()
            test_sl_global_as = {}
            sl_global_alg = {}
            sl_global_mod = {}
            sl_global_ppu = {}
            sl_global_ts = {}
            sl_global_wrn = {}
            sl_global_pz = {}
            sl_global_fast = {}
            s_all = ''

            lst_tr_par = []
            lst_tr_par_lower = []
            lst_apr_par = []
            lst_apr_par_lower = []
            sl_global_tr = {}
            sl_global_apr = {}
            sl_global_diag = {}
            sl_global_drv = {}
            sl_global_drv_imit = {}

            sl_global_grh = {}
            sl_sar_tun = {}
            sl_global_sar = {}
            sl_global_cdo = {}
            sl_global_pru = {}
            sl_add_par = {}
            sl_add_par_struct = {}

            if 'ТР' in sl_cpu_spec.get(line_source[0], 'бла') and os.path.exists(os.path.join('Template_Alpha', 'TR',
                                                                                              f'TR_par_{choice_tr}')):
                with open(os.path.join('Template_Alpha', 'TR', f'TR_par_{choice_tr}'), 'r', encoding='UTF-8') as f_tr:
                    lst_tr_par = [i for i in f_tr.read().split('\n') if i and '#' not in i]
                    # Получаем нижний регистр топливных переменных для дальнейшей проверки
                    lst_tr_par_lower = [a.lower() for a in lst_tr_par]
            if 'АПР' in sl_cpu_spec.get(line_source[0], 'бла') and os.path.exists(os.path.join('Template_Alpha', 'APR',
                                                                                               'APR_par')):
                with open(os.path.join('Template_Alpha', 'APR', 'APR_par'), 'r', encoding='UTF-8') as f_:
                    lst_apr_par = [i for i in f_.read().split('\n') if i and '#' not in i]
                    # Получаем нижний регистр переменных АПР для дальнейшей проверки
                    lst_apr_par_lower = [a.lower() for a in lst_apr_par]
            if 'САР' in sl_cpu_spec.get(line_source[0], 'бла'):
                # Tuning
                if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'Tun_SAR.txt')):
                    with open(os.path.join('Template_Alpha', 'SAR', 'Tun_SAR.txt'), 'r', encoding='UTF-8') as f_:
                        for line in f_:
                            if '#' in line:
                                continue
                            if not line.strip():
                                break
                            sl_sar_tun[line.strip().split(';')[2].lower()] = line.strip().split(';')[0]
                # REGUL
                if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'REGUL')):
                    with open(os.path.join('Template_Alpha', 'SAR', 'REGUL'), 'r', encoding='UTF-8') as f_:
                        for line in f_:
                            if '#' in line:
                                continue
                            if not line.strip():
                                break
                            sl_sar_tun[f"{line.strip().split(';')[0].lower()}.REGUL"] = line.strip().split(';')[1]
                # WRN
                if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'WRN')):
                    with open(os.path.join('Template_Alpha', 'SAR', 'WRN'), 'r', encoding='UTF-8') as f_:
                        for line in f_:
                            if '#' in line:
                                continue
                            if not line.strip():
                                break
                            sl_sar_tun[f"{line.strip().split(';')[0].lower()}.WRN"] = line.strip().split(';')[1]
                # Signal_KHR
                if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'Signal_KHR')):
                    with open(os.path.join('Template_Alpha', 'SAR', 'Signal_KHR'), 'r', encoding='UTF-8') as f_:
                        for line in f_:
                            if '#' in line:
                                continue
                            if not line.strip():
                                break
                            sl_sar_tun[f"{line.strip().split(';')[0].lower()}.Signal_KHR"] = line.strip().split(';')[1]
                # Reload
                if os.path.exists(os.path.join('Template_Alpha', 'SAR', 'Reload_checkbox')):
                    with open(os.path.join('Template_Alpha', 'SAR', 'Reload_checkbox'), 'r', encoding='UTF-8') as f_:
                        for line in f_:
                            if '#' in line:
                                continue
                            if not line.strip():
                                break
                            sl_sar_tun[f"{line.strip().split(';')[0].lower()}.Reload"] = line.strip().split(';')[1]

            # Если есть файл аналогов
            if sl_ai_config.get(line_source[0]) and os.path.exists(os.path.join(line_source[1], '0_par_A.st')):
                with open(os.path.join(line_source[1], '0_par_A.st'), 'rt') as f_par_a:
                    text = f_par_a.read().split('\n')
                sl_tmp_ai = create_sl(text, 'AI_', 'A_INP|', par_config=sl_ai_config.get(line_source[0], tuple()))

            # Если есть файл расчётных
            if sl_ae_config.get(line_source[0]) and os.path.exists(os.path.join(line_source[1], '0_par_Evl.st')):
                with open(os.path.join(line_source[1], '0_par_Evl.st'), 'rt') as f_par_evl:
                    text = f_par_evl.read().split('\n')
                sl_tmp_ae = create_sl(text, 'AE_', 'A_EVL|', par_config=sl_ae_config.get(line_source[0], tuple()))

            # Если есть файл дискретных
            if sl_di_config.get(line_source[0]) and os.path.exists(os.path.join(line_source[1], '0_par_D.st')):
                with open(os.path.join(line_source[1], '0_par_D.st'), 'rt') as f_par_d:
                    text = f_par_d.read().split('\n')
                sl_tmp_di = create_sl(text, 'DI_', 'D_INP|', par_config=sl_di_config.get(line_source[0], tuple()))
                sl_tmp_ai_di = create_sl(text, 'DI_', 'D_INP_AI|', par_config=sl_di_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_1x0
            if {'IM1x0', 'IM1x0inv'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_1x0.st')):
                with open(os.path.join(line_source[1], '0_IM_1x0.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im1x0, set_cnt_im1x0 = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_1x1
            if {'IM1x1', 'IM1x1inv'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_1x1.st')):
                with open(os.path.join(line_source[1], '0_IM_1x1.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im1x1, set_cnt_im1x1 = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_1x2
            if {'IM1x2', 'IM1x2inv'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_1x2.st')):
                with open(os.path.join(line_source[1], '0_IM_1x2.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im1x2, set_cnt_im1x2 = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_1x2pz
            if {'IM1x2pz'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_1x2pz.st')):
                with open(os.path.join(line_source[1], '0_IM_1x2pz.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im1x2pz, set_cnt_im1x2pz = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_2x2
            if {'IM2x2', 'IM2x4', 'IM2x2PCH'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_2x2.st')):
                with open(os.path.join(line_source[1], '0_IM_2x2.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im2x2, set_cnt_im2x2 = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл ИМ_АО
            if {'IM_AO'} & sl_cpu_type_im.get(line_source[0], set()) and os.path.exists(os.path.join(line_source[1], '0_IM_AO.st')):
                with open(os.path.join(line_source[1], '0_IM_AO.st'), 'rt') as f_im:
                    text = f_im.read().split('\n')
                sl_tmp_im_ao, bla_ = create_sl_im(text, par_config=sl_im_config.get(line_source[0], tuple()))

            # Если есть файл кнопок
            if sl_btn_config.get(line_source[0]) and os.path.exists(os.path.join(line_source[1], '0_BTN.st')):
                with open(os.path.join(line_source[1], '0_BTN.st'), 'rt') as f_btn:
                    text = f_btn.read().split('\n')
                tuple_btn_config = sl_btn_config.get(line_source[0], tuple())
                for i in text:
                    if 'BTN_' in i and '(' in i:
                        a = i.split(',')[0]
                        par_btn = a[:a.find('(')].strip()
                        if par_btn in tuple_btn_config:
                            sl_tmp_btn[int(a[a.find('(')+1:].strip())] = par_btn

            # Если есть файл защит PZ
            if os.path.exists(os.path.join(line_source[1], '0_PZ.st')):
                with open(os.path.join(line_source[1], '0_PZ.st'), 'rt') as f_pz:
                    text = f_pz.read().split('\n')
                set_tmp_alr = create_sl_pz(text)

            # Если есть файл уставок
            if sl_set_config.get(line_source[0]) and os.path.exists(os.path.join(line_source[1], '0_Par_Set.st')):
                with open(os.path.join(line_source[1], '0_Par_Set.st'), 'rt') as f_set:
                    text = f_set.read().split('\n')
                sl_tmp_set = create_sl(text, 'SP_', 'A_SET|', par_config=sl_set_config.get(line_source[0], tuple()))

            # Если есть глобальный словарь
            if os.path.exists(os.path.join(line_source[1], 'global0.var')):
                with open(os.path.join(line_source[1], 'global0.var'), 'rt') as f_global:
                    for line in f_global:
                        line = line.strip()

                        # Определяем добавляемые неархивируемые теги, если таковые нужны
                        if len(line.split(',')) >= 10 and sl_need_add_pars_struct.get(line_source[0]):
                            tmp_var_may_be_fb = get_variable(line=line)
                            if tmp_var_may_be_fb in sl_need_add_pars_struct.get(line_source[0]):
                                index_par_fb = line[:line.find(',//')].split(',')[-8]
                                type_sig_fb = line.split(',')[1]
                                # print(tmp_var_may_be_fb, index_par, type_sig)
                                sl_add_par_struct[f"System.{tmp_var_may_be_fb.replace('|', '.')}"] = (index_par_fb, type_sig_fb)

                        # Получаем сигналы SARa
                        if sl_sar_tun and len(line.split(',')) >= 10:
                            # Получаем переменную
                            tmp_var = get_variable_lower(line=line)
                            if tmp_var in sl_sar_tun:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_sar = line.split(',')
                                sl_global_sar[f'Tuning.{sl_sar_tun[tmp_var]}.Value'] = [index_par, line_sar[1]]

                            elif f'{tmp_var}.REGUL' in sl_sar_tun:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_sar = line.split(',')
                                tm = sl_sar_tun[f'{tmp_var}.REGUL']
                                sl_global_sar[f'REGUL.{tm}'] = [index_par, line_sar[1]]
                            elif f'{tmp_var}.WRN' in sl_sar_tun:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_sar = line.split(',')
                                tm = sl_sar_tun[f'{tmp_var}.WRN']
                                sl_global_sar[f'WRN.{tm}'] = [index_par, line_sar[1]]
                            elif f'{tmp_var}.Signal_KHR' in sl_sar_tun:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_sar = line.split(',')
                                tm = sl_sar_tun[f'{tmp_var}.Signal_KHR']
                                sl_global_sar[f'IM.KHR.{tm}'] = [index_par, line_sar[1]]
                            elif f'{tmp_var}.Reload' in sl_sar_tun:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_sar = line.split(',')
                                tm = sl_sar_tun[f'{tmp_var}.Reload']
                                sl_global_sar[f'Reload.{tm}.Value'] = [index_par, line_sar[1]]

                        # Получаем сигналы топливного регулятора
                        if lst_tr_par and len(line.split(',')) >= 10:
                            # Получаем переменную в нижнем регистре и с разделителем
                            tmp_var = get_variable_lower(line=line)
                            # Делим по разделителю
                            lst_tmp_var = tmp_var.split('|')
                            # Если есть разделитель...
                            if len(lst_tmp_var) == 2:
                                # ...то у папки удаляем в конце цифры
                                lst_tmp_var[0] = lst_tmp_var[0].rstrip(string.digits)
                                # Выясняем, что за переменная в перечне и вносим в словарь и есть ли она
                                if '.'.join(lst_tmp_var) in lst_tr_par_lower:
                                    index_lst = lst_tr_par_lower.index('.'.join(lst_tmp_var))
                                    index_par = line[:line.find(',//')].split(',')[-8]
                                    line_tr = line.split(',')
                                    sl_global_tr[lst_tr_par[index_lst]] = [index_par, line_tr[1]]

                        # Ищем переменные диагностики контроллера помимо каталога DIAG|
                        if len(line.split(',')) >= 10:
                            # Получаем переменную с разделителем
                            tmp_var = get_variable(line=line)
                            # Если переменная есть в списке сигналов контроллера
                            # По сути ищем переменные контроллера без разделителей в глобальном словаре
                            type_cpu = sl_for_diag[line_source[0]]['CPU'][1] + '_Res' if \
                                sl_for_diag[line_source[0]]['CPU'][0] in sl_cpu_res.get(line_source[0], 'бла') \
                                else sl_for_diag[line_source[0]]['CPU'][1]
                            if sl_for_diag.get(line_source[0]) and \
                                    tmp_var in sl_diag_cpu_sig.get(type_cpu, {}):
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_diag = line.split(',')
                                module_cpu = sl_for_diag[line_source[0]]['CPU'][0]
                                tag_name = sl_diag_cpu_sig[type_cpu][tmp_var]
                                # (алг.имя CPU, имя пер-через словарь соответствия) : [инд. пер, тип пер]
                                sl_global_diag[(module_cpu, tag_name)] = [index_par, line_diag[1]]

                            # Анализируем фасты на тот случай, если сигнал диагностики ТОЛЬКО фастовый
                            tmp_var_fast = tmp_var.replace('FAST|', '') if tmp_var.startswith('FAST|') else ''
                            if sl_for_diag.get(line_source[0]) and tmp_var_fast and \
                                    tmp_var_fast in sl_diag_cpu_sig.get(type_cpu, {}):
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_diag = line.split(',')
                                module_cpu = sl_for_diag[line_source[0]]['CPU'][0]
                                tag_name = sl_diag_cpu_sig[type_cpu][tmp_var_fast]
                                # (алг.имя CPU, имя пер-через словарь соответствия) : [инд. пер, тип пер]
                                sl_global_diag[(module_cpu, tag_name)] = [index_par, line_diag[1]]

                        # Ищем переменные ПРУ
                        # print(sl_pru_config.get(line_source[0]))
                        if sl_pru_config.get(line_source[0]) and len(line.split(',')) >= 10:
                            # Получаем переменную с разделителем
                            tmp_var = get_variable(line=line)
                            if tmp_var.replace('|', '_', 1) in sl_pru_config[line_source[0]]:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line_pru = line.split(',')
                                sl_global_pru[tmp_var.replace('|', '_', 1)] = [index_par, line_pru[1]]

                        if 'A_INP|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_ai[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_ai['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'A_EVL|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_ae[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_ae['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'D_INP|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_di[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_di['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'D_INP_AI|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_ai_di[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_ai_di['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_1x0|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im1x0[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im1x0['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_1x1|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im1x1[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im1x1['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_1x2|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im1x2[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im1x2['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_1x2pz|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im1x2pz[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im1x2pz['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_2x2|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im2x2[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im2x2['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'IM_AO|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'msg' not in line[0]:
                                sl_global_im_ao[line[0][line[0].find('|')+1:]] = [index_par, line[1]]
                            else:
                                sl_global_im_ao['Message.' + line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'BTN|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_btn[line[0][line[0].find('|')+1:]] = [index_par, line[1]]

                        elif 'IM|' in line and len(line.split(',')) >= 10 and ('WorkTime' in line or 'Swap' in line):
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_cnt[line[0][line[0].find('|')+1:]] = [index_par, line[1]]

                        elif 'FAST|ALR_' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line_alr = line.split(',')
                            sl_global_fast_alr[line_alr[0][line_alr[0].find('_')+1:]] = [index_par, line_alr[1]]

                        elif 'ALG|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_alg[f"ALG_{line[0][line[0].find('|')+1:]}"] = [index_par, line[1]]

                        elif 'GRH|' in line and len(line.split(',')) >= 10:  # в новом конфигураторе - в ветку GRH.
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_grh[f"{line[0][1:]}"] = [index_par, line[1]]

                        elif 'MOD|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if 'regnum' in line[0][line[0].find('|') + 1:].lower():
                                sl_global_mod['regNum'] = [index_par, line[1]]
                            elif 'regname' in line[0][line[0].find('|') + 1:].lower():
                                sl_global_mod['regName'] = [index_par, line[1]]
                            elif 'regcolor' in line[0][line[0].find('|') + 1:].lower():
                                sl_global_mod['regColor'] = [index_par, line[1]]
                            else:
                                sl_global_mod[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'PPU|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_ppu[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'TS|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_ts[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'WRN|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_wrn[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'MOD_PZ|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_pz[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        elif 'A_SET|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_set[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        # elif ('svk2|' in line or 'svk|' in line) and len(line.split(',')) >= 10:
                        #     line = line.split(',')
                        #     if f"SVK.{line[0][line[0].find('|') + 1:]}" in lst_tr_par:
                        #         sl_global_tr[f"SVK.{line[0][line[0].find('|') + 1:]}"] = [max(int(line[9]),
                        #                                                                       int(line[10])),
                        #                                                                   line[1]]
                        #
                        # elif 'dis|' in line and len(line.split(',')) >= 10:
                        #     line = line.split(',')
                        #     if f"DIS.{line[0][line[0].find('|') + 1:]}" in lst_tr_par:
                        #         sl_global_tr[f"DIS.{line[0][line[0].find('|') + 1:]}"] = [max(int(line[9]),
                        #                                                                       int(line[10])),
                        #                                                                   line[1]]
                        elif 'APR|' in line and len(line.split(',')) >= 10:
                            # Получаем переменную в нижнем регистре и с разделителем и убираем "мусор"
                            tmp_var = get_variable_lower(line=line).replace('[', '').replace(']', '').replace('apr|',
                                                                                                              '')
                            # Если переменная есть в перечне и выясняем что, за переменная и добавляем в словарь
                            if tmp_var in lst_apr_par_lower:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line = line.split(',')
                                index_lst = lst_apr_par_lower.index(tmp_var)
                                key_apr = f"IM.{lst_apr_par[index_lst]}"
                                sl_global_apr[key_apr] = [index_par, line[1]]
                            # line = line.split(',')
                            # if line[0][line[0].find('|') + 1:].replace('[', '').replace(']', '') in lst_apr_par:
                            #     key_apr = f"IM.{line[0][line[0].find('|') + 1:].replace('[', '').replace(']', '')}"
                            #     sl_global_apr[key_apr] = [max(int(line[9]), int(line[10])), line[1]]

                        elif 'sTunings|' in line and len(line.split(',')) >= 10:
                            # Получаем переменную в нижнем регистре и с разделителем и добавляем перфикс тюнинга
                            tmp_var = get_variable_lower(line=line).replace('stunings|', 'tuning.')
                            # Если переменная есть в перечне и выясняем что, за переменная и добавляем в словарь
                            if tmp_var in lst_apr_par_lower:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line = line.split(',')
                                index_lst = lst_apr_par_lower.index(tmp_var)
                                key_apr = f"{lst_apr_par[index_lst]}.Value"
                                sl_global_apr[key_apr] = [index_par, line[1]]
                            # line = line.split(',')
                            # if f"Tuning.{line[0][line[0].find('|') + 1:]}" in lst_apr_par:
                            #     key_apr = f"Tuning.{line[0][line[0].find('|') + 1:]}.Value"
                            #     sl_global_apr[key_apr] = [max(int(line[9]), int(line[10])), line[1]]
                        elif 'SRCalc' in line and len(line.split(',')) >= 10:
                            # Получаем переменную в нижнем регистре и с разделителем и добавляем перфикс тюнинга
                            tmp_var = get_variable_lower(line=line).replace('srcalc|', 'srcalc.')
                            if tmp_var in lst_apr_par_lower:
                                index_par = line[:line.find(',//')].split(',')[-8]
                                line = line.split(',')
                                index_lst = lst_apr_par_lower.index(tmp_var)
                                key_apr = f"IM.{lst_apr_par[index_lst]}"
                                sl_global_apr[key_apr] = [index_par, line[1]]

                        elif 'DIAG|' in line and len(line.split(',')) >= 10:
                            # Получаем диагностику CPU из группы DIAG
                            var_name = get_variable(line=line).replace('DIAG|', '')
                            type_cpu = sl_for_diag[line_source[0]]['CPU'][1] + '_Res' if \
                                sl_for_diag[line_source[0]]['CPU'][0] in sl_cpu_res.get(line_source[0], 'бла') \
                                else sl_for_diag[line_source[0]]['CPU'][1]
                            if sl_for_diag.get(line_source[0]) and \
                                    var_name in sl_diag_cpu_sig.get(type_cpu, {}):
                                module_cpu = sl_for_diag[line_source[0]]['CPU'][0]
                                signal_name = sl_diag_cpu_sig[type_cpu][var_name]
                                # (алг.имя CPU, имя пер-через словарь соответствия) : [инд. пер, тип пер]
                                index_par = line[:line.find(',//')].split(',')[-8]
                                sl_global_diag[(module_cpu, signal_name)] = [index_par, line.split(',')[1]]
                            else:
                                # Анализируем переменные узла DIAG на предмет привязки к модулям в/в
                                for alg_module in sl_for_diag.get(line_source[0], {}):
                                    if var_name.endswith(alg_module):
                                        signal = var_name.replace(alg_module, '').rstrip('_')
                                        if signal in sl_module_diag_sig.get(sl_for_diag[line_source[0]][alg_module],
                                                                            'бла'):
                                            # print(signal, var_name)
                                            index_par = line[:line.find(',//')].split(',')[-8]
                                            # Проверяем наличие сигнала в словаре соответствия
                                            if sl_module_diag_sig_conform.get(sl_for_diag[line_source[0]][alg_module]) \
                                                    and sl_module_diag_sig_conform[sl_for_diag[line_source[0]][alg_module]].get(signal):
                                                signal_in = sl_module_diag_sig_conform[sl_for_diag[line_source[0]][alg_module]].get(signal)
                                            else:
                                                signal_in = signal
                                            sl_global_diag[(alg_module, signal_in)] = [index_par, line.split(',')[1]]

                        elif 'ALR|' in line and 'ALR|Delay' not in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            tmp_alg_alr = line[0][1:]  # c префиксом ALR|
                            alg_alr = tmp_alg_alr[tmp_alg_alr.find('|')+1:]  # без префикса ALR|
                            # Если текущий контроллер есть в словаре из конфигуратора...
                            if line_source[0] in sl_sig_alr:
                                # ...если ALRка есть в перечне ALRов контроллера из конфигуратора и нет в PZ
                                if alg_alr in sl_sig_alr.get(line_source[0], 'бла') and alg_alr not in set_tmp_alr:
                                    # ...то считаем, что это АС и добавляем в словарь
                                    test_sl_global_as[alg_alr] = [index_par, line[1]]

                        elif 'CDO|' in line and len(line.split(',')) >= 10:
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            sl_global_cdo[line[0][line[0].find('|') + 1:]] = [index_par, line[1]]

                        # если в текущем контроллере объявлены драйвера и строка явно содержит индекс
                        elif line_source[0] in sl_cpu_drv_signal and len(line.split(',')) >= 10:
                            tmp_check = line.split(',')[0]
                            # если в считанной строке-переменной есть признак какого-либо драйвера
                            if tmp_check[1:tmp_check.find('|')] in sl_cpu_drv_signal.get(line_source[0], 'бла'):
                                tmp_check_drv = tmp_check[1:tmp_check.find('|')]
                                tmp_check_par = tmp_check[tmp_check.find('|') + 1:]
                                # если в считанной строке с признаком драйвера обнаружена объявленная переменная
                                if tmp_check_par in sl_cpu_drv_signal[line_source[0]][tmp_check_drv] and \
                                        tmp_check_par not in sl_cpu_drv_signal_with_imit[line_source[0]][tmp_check_drv]:
                                    index_par = line[:line.find(',//')].split(',')[-8]
                                    sl_global_drv[(tmp_check_drv, tmp_check_par)] = (index_par, line.split(',')[1])
                                else:
                                    # Если драйверная переменная выставлена в конфигураторе без имитации, то выставляем
                                    for pref in ('', 'coSim_', 'Sim_'):
                                        if tmp_check_par.startswith(pref) and \
                                                tmp_check_par.replace(pref, '') in \
                                                sl_cpu_drv_signal_with_imit[line_source[0]][tmp_check_drv]:
                                            index_par = line[:line.find(',//')].split(',')[-8]
                                            sl_global_drv_imit[(tmp_check_drv, pref[:-1],
                                                                tmp_check_par.replace(pref, ''))] = \
                                                (index_par,
                                                 line.split(',')[1])

                        # Обрабатываем need_add (пока только по ветке FAST)
                        if sl_need_add_pars.get(line_source[0]) and 'FAST|' in line:
                            tmp_var = get_variable(line=line).replace('FAST|', '')
                            if tmp_var in sl_need_add_pars.get(line_source[0]):
                                index_par = line[:line.find(',//')].split(',')[-8]
                                type_sig = line.split(',')[1]
                                # print(tmp_var, index_par, type_sig)
                                sl_add_par[f'System.Pars.{tmp_var}'] = (index_par, type_sig)

                        if 'FAST|' in line:
                            tmp_var = get_variable(line=line)
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            # В словаре sl_global_fast лежит  алг имя(FAST|): индекс переменной
                            sl_global_fast[line[0][1:]] = index_par
                            # Ищем переменные контроллеров в FAST
                            type_cpu = sl_for_diag[line_source[0]]['CPU'][1] + '_Res' if \
                                sl_for_diag[line_source[0]]['CPU'][0] in sl_cpu_res.get(line_source[0], 'бла') \
                                else sl_for_diag[line_source[0]]['CPU'][1]
                            if sl_for_diag.get(line_source[0]) and tmp_var.replace('FAST|', '') \
                                    in sl_diag_cpu_sig.get(type_cpu, {}):
                                sl_global_fast[tmp_var] = index_par

            # В словаре sl_global_ai лежит подимя[индекс массива]: [индекс переменной, тип переменной(I, B, R)]
            sl_global_ai = {key: value for key, value in sl_global_ai.items() if key[:key.find('[')] in dict_signal.get('ai', '')}
            sl_global_ae = {key: value for key, value in sl_global_ae.items() if key[:key.find('[')] in dict_signal.get('ae', '')}
            for key, value in sl_global_di.items():
                if 'ValueAlg' == key[:key.find('[')]:
                    var_ = sl_tmp_di.get(int(key[key.find('[')+1:key.find(']')]), 'bla')
                    if f"DI_{var_[var_.find('_')+1:]}" in sl_sig_wrn.get(line_source[0], 'бла'):
                        sl_wrn_di[f"DI_{var_[var_.find('_')+1:]}"] = value
            for key, value in sl_global_ai_di.items():
                if 'ValueAlg' == key[:key.find('[')]:
                    var_ = sl_tmp_ai_di.get(int(key[key.find('[')+1:key.find(']')]), 'bla')
                    if f"DI_{var_[var_.find('_')+1:]}" in sl_sig_wrn.get(line_source[0], 'бла'):
                        sl_wrn_di[f"DI_{var_[var_.find('_')+1:]}"] = value

            sl_global_di = {key: value for key, value in sl_global_di.items() if key[:key.find('[')] in dict_signal.get('di', '')}
            sl_global_ai_di = {key: value for key, value in sl_global_ai_di.items() if key[:key.find('[')] in dict_signal.get('ai_di', '')}
            sl_global_im1x0 = {key: value for key, value in sl_global_im1x0.items() if key[:key.find('[')] in dict_signal.get('im1x0', '')}
            sl_global_im1x1 = {key: value for key, value in sl_global_im1x1.items() if key[:key.find('[')] in dict_signal.get('im1x1', '')}
            sl_global_im1x2 = {key: value for key, value in sl_global_im1x2.items() if key[:key.find('[')] in dict_signal.get('im1x2', '')}
            sl_global_im1x2pz = {key: value for key, value in sl_global_im1x2pz.items() if key[:key.find('[')] in dict_signal.get('im1x2pz', '')}
            sl_global_im2x2 = {key: value for key, value in sl_global_im2x2.items() if key[:key.find('[')] in dict_signal.get('im2x2', '')}
            sl_global_im_ao = {key: value for key, value in sl_global_im_ao.items() if key[:key.find('[')] in dict_signal.get('imao', '')}
            sl_global_btn = {key: value for key, value in sl_global_btn.items() if key[:key.find('[')] in dict_signal.get('btn', '')}
            sl_global_pz = {key: value for key, value in sl_global_pz.items() if key[:key.find('[')] in dict_signal.get('pz', '')}
            sl_global_set = {key: value for key, value in sl_global_set.items() if key[:key.find('[')] in dict_signal.get('set', '')}
            # отсюда и далее до нар ориентируемся на то, что есть в конфигураторе, так как в проекте может быть "мусор"
            # в данных словарях лежит alg имя: [индекс переменной, тип переменной(I, B, R)]
            sl_global_alg = {key: value for key, value in sl_global_alg.items()
                             if key in sl_sig_alg.get(line_source[0], 'бла')}
            # формирование словаря sl_global_grh добавлено позже для создания алгоритма в новом конфигураторе
            sl_global_grh = {key[key.find('|') + 1:]: value for key, value in sl_global_grh.items()
                             if key in sl_grh.get(line_source[0], 'бла')}
            sl_global_mod = {key: value for key, value in sl_global_mod.items()
                             if key in sl_sig_mod.get(line_source[0], 'бла')}
            sl_global_ppu = {key: value for key, value in sl_global_ppu.items()
                             if key in sl_sig_ppu.get(line_source[0], 'бла')}
            sl_global_ts = {key: value for key, value in sl_global_ts.items()
                            if key in sl_sig_ts.get(line_source[0], 'бла')}
            sl_global_wrn = {key: value for key, value in sl_global_wrn.items()
                             if key in sl_sig_wrn.get(line_source[0], 'бла')}
            sl_global_wrn.update(sl_wrn_di)

            sl_global_cdo = {key: value for key, value in sl_global_cdo.items()
                             if key in sl_cpu_cdo.get(line_source[0], 'бла')}

            # print(line_source[0], len(sl_global_pz))
            # Объединяем множества ИМ в одно для накопления наработок
            for jj in [set_cnt_im1x0, set_cnt_im1x1, set_cnt_im1x2, set_cnt_im2x2, set_cnt_im1x2pz]:
                set_all_im.update(jj)
            sl_global_cnt = {key: value for key, value in sl_global_cnt.items() if key in set_all_im}

            sl_global_fast_alr = {key: value for key, value in sl_global_fast_alr.items() if key in set_tmp_alr}

            # Обработка и запись в карту аналогов
            if sl_global_ai and sl_tmp_ai:
                s_all += create_group_par(sl_global_ai, sl_tmp_ai, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                          'AI', line_source[0])

            # Обработка и запись в карту расчётных
            if sl_global_ae and sl_tmp_ae:
                s_all += create_group_par(sl_global_ae, sl_tmp_ae, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                          'AE', line_source[0])

            # Обработка и запись в карту дискретных
            if sl_global_di and sl_tmp_di:
                s_all += create_group_par(sl_global_di, sl_tmp_di, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                          'DI', line_source[0])

            # Обработка и запись в карту дискретных аналогов (ai_di)
            if sl_global_ai_di and sl_tmp_ai_di:
                s_all += create_group_par(sl_global_ai_di, sl_tmp_ai_di, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                          'DI', line_source[0])

            # Обработка и запись в карту ИМ1x0

            if sl_global_im1x0 and sl_tmp_im1x0:
                s_all += create_group_im(sl_global_im1x0, sl_tmp_im1x0, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту ИМ1x1
            if sl_global_im1x1 and sl_tmp_im1x1:
                s_all += create_group_im(sl_global_im1x1, sl_tmp_im1x1, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту ИМ1x2
            if sl_global_im1x2 and sl_tmp_im1x2:
                s_all += create_group_im(sl_global_im1x2, sl_tmp_im1x2, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])
            # Обработка и запись в карту ИМ1x2pz
            if sl_global_im1x2pz and sl_tmp_im1x2pz:
                s_all += create_group_im(sl_global_im1x2pz, sl_tmp_im1x2pz, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту ИМ2x2
            if sl_global_im2x2 and sl_tmp_im2x2:
                s_all += create_group_im(sl_global_im2x2, sl_tmp_im2x2, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту ИМ_АО
            if sl_global_im_ao and sl_tmp_im_ao:
                s_all += create_group_im(sl_global_im_ao, sl_tmp_im_ao, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту кнопок
            if sl_global_btn and sl_tmp_btn:
                s_all += create_group_btn(sl_global_btn, sl_tmp_btn, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту наработок
            if sl_global_cnt:
                s_all += create_group_system_sig('CNT', sl_global_cnt, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту ALR
            if sl_global_fast_alr:
                s_all += create_group_alr(sl_global_fast_alr, tmp_ind_arc, line_source[0])

            # Если выцепили АСки, то закидываем в карту индексов
            if test_sl_global_as:
                s_all += create_group_system_sig('ALR', test_sl_global_as, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту ALG
            if sl_global_alg:
                s_all += create_group_system_sig('ALG', sl_global_alg, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту GRH
            if sl_global_grh:
                s_all += create_group_system_sig('GRH', sl_global_grh, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту Режимы
            if sl_global_mod:
                s_all += create_group_system_sig('MODES', sl_global_mod, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту PPU
            if sl_global_ppu:
                s_all += create_group_system_sig('PPU', sl_global_ppu, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту TS
            if sl_global_ts:
                s_all += create_group_system_sig('TS', sl_global_ts, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту WRN
            if sl_global_wrn:
                s_all += create_group_system_sig('WRN', sl_global_wrn, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту Защит(PZ)
            if sl_global_pz and line_source[0] in sl_pz and dict_signal.get('pz'):
                s_all += create_group_pz(sl_global_pz, dict_signal.get('pz', ''), sl_pz[line_source[0]], tmp_ind_no_arc,
                                         line_source[0])

            # Обработка и запись в карту уставок
            if sl_global_set and sl_tmp_set:
                s_all += create_group_par(sl_global_set, sl_tmp_set, sl_global_fast, tmp_ind_arc, tmp_ind_no_arc,
                                          'System.SET', line_source[0])

            # Обработка и запись в карту ТР
            if sl_global_tr and 'ТР' in sl_cpu_spec.get(line_source[0], 'бла'):
                s_all += create_group_tr(sl_global_tr, tmp_ind_no_arc, 'System.TR', line_source[0])

            # Обработка и запись в карту тегов SAR
            if sl_global_sar:
                s_all += create_group_sar(sl_global_sar, tmp_ind_no_arc, 'SAR', line_source[0])

            # Обработка и запись в карту АПР
            if sl_global_apr and 'АПР' in sl_cpu_spec.get(line_source[0], 'бла'):
                s_all += create_group_apr(sl_global_apr, sl_global_fast, tmp_ind_no_arc, tmp_ind_arc, 'APR',
                                          line_source[0])

            # Обработка и запись в карту драйверных переменных
            if sl_global_drv or sl_cpu_drv_iec.get(line_source[0], {}):
                s_all += create_group_drv(drv_sl=sl_global_drv, template_no_arc_index=tmp_ind_no_arc,
                                          source=line_source[0],
                                          sl_global_fast=sl_global_fast, template_arc_index=tmp_ind_arc,
                                          sl_drv_iec=sl_cpu_drv_iec.get(line_source[0], {}),
                                          sl_global_drv_imit=sl_global_drv_imit)

            # повторно открываем глобальный словарь контроллера для сбора диагностики (здесь немного по-другому читаем)
            if os.path.exists(os.path.join(line_source[1], 'global0.var')):
                with open(os.path.join(line_source[1], 'global0.var'), 'rt') as f_global:
                    while 8:
                        line = f_global.readline().strip()
                        if not line:
                            break
                        if line.split(',')[0][1:] in sl_for_diag.get(line_source[0], 'бла'):
                            module = line.split(',')[0][1:]  # алгоритмическое имя модуля
                            while 8:
                                tmp_line = f_global.readline().strip()
                                if tmp_line == '/':  # конец описания модуля отделяется двумя строками по / в каждой
                                    tmp_line = f_global.readline().strip()
                                    if tmp_line == '/':
                                        break
                                if not tmp_line:
                                    break
                                if sl_for_diag.get(line_source[0]):
                                    curr_module = sl_for_diag[line_source[0]][module]  # тип модуля
                                else:
                                    curr_module = ''
                                tag = get_variable(line=tmp_line)
                                if tag in sl_module_diag_sig.get(curr_module, 'бла'):
                                    if tag not in sl_module_diag_sig_conform.get(curr_module, 'бла'):
                                        tag_in = tag
                                    else:
                                        tag_in = sl_module_diag_sig_conform[curr_module].get(tag)
                                    # print(tmp_line.split(',')[0][1:], get_variable(line=tmp_line))

                                    # В словаре диагностики (алг.имя модуля, имя пер) : [инд. пер, тип пер]
                                    if (module, tag_in) not in sl_global_diag:
                                        index_par = tmp_line[:tmp_line.find(',//')].split(',')[-8]
                                        sl_global_diag[(module, tag_in)] = [index_par,
                                                                            tmp_line.split(',')[1]]
            if sl_global_diag:
                s_all += create_group_diag(diag_sl=sl_global_diag, template_no_arc_index=tmp_ind_no_arc,
                                           source=line_source[0], template_arc_index=tmp_ind_arc,
                                           sl_global_fast=sl_global_fast)
            # Обработка и запись в карту CDO
            # print(sl_global_cdo)
            if sl_global_cdo:
                s_all += create_group_system_sig('CDO', sl_global_cdo, tmp_ind_no_arc, line_source[0])

            # Обработка и запись в карту МКО
            if sl_add_cpu_mko.get(line_source[0]):
                s_all += create_group_add_noarc(sl_add=sl_add_cpu_mko.get(line_source[0]),
                                                template_no_arc_index=tmp_ind_no_arc,
                                                source=line_source[0])

            # Добавляем add-параметры
            if sl_add_par:
                s_all += create_group_add_arc(sl_add=sl_add_par,
                                              template_arc=tmp_ind_arc, source=line_source[0], post_pref_par='.Value')
            if sl_add_par_struct:
                s_all += create_group_add_noarc(sl_add=sl_add_par_struct,
                                                 template_no_arc_index=tmp_ind_no_arc,
                                                 source=line_source[0], post_pref_par='')

            # Обработка и запись в карту сигналов ПРУ
            if sl_global_pru:
                s_all += create_group_system_sig('PRU', sl_global_pru, tmp_ind_no_arc, line_source[0])

            # Проверка изменений, и если есть изменения, то запись
            # Если нет папки File_for_Import, то создадим её
            if not os.path.exists('File_for_Import'):
                os.mkdir('File_for_Import')
            # Если нет папки File_for_Import/Maps, то создадим её
            if not os.path.exists(os.path.join('File_for_Import', 'Maps')):
                os.mkdir(os.path.join('File_for_Import', 'Maps'))
            # Проверка на пустую карту, то есть в том случае, когда
            new_map = '<root format-version=\"0\">\n' + s_all.rstrip() + '\n</root>'
            if new_map == '<root format-version=\"0\">\n' + '\n</root>':
                print(f'Неверно указана папка проекта контроллера {line_source[0]}(ошибка пустой карты)')
                print(f'Карта адресов контроллера {line_source[0]} не обновлена')
            else:
                check_diff_file(check_path=os.path.join('File_for_Import', 'Maps'),
                                file_name_check=f'trei_map_{line_source[0]}.xml',
                                new_data=new_map,
                                message_print=f'Требуется заменить карту адресов контроллера {line_source[0]}')

            # совместно с модулем difflib можно в будущем определить отличающиеся строки - на будущее
            # new_map_file = new_map_file.splitlines(keepends=True)
            # old_map_file = f_read_check.read().splitlines(keepends=True)
            # diff = difflib.ndiff(new_map_file, old_map_file)
            # dd = ''.join(diff)
            # print('NO' if '- ' in dd or '+ ' in dd else 'YES')
            # for j in dd.split('\n'):
            #    if '- ' in j or '+ ' in j:
            #        print(j)


def read_mko_cpu_index(tuple_all_cpu: tuple, sl_cpu_path: dict):
    # sl_cpu_mko_index = {cpu: ((полное имя переменной диагностики МКО, индекс), )}
    sl_cpu_mko_index = {}
    for cpu, path in sl_cpu_path.items():
        if cpu is None or path is None:
            continue
        # Если нет папки контроллера, то сообщаем об этом юзеру и идём дальше
        if not os.path.exists(path):
            # print(f"НЕ НАЙДЕНА ПАПКА ПРОЕКТА КОНТРОЛЛЕРА {cpu}, КАРТА АДРЕСОВ НЕ БУДЕТ ОБНОВЛЕНА")
            continue
        else:
            line_source = [cpu.strip(), path.strip()]
            if cpu not in tuple_all_cpu:
                continue

            # Если есть глобальный словарь
            if os.path.exists(os.path.join(line_source[1], 'global0.var')):
                with open(os.path.join(line_source[1], 'global0.var'), 'rt') as f_global:
                    for line in f_global:
                        line = line.strip()

                        if len(line.split(',')) >= 10 and 'from_' in line.lower() \
                                and re.findall(r'noping\d', line.lower()):
                            # Получаем переменную с разделителем
                            tmp_var = get_variable(line=line)
                            index_par = line[:line.find(',//')].split(',')[-8]
                            line = line.split(',')
                            if line_source[0] not in sl_cpu_mko_index:
                                sl_cpu_mko_index[line_source[0]] = tuple()
                            tuple_par_mko = (tmp_var, index_par)
                            add_ = (tmp_var[:tmp_var.rfind('|')].split('_')[-1],
                                    tmp_var[:tmp_var.rfind('|')].split('_')[1]) \
                                if tmp_var[:tmp_var.rfind('|')].count('_') > 1 \
                                else tmp_var[:tmp_var.rfind('|')].split('_')[-1]
                            tuple_par_mko += (add_,)
                            if tuple_par_mko not in sl_cpu_mko_index.get(line_source[0],  tuple()):
                                sl_cpu_mko_index[line_source[0]] += (tuple_par_mko, )

    return sl_cpu_mko_index


def create_group_add_noarc(sl_add, template_no_arc_index, source, post_pref_par: str=""):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_add.items():
        a = key
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_no_arc_index).substitute(name_signal=f'{a}{post_pref_par}',
                                                            type_signal=sl_type[value[1]], index=value[0],
                                                            data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


def create_group_add_arc(sl_add: dict, template_arc, source, post_pref_par: str):
    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_add.items():
        a = key
        pref_arc = f'NoArc{sl_data_cat[value[1]]}'
        s_out += Template(template_arc).substitute(name_signal=f'{a}{post_pref_par}',
                                                   type_signal=sl_type[value[1]], index=value[0],
                                                   data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out


'''
def create_group_alr(sl_global_fast_alr, template_arc_index, source):
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool'
    }
    s_out = ''
    for key, value in sl_global_fast_alr.items():
        a = key
        pref_arc = 'Arc'  # для проекта Бованенково убрать '.Value'
        s_out += Template(template_arc_index).substitute(name_signal=f'System.ALR.{a}.Value',
                                                         type_signal=sl_type[value[1]], index=value[0],
                                                         data_category=f'DataCategory_{source}_{pref_arc}')
    return s_out
'''

def create_index_add(return_sl_cpu_add_index: dict):
    buff_size = 50
    tmp_ind_arc = '  <item Binding="Introduced">\n' \
                  '    <node-path>$name_signal</node-path>\n' \
                  '    <protocoltype>$type_signal</protocoltype>\n' \
                  '    <index>$index</index>\n' \
                  f'    <buffer-length>{buff_size}</buffer-length>\n' \
                  '    <archivation-period>1</archivation-period>\n' \
                  '    <category>$data_category</category>\n' \
                  '  </item>\n'
    tmp_ind_no_arc = '  <item Binding="Introduced">\n' \
                     '    <node-path>$name_signal</node-path>\n' \
                     '    <protocoltype>$type_signal</protocoltype>\n' \
                     '    <index>$index</index>\n' \
                     '    <category>$data_category</category>\n' \
                     '  </item>\n'

    sl_data_cat = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Discrete',
        'N': 'Analog'
    }
    sl_type = {
        'R': 'Analog',
        'I': 'Analog',
        'B': 'Bool',
        'N': 'Double'
    }
    # return_sl_cpu_add_index = {cpu: {(полный тег, тип тега): индекс}}
    # print(return_sl_cpu_add_index)
    for cpu, vals_tag in return_sl_cpu_add_index.items():
        s_out = ''
        for tuple_key, index_tag in vals_tag.items():
            tag = tuple_key[0]
            type_tag = tuple_key[1]
            pref_arc = f"NoArc{sl_data_cat[type_tag]}"
            s_out += Template(tmp_ind_no_arc).substitute(name_signal=f'{tag}',
                                                         type_signal=sl_type[type_tag],
                                                         index=index_tag,
                                                         data_category=f'DataCategory_{cpu}_{pref_arc}')

        # Проверка на пустую карту, то есть в том случае, когда
        new_map = '<root format-version=\"0\">\n' + s_out.rstrip() + '\n</root>'
        if new_map == '<root format-version=\"0\">\n' + '\n</root>':
            print(f'Карта добавленного контроллера {cpu} пустая, не обновлена')
        else:
            check_diff_file(check_path=os.path.join('File_for_Import', 'Maps'),
                            file_name_check=f'ADD_trei_map_{cpu}.xml',
                            new_data=new_map,
                            message_print=f'Требуется импортировать карту адресов контроллера {cpu} - '
                                          f'File_for_Import/Maps/ADD_trei_map_{cpu}.xml')

    return

