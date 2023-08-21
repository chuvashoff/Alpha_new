import uuid
from math import floor, ceil
from func_for_v3 import *
from Create_mnemo_v3 import multiple_replace_xml_mnemo, check_diff_mnemo, json_load
# from lxml.etree import CDATA


def create_mnemo_visual(sl_object_all: dict, sl_command_in_cpu: dict, sl_condition_in_cpu: dict, sl_mod_cpu: dict):
    # sl_command_in_cpu = {cpu: {(Режим_alg, русское имя режима): {номер шага: {команда_alg: русский текст команды}}}}
    # sl_condition_in_cpu = {cpu: {Режим_alg: {номер шага: {условие_перехода_alg: русский текст перехода}}}}
    # all_sub_modes = tuple([submod[submod.find('_')+1:] for submod in tuple_submodes_start])
    # print('sl_condition_in_cpu ', sl_condition_in_cpu)

    # СЛОВАРЬ УНИКАЛЬНЫХ ОБЪЕКТОВ
    # Формируем словарь вида {кортеж контроллеров: (Объект, рус имя объекта, индекс объекта)}
    # При этом, если есть полное совпадение контроллеров, то дублирования нет
    # sl_cpus_object = {cpu: obj[0] for obj, sl_cpu in sl_object_all.items() for cpu in sl_cpu}
    sl_cpus_object = {}
    for obj, sl_cpu in sl_object_all.items():
        cpus = tuple(sorted(sl_cpu.keys()))
        if cpus not in sl_cpus_object:
            sl_cpus_object[cpus] = obj

    # Формируем словарь команд, только с привязкой к объекту, а не к cpu
    sl_command_object = {obj: {} for obj in sl_object_all}
    for obj, sl_cpu in sl_object_all.items():
        for cpu in sl_cpu:
            if cpu in sl_command_in_cpu:
                sl_command_object[obj].update(sl_command_in_cpu[cpu])
    # for obj in sl_command_object:
    #     print(obj)
    #     for mod in sl_command_object[obj]:
    #         print(mod, sl_command_object[obj][mod])

    # Формируем словарь условий перехода, только с привязкой к объекту, а не к cpu
    sl_condition_object = {obj: {} for obj in sl_object_all}
    for obj, sl_cpu in sl_object_all.items():
        for cpu in sl_cpu:
            if cpu in sl_command_in_cpu:
                sl_condition_object[obj].update(sl_condition_in_cpu[cpu])
    # for obj in sl_condition_object:
    #     print(obj)
    #     for mod in sl_condition_object[obj]:
    #         print(mod, sl_condition_object[obj][mod])

    # Формируем словарь {объект: кортеж режимов(в том числе подрежимов)}
    sl_modes_object = {obj: tuple() for obj in sl_object_all}
    for obj, sl_cpu in sl_object_all.items():
        for cpu in sl_cpu:
            sl_modes_object[obj] += sl_mod_cpu.get(cpu, tuple())
    # for obj, tt in sl_modes_object.items():
    #     print(obj, tt)
    # print('sl_modes_object ', sl_modes_object)

    # Формируем словарь {объект: кортеж подрежимов}
    sl_submodes_object = {obj: tuple() for obj in sl_object_all}
    sl_submodes_cpu = {cpu: tuple() for cpu in sl_command_in_cpu}
    for cpu, _sl_mod in sl_command_in_cpu.items():
        for _, _sl_step in _sl_mod.items():
            for _, _sl_command in _sl_step.items():
                sl_submodes_cpu[cpu] += tuple([i[i.find('_')+1:i.find('_START')] for i in tuple(_sl_command.keys())
                                               if i.endswith('_START')])
    # Удаляем повторы
    sl_submodes_cpu = {cpu: tuple(sorted(set(tuple_subs))) for cpu, tuple_subs in sl_submodes_cpu.items()}

    for obj, sl_cpu in sl_object_all.items():
        for cpu in sl_cpu:
            sl_submodes_object[obj] += sl_submodes_cpu.get(cpu, tuple())
    # print('subs')
    # Убеждаемся, что это реальные подрежимы, которые определены для данного объекта
    sl_submodes_object = {obj: tuple([subs for subs in tuple_subs
                                      if subs in [tuple_mod[0] for tuple_mod in sl_modes_object.get(obj, (('', ''),))]])
                          for obj, tuple_subs in sl_submodes_object.items()}
    # for obj, tt in sl_submodes_object.items():
    #     print(obj, tt)

    # Формируем словарь вида (учитывается только алг.имя режима)
    # {объект: {режим(или подрежим) : (кортеж режимов, подрежимов, которые могут открыть данный режим)}}
    sl_object_modes_to_modes = {obj: {m[0]: tuple() for m in tuple_subs} for obj, tuple_subs in sl_modes_object.items()}

    for obj, _sl_mod in sl_command_object.items():
        for main_mod, _sl_step in _sl_mod.items():
            for _, _sl_command in _sl_step.items():
                for ss in [i[i.find('_')+1:i.find('_START')] for i in _sl_command if i.endswith('_START')]:
                    if ss in sl_object_modes_to_modes[obj]:
                        if main_mod[0] not in sl_object_modes_to_modes[obj][ss]:
                            sl_object_modes_to_modes[obj][ss] += (main_mod[0],)
    # for obj in sl_object_modes_to_modes:
    #     print(obj)
    #     for m in sl_object_modes_to_modes[obj]:
    #         print(m, sl_object_modes_to_modes[obj][m])

    # sl_object_all {(Объект, рус имя объекта, индекс объекта):
    # {контроллер: (ip основной, ip резервный, индекс объекта)} }

    # словарь команд по cpu sl_command_in_cpu = {cpu: sl_command}
    # sl_command = {(Режим_alg, русское имя режима): {номер шага: {команда_alg: русский текст команды}}}

    # sl_condition_in_cpu -  словарь такого же вида, как sl_command_in_cpu
    # только для условий перехода и без кортежа в режимах - там просто режим_alg

    # print(sl_condition_in_cpu)
    # print(tuple_submodes_start)
    # print(sl_command_in_cpu)
    # Словарь режимов, которые вызывают подрежимы
    # {кортеж режима : (кортеж подрежимов _START)}
    #

    # print(tuple_submodes_start)
    # Словарь ID для типовых структур, возможно потом будет считываться с файла или как-то по-другому
    sl_uuid_base_default = {
        "00_AlgVisual_Base": "4d4dc649-f350-4c61-89d1-6c938208b3fe",
        'Rectangle': '15726dc3-881e-4d8d-b0fa-a8f8237f08ca',
        'Text': '21d59f8d-2ca4-4592-92ca-b4dc48992a0f',
        'ApItemBool': 'e3f11724-0f76-4497-8d01-38fbb82fb844',
        'Step': 'afb45021-6965-4de3-9d8a-c9a825bf814d',
        'Cmd': 'b557930e-9c1e-452c-a60c-d16e1cbcf50f',
        'Cmd_Link': 'b8eea571-a5ec-4ed6-911a-9541f23b7cad',
        'Set_SP': '976b60b5-5800-4f93-9840-42353d513f6a',
        'Set_OR': 'd5a005dc-a385-4809-bc3d-b38255b27418',
        'Set': '51bbe086-73b0-4b6f-b6b2-69bf899f1d51',
        'notifying_string': '14976fbf-36ab-415f-abc3-9f8fdc217351',
        'Line': '4dd08b15-1502-453f-a174-2c0a5aa850ba',
        'Point': '467f1af0-7bb4-4a61-b6fb-06e7bfd530d6',
        'Action': 'a9ee9770-1c4a-44c9-b815-157d9fc2ab95',
        'Back': '808d0619-d21b-4102-b931-0c8f315bfcc1',
        'Form': 'ffaf5544-6200-45f4-87ec-9dd24558a9d5',
        'ApSource': '966603da-f05e-4b4d-8ef0-919efbf8ab2c',
        'string': '76403785-f3d5-41a7-9eb6-d19d2aa2d95d',
        'Button': '61e46e4a-827f-4dd2-ac8a-b68bcaddf442',
        '01_MainControl': 'c1882486-6ced-4543-a63a-eb1e5f0c3cf8',
        '00_FormAlg_Base': '8970c7d2-2f62-4029-b1a6-48d46a91463b'
    }
    try:
        if os.path.exists(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json')):
            with open(os.path.join('Template_Alpha', 'Systemach', 'Mnemo', f'uuid_base_elements.json'), 'r',
                      encoding='UTF-8') as f_sig:
                text_json = json_load(f_sig)
            sl_uuid_base = text_json
        else:
            print('Файл Systemach/Mnemo/uuid_base_elements.json не найден, '
                  'uuid базовых элементов будут определены по умолчанию')
            sl_uuid_base = sl_uuid_base_default
    except Exception:
        print('Файл Systemach/Mnemo/uuid_base_elements.json заполнен некорректно, '
              'uuid базовых элементов будут определены по умолчанию')
        sl_uuid_base = sl_uuid_base_default

    gor_base = 500  # sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[0]
    # vert_base = 270  # sl_size.get(f'{str(size_shirina)}x{str(size_vysota)}', (1780, 900))[1]
    # Для каждого объекта...
    # for objects in sl_object_all:
    #     # Для каждого контроллера в объекте
    #     for cpu in sl_object_all[objects]:
    #         # Если контроллер в составе
    #         if cpu in set(sl_command_in_cpu[objects].keys()):

    sl_page_uuid = {}
    # Если не существует файла uuid_FormAlg, то создаём его и записываем uuid форм вызовов алгоритмов
    # для каждого объекта
    if not os.path.exists(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo', 'Systemach', 'uuid_FormAlg')):
        with open(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo', 'Systemach', 'uuid_FormAlg'),
                  'w', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for _, obj in sl_cpus_object.items():
                if sl_modes_object.get(obj, ''):
                    generate_uuid = ('f7d5f21d-c4e8-4ce8-932e-ef2d8b44d2eb' if obj[2] == '1' else uuid.uuid4())
                    sl_page_uuid[f"01_FormAlg_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'01_FormAlg_{obj[0]}:{generate_uuid}\n')
                # Пробегаемся по режимам(в том числе по подрежимам данного объекта) и закидываем их в словарь
                for modes_obj in sl_modes_object.get(obj, ''):
                    generate_uuid = uuid.uuid4()
                    name_mnemo = f"AlgVisual_{modes_obj[0]}_{obj[0]}"
                    sl_page_uuid[name_mnemo] = f'{generate_uuid}'
                    f_uuid_write.write(f"{name_mnemo}:{generate_uuid}\n")

    else:
        # Если файл существует, то считываем и записываем в словарь
        with open(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo', 'Systemach', 'uuid_FormAlg'),
                  'r', encoding='UTF-8') as f_uuid_read:
            for line in f_uuid_read:
                lst_line = line.strip().split(':')
                sl_page_uuid[lst_line[0]] = lst_line[1]
        # Если после вычитывания не обнаружили формы для отсутствующих объектов
        # (например, увеличилось количество объектов), то дозаписываем
        with open(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo', 'Systemach', 'uuid_FormAlg'),
                  'a', encoding='UTF-8') as f_uuid_write:
            # Пробегаемся по УНИКАЛЬНЫМ объектам
            for _, obj in sl_cpus_object.items():
                if sl_modes_object.get(obj, '') and f"01_FormAlg_{obj[0]}" not in sl_page_uuid:
                    generate_uuid = uuid.uuid4()
                    sl_page_uuid[f"01_FormAlg_{obj[0]}"] = f'{generate_uuid}'
                    f_uuid_write.write(f'01_FormAlg_{obj[0]}:{generate_uuid}\n')
                # Пробегаемся по режимам(в том числе по подрежимам данного объекта)
                # и закидываем их в словарь в случае отсутствия такового
                for modes_obj in sl_modes_object.get(obj, ''):
                    if f"AlgVisual_{modes_obj[0]}_{obj[0]}" not in sl_page_uuid:
                        generate_uuid = uuid.uuid4()
                        name_mnemo = f"AlgVisual_{modes_obj[0]}_{obj[0]}"
                        sl_page_uuid[name_mnemo] = f'{generate_uuid}'
                        f_uuid_write.write(f"{name_mnemo}:{generate_uuid}\n")

    # Для каждого УНИКАЛЬНОГО объекта(уникального ранее определили по составу ПЛК) создаём мнемосхему 01_FormAlg
    # только в том случае, если у него определены какие-то режимы
    for _, obj in sl_cpus_object.items():
        if sl_modes_object.get(obj, ''):
            root_type = ET.Element(
                'type', access_modifier="private", name=f"01_FormAlg_{obj[0]}",
                display_name=f"01_FormAlg_{obj[0]}",
                uuid=f"{sl_page_uuid[f'01_FormAlg_{obj[0]}']}",
                base_type="00_FormAlg_Base",
                base_type_id=f"{sl_uuid_base.get('00_FormAlg_Base', '')}",
                ver="2")
            for target, target_value in {'X': '1', 'Y': '1', 'ZValue': '0', 'Rotation': '0', 'Scale': '1',
                                         "Visible": 'true', "Enabled": 'true', "PenColor": "4278190080",
                                         "PenStyle": "0", "PenWidth": "2", "BrushColor": "4293980400",
                                         "BrushStyle": "1", "WindowX": "0", "WindowY": "0",
                                         "WindowCaption": "01_FormAlg", "ShowWindowCaption": "true",
                                         "ShowWindowMinimize": "true", "ShowWindowMaximize": "true",
                                         "ShowWindowClose": "true", "AlwaysOnTop": "false", "WindowSizeMode": "1",
                                         "WindowBorderStyle": "1", "WindowState": "0", "WindowScalingMode": "0",
                                         "MonitorNumber": "0", "WindowPosition": "0", "WindowCloseMode": "0",
                                         "Opacity": "1"}.items():
                ET.SubElement(root_type, 'designed', target=target, value=target_value, ver="2")

            # # Добавляем ApSource_CurrentForm
            # apsource_currentform = ET.SubElement(root_type, 'object', access_modifier="private",
            #                                      name="ApSource_CurrentForm",
            #                                      display_name="ApSource_CurrentForm",
            #                                      uuid=f"{uuid.uuid4()}",
            #                                      base_type="ApSource",
            #                                      base_type_id=sl_uuid_base.get('ApSource', ''), ver="3")
            # ET.SubElement(apsource_currentform, 'designed', target="Active", value="true", ver="3")
            # ET.SubElement(apsource_currentform, 'designed', target="ReAdvise", value="0", ver="3")
            # ET.SubElement(apsource_currentform, 'init', target="ParentSource", ver="3", ref="_init_ApSource")
            # ET.SubElement(apsource_currentform, 'init', target="Path", ver="3", ref="_init_GPAPath")
            # ET.SubElement(apsource_currentform, 'designed', target="Path", value="", ver="5")
            # ET.SubElement(apsource_currentform, 'designed', target="ClientDisplayName", value="HMI", ver="5")
            # ET.SubElement(apsource_currentform, 'designed', target="ClientId", value="HMI", ver="5")
            #
            # ET.SubElement(root_type, 'param', access_modifier="private", name="_init_ApSource",
            #               display_name="_init_ApSource",
            #               uuid=f"{uuid.uuid4()}",
            #               base_type="ApSource", base_type_id=sl_uuid_base.get('ApSource', ''),
            #               base_const="true", base_ref="true", ver="3")
            # ET.SubElement(root_type, 'param', access_modifier="private", name="_init_GPAPath",
            #               display_name="_init_GPAPath",
            #               uuid=f"{uuid.uuid4()}",
            #               base_type="string", base_type_id=sl_uuid_base.get('string', ''), ver="3")

            # Пробегаемся по возможным режимам с контролем вхождения в объект
            x_but_start = 17
            x_but = x_but_start
            y_but_start = 10
            y_but = y_but_start
            i = 0
            for modes_obj in sl_modes_object.get(obj, ''):
                object_bool_mod = ET.SubElement(root_type, 'object', access_modifier="private",
                                                name=f"MOD_{modes_obj[0]}",
                                                display_name=f"MOD_{modes_obj[0]}",
                                                uuid=f"{uuid.uuid4()}",
                                                base_type="ApItemBool",
                                                base_type_id=sl_uuid_base.get('ApItemBool', ''), ver="3")
                ET.SubElement(object_bool_mod, 'init', target="Source", ver="3",
                              ref=f"here.ApSource_CurrentForm")
                ET.SubElement(object_bool_mod, 'init', target="Path", ver="3",
                              value=f'System.GRH.{modes_obj[0]}_START.Value')
                # Добавляем кнопки
                object_button_mod = ET.SubElement(root_type, 'object', access_modifier="private",
                                                  name=f"Alg_{modes_obj[0]}",
                                                  display_name=f"Alg_{modes_obj[0]}",
                                                  uuid=f"{uuid.uuid4()}",
                                                  base_type="Button",
                                                  base_type_id=sl_uuid_base.get('Button', ''), ver="3")
                for target, target_value in {'X': str(x_but), 'Y': str(y_but),
                                             'Rotation': '0', 'Scale': '1',
                                             "Visible": 'true', "Enabled": 'true',
                                             'Width': '225', 'Height': '35', 'Text': f'{modes_obj[1]}',
                                             "TextAlignment": "132",
                                             "Font": "PT Astra Sans,14,-1,5,50,0,0,0,0,0,Обычный",
                                             'FontColor': '0xffffffff', "OnClickFontColor": "4278190080",
                                             "OnHoverFontColor": "4278190080", "BrushColor": "0xff27567a",
                                             "BrushStyle": "1", "OnClickBrushColor": "4288716960",
                                             "OnClickBrushStyle": "1", "OnHoverBrushColor": "4294967295",
                                             "OnHoverBrushStyle": "1", "PenColor": "4278190080",
                                             "PenStyle": "1", "PenWidth": "1", "OnClickPenColor": "4278190080",
                                             "OnClickPenStyle": "1", "OnClickPenWidth": "3",
                                             "OnHoverPenColor": "4278190080", "OnHoverPenStyle": "1",
                                             "OnHoverPenWidth": "2", "ZValue": "0", "Opacity": "1",
                                             "Checkable": "false", "DisabledFontColor": "4278190080",
                                             "DisabledBrushColor": "4288716960", "DisabledBrushStyle": "1",
                                             "DisabledPenColor": "4288716960", "DisabledPenStyle": "1",
                                             "DisabledPenWidth": "1"}.items():
                    ET.SubElement(object_button_mod, 'designed', target=target, value=target_value, ver="2")
                object_brush = ET.SubElement(object_button_mod, 'do-trace', access_modifier="private",
                                             target='BrushColor', ver="3")
                ET.SubElement(object_button_mod, 'designed', target="Checked", value=f"false", ver="4")

                # В кнопку добавляем динамику подсветки
                object_cond_expr = ET.SubElement(object_brush, 'conditional-expr')
                object_cond = ET.SubElement(object_cond_expr, 'condition')
                object_cond.text = f'yopta_on![CDATA[MOD_{modes_obj[0]}]]yopta_off'
                object_expr = ET.SubElement(object_cond_expr, 'expr')
                object_expr.text = f'yopta_on![CDATA[0xff008000]]yopta_off'

                object_cond_def = ET.SubElement(object_brush, 'default-expr')
                object_expr = ET.SubElement(object_cond_def, 'expr')
                object_expr.text = f'yopta_on![CDATA[0xff27567a]]yopta_off'

                # Добавляем динамику открытия мнемо
                object_handler = ET.SubElement(
                    object_button_mod, 'do-on', access_modifier="private",
                    name=f"Handler_Open_{modes_obj[0]}",
                    display_name=f"Handler_Open_{modes_obj[0]}",
                    ver="5", event="MouseClick", form_action="open", form_by_id="false")
                name_open = f"AlgVisual_{modes_obj[0]}_{obj[0]}"
                object_open_in_handler = ET.SubElement(object_handler, 'object', access_modifier="private",
                                                       uuid=f"{uuid.uuid4()}",
                                                       base_type=name_open,
                                                       base_type_id=f"{sl_page_uuid.get(name_open, '')}",
                                                       ver="5")
                ET.SubElement(object_open_in_handler, 'init', target="_AbonentPath", ver="5",
                              ref=f"here._AbonentPath")
                ET.SubElement(object_open_in_handler, 'init', target="OpenFrom", ver="5", value="01_FormAlg")
                ET.SubElement(object_open_in_handler, 'designed', target="WindowCaption", ver="5",
                              value=f"{modes_obj[0]}")
                ET.SubElement(object_open_in_handler, 'init', target="Link_MainControl", ver="5",
                              ref=f"here.Link_MainControl")
                ET.SubElement(object_open_in_handler, 'init', target="X", ver="5", value=f"1")
                ET.SubElement(object_open_in_handler, 'init', target="Y", ver="5", value=f"1")
                i += 1
                x_but += 235
                if i == 2:
                    i = 0
                    x_but = x_but_start
                    y_but += 50

            # Определяем размеры окна
            ET.SubElement(root_type, 'designed', target='Width', value='490', ver="2")
            ET.SubElement(root_type, 'designed', target='Height', value=f'{y_but + 70}', ver="2")  # 600
            ET.SubElement(root_type, 'designed', target='WindowWidth', value='490', ver="2")
            ET.SubElement(root_type, 'designed', target='WindowHeight', value=f'{y_but + 70}', ver="2")

            # Добавляем Линк на главную форму
            # ET.SubElement(root_type, 'object', access_modifier="private",
            #               name=f"Link_MainControl",
            #               display_name=f"Link_MainControl",
            #               uuid=f"{uuid.uuid4()}",
            #               base_type="01_MainControl",
            #               base_type_id=sl_uuid_base.get('01_MainControl', ''), base_const="true",
            #               base_ref="true", ver="5")

            object_handler = ET.SubElement(root_type, 'do-on', access_modifier="private",
                                           name=f"Handler_1", display_name=f"Handler_1", ver="5", event="Opened")
            el = ET.SubElement(object_handler, 'body', kind="om")
            el.text = f'yopta_on![CDATA[here.Link_MainControl.ALG._MainH = me.Height;\n' \
                      f'here.Link_MainControl.ALG._MainW = me.Width;]]yopta_off'

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_type).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo'),
                             file_name_check=f"01_FormAlg_{obj[0]}.omobj",
                             message_print=f'Требуется заменить мнемосхему 01_FormAlg_{obj[0]}.omobj'
                             )

            # with open(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo',
            #                        f"01_FormAlg_{obj[0]}.omobj"),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))

            # sl_create[obj] = sorted(tuple(_sl_cpu_obj.keys()))
    # print(sl_create.values())

    # Создаём словарь, который содержит объект и отсортированный состав контроллеров
    # sl_create = {[Состав контроллеров]: кортеж созданных мнемосхем виде AlgVisual_alg}
    # sl_create = {tuple(sorted(tuple(_sl_cpu_obj.keys()))): tuple() for _, _sl_cpu_obj in sl_object_all.items()}

    # Для каждого УНИКАЛЬНОГО объекта...
    for _, obj in sl_cpus_object.items():
        # ...Для каждого режима в объекте...
        for tuple_mod in sl_modes_object.get(obj, ''):  # tuple_mod - кортеж (алг имя, рус имя)
            # print(tuple_mod)
            # Создаём мнемосхему хода алгоритма
            # только в том случае, если у него определены какие-то режимы и
            # подобного рода ещё не создавали - определяем по ПЛК
            name_mnemo = f"AlgVisual_{tuple_mod[0]}_{obj[0]}"
            root_type = ET.Element(
                'type', access_modifier="private", name=name_mnemo,
                display_name=name_mnemo,
                uuid=f"{sl_page_uuid[name_mnemo]}",
                base_type="00_AlgVisual_Base",
                base_type_id=f"{sl_uuid_base.get('00_AlgVisual_Base', '4d4dc649-f350-4c61-89d1-6c938208b3fe')}",
                ver="2")
            # ...заполняем стандартную информацию
            ET.SubElement(root_type, 'designed', target='X', value="1", ver="2")
            ET.SubElement(root_type, 'designed', target='Y', value="1", ver="2")
            ET.SubElement(root_type, 'designed', target='Rotation', value="0", ver="2")
            ET.SubElement(root_type, 'designed', target='Scale', value="1", ver="2")
            ET.SubElement(root_type, 'designed', target='Visible', value="true", ver="2")
            ET.SubElement(root_type, 'designed', target='Enabled', value="true", ver="2")
            ET.SubElement(root_type, 'designed', target='Tooltip', value="", ver="2")
            # ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="2")
            # ET.SubElement(root_type, 'designed', target='Height', value=f"{vert_base}", ver="2")
            ET.SubElement(root_type, 'designed', target='PenColor', value="4278190080", ver="2")
            ET.SubElement(root_type, 'designed', target='PenStyle', value="0", ver="2")
            ET.SubElement(root_type, 'designed', target='PenWidth', value="1", ver="2")
            ET.SubElement(root_type, 'designed', target='BrushColor', value="4293980400", ver="2")
            ET.SubElement(root_type, 'designed', target="BrushStyle", value="1", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowX", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowY", value="0", ver="2")
            # ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{size_shirina}", ver="2")
            # ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{window_height}", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowCaption", value=f"{tuple_mod[0]}", ver="2")

            ET.SubElement(root_type, 'designed', target="ShowWindowCaption", value="true", ver="2")
            ET.SubElement(root_type, 'designed', target="ShowWindowMinimize", value="true", ver="2")
            ET.SubElement(root_type, 'designed', target="ShowWindowMaximize", value="true", ver="2")
            ET.SubElement(root_type, 'designed', target="ShowWindowClose", value="true", ver="2")
            ET.SubElement(root_type, 'designed', target="AlwaysOnTop", value="false", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowSizeMode", value="1", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowBorderStyle", value="1", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowState", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowScalingMode", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="MonitorNumber", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowPosition", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowCloseMode", value="0", ver="2")
            ET.SubElement(root_type, 'designed', target="ZValue", value="0", ver="3")
            ET.SubElement(root_type, 'designed', target="Opacity", value="1", ver="3")
            # Добавляем заголовок
            object_headline = ET.SubElement(root_type, 'object', access_modifier="private",
                                            name=f"Headline",
                                            display_name=f"Headline",
                                            uuid=f"{uuid.uuid4()}",
                                            base_type="Rectangle",
                                            base_type_id=sl_uuid_base.get('Rectangle', ''), ver="2")
            ET.SubElement(object_headline, 'designed', target='X', value="0", ver="2")
            ET.SubElement(object_headline, 'designed', target='Y', value="0", ver="2")
            ET.SubElement(object_headline, 'designed', target='Rotation', value="0", ver="2")
            ET.SubElement(object_headline, 'designed', target='Scale', value="1", ver="2")
            ET.SubElement(object_headline, 'designed', target='Visible', value="true", ver="2")
            ET.SubElement(object_headline, 'designed', target='Enabled', value="true", ver="2")
            ET.SubElement(object_headline, 'designed', target='Tooltip', value="", ver="2")
            # пока величины задал статично
            ET.SubElement(object_headline, 'designed', target='Width', value=f"500", ver="2")
            ET.SubElement(object_headline, 'designed', target='Height', value=f"30", ver="2")

            ET.SubElement(object_headline, 'designed', target='RoundingRadius', value=f"0", ver="2")
            ET.SubElement(object_headline, 'designed', target='PenColor', value="4278190080", ver="2")
            ET.SubElement(object_headline, 'designed', target='PenStyle', value="1", ver="2")
            ET.SubElement(object_headline, 'designed', target='PenWidth', value="1", ver="2")
            ET.SubElement(object_headline, 'designed', target='BrushColor', value="4278190080", ver="2")
            ET.SubElement(object_headline, 'designed', target="BrushStyle", value="0", ver="2")
            ET.SubElement(object_headline, 'designed', target="ZValue", value="0", ver="3")
            ET.SubElement(object_headline, 'designed', target="Opacity", value="1", ver="3")

            object_headline_text = ET.SubElement(object_headline,
                                                 'object', access_modifier="private",
                                                 name=f"{tuple_mod[0]}",
                                                 display_name=f"{tuple_mod[0]}",
                                                 uuid=f"{uuid.uuid4()}",
                                                 base_type="Rectangle",
                                                 base_type_id=sl_uuid_base.get('Text', ''), ver="2")

            ET.SubElement(object_headline_text, 'designed', target='X', value="0", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Y', value="0", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Rotation', value="0", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Scale', value="1", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Visible', value="true", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Enabled', value="true", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Tooltip', value="", ver="2")
            # пока величины задал статично
            ET.SubElement(object_headline_text, 'designed', target='Width', value=f"500", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Height', value=f"30", ver="2")

            ET.SubElement(object_headline_text, 'designed', target='Text', value=f"{tuple_mod[1]}", ver="2")
            ET.SubElement(object_headline_text, 'designed', target='Font',
                          value="PT Astra Sans,14,-1,5,50,0,0,0,0,0,Обычный", ver="2")
            ET.SubElement(object_headline_text, 'designed', target="FontColor", value="4278190080", ver="2")
            ET.SubElement(object_headline_text, 'designed', target="TextAlignment", value="132", ver="2")
            ET.SubElement(object_headline_text, 'designed', target="ZValue", value="0", ver="3")
            ET.SubElement(object_headline_text, 'designed', target="Opacity", value="1", ver="3")
            # Добавляем AP bool режима
            object_ap_mod = ET.SubElement(root_type,
                                          'object', access_modifier="private",
                                          name=f"_MOD",
                                          display_name=f"_MOD",
                                          uuid=f"{uuid.uuid4()}",
                                          base_type="ApItemBool",
                                          base_type_id=sl_uuid_base.get('ApItemBool', ''), ver="3")
            # path_mod = (f'System.GRH.{tuple_mod[0]}_START.Value'
            #             if tuple_mod[0] in sl_submodes_object.get(obj, '') else
            #             f'System.MODES.{tuple_mod[0]}.Value')
            path_mod = f'System.GRH.{tuple_mod[0]}_START.Value'

            ET.SubElement(object_ap_mod, 'init', target="Path", ver="3", value=f"{path_mod}")
            ET.SubElement(object_ap_mod, 'init', target="Source", ver="3", ref=f"here.ApSource_CurrentForm")

            # Пробегаемся по шагам
            x_start_num_step = 0.0
            dx_num_step = 0.0
            y_start_num_step = 30.0
            dy_num_step = 0.0
            x_start_com = 30.0
            dx_com = 0.0
            y_start_com = 30.0
            # dy_com = 0.0
            x_start_cond = 230.0
            dx_cond = 0.0
            y_start_cond = 30.0
            # dy_cond = 0.0
            max_next_step = 0.0
            # Для определения мнемосхемы заводим переменную для суммирования максимумов
            max_sum = 0.0
            for num_step, sl_com in sl_command_object[obj][tuple_mod].items():
                # print(f'Начало шага {num_step} режима {modes_tuple[0]}, '
                #       f'максимальное число из шагов и условий предыдущего шага: {max_next_step}')
                # На каждом шагу переопределяем приращения
                dy_num_step += 20 * max_next_step
                # dy_com += 20 * max_next_step
                dy_com = dy_num_step
                # dy_cond = 20 * num_step * max_next_step
                dy_cond = dy_num_step
                # print(dy_com)
                # Добавляем номер шага
                object_num_step = ET.SubElement(root_type,
                                                'object', access_modifier="private",
                                                name=f"Step_{num_step}",
                                                display_name=f"Step_{num_step}",
                                                uuid=f"{uuid.uuid4()}",
                                                base_type="Step",
                                                base_type_id=sl_uuid_base.get('Step', ''), ver="3")
                ET.SubElement(object_num_step, 'designed', target='X',
                              value=f"{x_start_num_step + dx_num_step}", ver="3")
                ET.SubElement(object_num_step, 'designed', target='Y',
                              value=f"{y_start_num_step + dy_num_step}", ver="3")
                ET.SubElement(object_num_step, 'designed', target='Rotation', value="0", ver="3")
                ET.SubElement(object_num_step, 'init', target="Point", ver="3",
                              value=f"{num_step}")  # Какое значение?
                ET.SubElement(object_num_step, 'init', target="_init_Object", ver="3", value=f"System")
                ET.SubElement(object_num_step, 'init', target="_Point", ver="3",
                              value=f"GRH.{tuple_mod[0]}_Point")
                # ET.SubElement(object_num_step, 'init', target="Height", ver="3", value=f"1") # Какое значение?
                ET.SubElement(object_num_step, 'init', target="Num", ver="3",
                              value=f"{num_step}")  # Какое значение?
                ET.SubElement(object_num_step, 'init', target="_MOD", ver="3", ref="here._MOD")
                ET.SubElement(object_num_step, 'init', target="_init_APSource", ver="3",
                              ref="here.ApSource_CurrentForm")
                ET.SubElement(object_num_step, 'designed', target="Opacity", value="1", ver="4")

                # Для каждого шага создаём словарь по OR условий перехода, чтобы разбить
                # tmp_sl_or = {псевдошаг разбивки OR: кортеж переменных в группе}
                tmp_sl_or = {}
                for cond in sl_condition_object[obj][tuple_mod[0]][num_step]:
                    if digit_count(cond, 1) not in tmp_sl_or:
                        tmp_sl_or[digit_count(cond, 1)] = tuple()
                    tmp_sl_or[digit_count(cond, 1)] += (cond,)
                # Определяем кого больше, команд или условий перехода с учётом OR

                tt = len([vv for _, value in tmp_sl_or.items()
                          for vv in value if 'Par_In' not in vv]) + len(tmp_sl_or) - 1
                # print('tmp_sl_or__', tmp_sl_or)
                # print(f'Количество команд шага {num_step}:{len(sl_com)}; Количество условий шага {num_step}:{tt}')
                max_next_step = max(len(sl_com), tt)
                max_sum += max_next_step
                # для каждой группы по ИЛИ делаем (добавляем условия перехода)
                # Определяем шаг расширения
                _height = (round(max_next_step / tt, 3) if tt else 1.0)
                for or_bla, conditions in tmp_sl_or.items():
                    # Для каждого условия в группах по ИЛИ делаем
                    for cond in conditions:
                        # Par_In пропускаем
                        if 'Par_In' in cond:
                            continue
                        # Наличие таймера, что-то сделать
                        if 'Tmv_Out' in cond or 'Tmv_Rev' in cond:
                            object_cond = ET.SubElement(root_type,
                                                        'object', access_modifier="private",
                                                        name=f"Set_SP_{num_step}_{cond}",
                                                        display_name=f"Set_SP_{num_step}_{cond}",
                                                        uuid=f"{uuid.uuid4()}",
                                                        base_type="Set_SP",
                                                        base_type_id=sl_uuid_base.get('Set_SP', ''), ver="3")
                            ET.SubElement(object_cond, 'designed', target='X',
                                          value=f"{x_start_cond + dx_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Y',
                                          value=f"{y_start_cond + dy_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Rotation', value="0", ver="3")
                            ET.SubElement(object_cond, 'init', target="Point", ver="3",
                                          value=f"{num_step}")  # Какое значение?
                            ET.SubElement(object_cond, 'init', target="_CurPoint", ver="3",
                                          value=f"System.GRH.{tuple_mod[0]}_Point")
                            # Потом будет удалено!!!
                            # ET.SubElement(object_cond, 'init', target="SP", ver="3", value=f"300")
                            # ET.SubElement(object_cond, 'init', target="inv", ver="3", value=f"300")
                            text_cond = sl_condition_object[obj][tuple_mod[0]][num_step][cond]
                            if '-Вых' in text_cond:
                                text_cond = f"Таймер: {text_cond[:text_cond.find('-Вых')]}"
                            elif 'Обратный таймер режима' in text_cond:
                                text_cond = 'Обратный таймер'
                            ET.SubElement(object_cond, 'init', target="Text", ver="3",
                                          value=f"{text_cond}")
                            ET.SubElement(object_cond, 'init', target="_Set", ver="3",
                                          value=f"System.GRH.{cond}")
                            ET.SubElement(object_cond, 'init', target="_MOD", ver="3", ref="here._MOD")
                            ET.SubElement(object_cond, 'init', target="_init_APSource", ver="3",
                                          ref="here.ApSource_CurrentForm")
                            ET.SubElement(object_cond, 'init', target="_Height", ver="3", value=f"{_height}")
                        # Если есть признак того, что имеется дополнительный параметр с выводом уставки,
                        # создаём соответствующий объект
                        elif cond.replace('Cmd_In', 'Par_In') in conditions:
                            object_cond = ET.SubElement(root_type,
                                                        'object', access_modifier="private",
                                                        name=f"Set_SP_{num_step}_{cond}",
                                                        display_name=f"Set_SP_{num_step}_{cond}",
                                                        uuid=f"{uuid.uuid4()}",
                                                        base_type="Set_SP",
                                                        base_type_id=sl_uuid_base.get('Set_SP', ''), ver="3")
                            ET.SubElement(object_cond, 'designed', target='X',
                                          value=f"{x_start_cond + dx_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Y',
                                          value=f"{y_start_cond + dy_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Rotation', value="0", ver="3")
                            ET.SubElement(object_cond, 'init', target="Point", ver="3",
                                          value=f"{num_step}")  # Какое значение?
                            ET.SubElement(object_cond, 'init', target="_CurPoint", ver="3",
                                          value=f"System.GRH.{tuple_mod[0]}_Point")
                            # Потом будет удалено!!!
                            # ET.SubElement(object_cond, 'init', target="SP", ver="3", value=f"300")
                            # ET.SubElement(object_cond, 'init', target="inv", ver="3", value=f"300")
                            ET.SubElement(object_cond, 'init', target="Text", ver="3",
                                          value=f"{sl_condition_object[obj][tuple_mod[0]][num_step][cond]}")
                            ET.SubElement(object_cond, 'init', target="_Set", ver="3",
                                          value=f"System.GRH.{cond.replace('Cmd_In', 'Par_In')}")
                            ET.SubElement(object_cond, 'init', target="_Condition_step", ver="5",
                                          value=f"System.GRH.{cond}")
                            ET.SubElement(object_cond, 'init', target="_MOD", ver="3", ref="here._MOD")
                            ET.SubElement(object_cond, 'init', target="_init_APSource", ver="3",
                                          ref="here.ApSource_CurrentForm")
                            ET.SubElement(object_cond, 'init', target="_Height", ver="3", value=f"{_height}")
                        # В противном случае считаем, что это просто команда
                        # создаём соответствующий объект
                        else:
                            object_cond = ET.SubElement(root_type,
                                                        'object', access_modifier="private",
                                                        name=f"Set_{num_step}_{cond}",
                                                        display_name=f"Set_{num_step}_{cond}",
                                                        uuid=f"{uuid.uuid4()}",
                                                        base_type="Set",
                                                        base_type_id=sl_uuid_base.get('Set', ''), ver="3")
                            ET.SubElement(object_cond, 'designed', target='X',
                                          value=f"{x_start_cond + dx_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Y',
                                          value=f"{y_start_cond + dy_cond}", ver="3")
                            ET.SubElement(object_cond, 'designed', target='Rotation', value="0", ver="3")
                            ET.SubElement(object_cond, 'init', target="Text", ver="3",
                                          value=f"{sl_condition_object[obj][tuple_mod[0]][num_step][cond]}")
                            ET.SubElement(object_cond, 'init', target="_Set", ver="3",
                                          value=f"System.GRH.{cond}")
                            ET.SubElement(object_cond, 'init', target="Point", ver="3",
                                          value=f"{num_step}")  # Какое значение?
                            ET.SubElement(object_cond, 'init', target="_CurPoint", ver="3",
                                          value=f"System.GRH.{tuple_mod[0]}_Point")
                            ET.SubElement(object_cond, 'init', target="_MOD", ver="3", ref="here._MOD")
                            ET.SubElement(object_cond, 'init', target="_Height", ver="3", value=f"{_height}")
                            ET.SubElement(object_cond, 'init', target="_init_APSource", ver="3",
                                          ref="here.ApSource_CurrentForm")
                            ET.SubElement(object_cond, 'designed', target="Opacity", value="1", ver="4")
                        # Переходим к следующему Condу в группе по И, добавляем приращение,
                        # если ещё не закончили шагать
                        if len(conditions) > 1 and [i for i in conditions if 'Par_In' not in i][-1] != cond:
                            dy_cond += 20 * _height
                    # Если разбивка по ИЛИ выявила больше одного элемента, то добавим строчку "ИЛИ"
                    if len(tmp_sl_or) > 1 and list(tmp_sl_or.keys())[-1] != or_bla:
                        dy_cond += 20 * _height
                        object_text_or = ET.SubElement(root_type,
                                                       'object', access_modifier="private",
                                                       name=f"Set_OR_{num_step}_{or_bla}",
                                                       display_name=f"Set_OR_{num_step}_{or_bla}",
                                                       uuid=f"{uuid.uuid4()}",
                                                       base_type="Set_OR",
                                                       base_type_id=sl_uuid_base.get('Set_OR', ''), ver="4")
                        ET.SubElement(object_text_or, 'designed', target='X',
                                      value=f"{x_start_cond + dx_cond}", ver="4")
                        ET.SubElement(object_text_or, 'designed', target='Y',
                                      value=f"{y_start_cond + dy_cond}", ver="4")
                        ET.SubElement(object_text_or, 'designed', target='Rotation', value="0", ver="4")
                        ET.SubElement(object_text_or, 'init', target="Text", ver="4", value=f"ИЛИ")
                        ET.SubElement(object_text_or, 'init', target="_init_APSource", ver="4",
                                      ref=f"here.ApSource_CurrentForm")
                        ET.SubElement(object_text_or, 'init', target="Point", ver="4",
                                      value=f"{num_step}")  # Какое значение?
                        ET.SubElement(object_text_or, 'init', target="_CurPoint", ver="4",
                                      value=f"System.GRH.{tuple_mod[0]}_Point")
                        ET.SubElement(object_text_or, 'init', target="_MOD", ver="4", ref="here._MOD")
                        # Потом будет удалено, возможно!!!
                        # ET.SubElement(object_text_or, 'init', target="_Set", ver="4", value="System")
                        ET.SubElement(object_text_or, 'init', target="_Height", ver="3", value=f"{_height}")
                        # y_cond += 20 # определять по-другому

                    # Добавляем отступ, если ещё не закончили шагать по группам ИЛИ
                    if len(tmp_sl_or) > 1 and list(tmp_sl_or.keys())[-1] != or_bla:
                        dy_cond += 20 * _height

                # Добавляем команды
                # Для команд определяем, насколько её расширять
                _height = (round(max_next_step / len(sl_com), 3) if sl_com else 1.0)
                for alg_com, rus_com in sl_com.items():
                    # print(f'{tuple_mod[0]}:', alg_com.replace(f'{tuple_mod[0]}_', ''), rus_com,)
                    # Определяем имя команды без префикса её режима
                    alg_without_prefmod = alg_com.replace(f'{tuple_mod[0]}_', '', 1)
                    # Если команда запускает режим, то добавляем линк-команду
                    if '_START' in alg_without_prefmod and alg_without_prefmod.replace('_START', '') in \
                            sl_submodes_object[obj]:
                        object_command = ET.SubElement(root_type,
                                                       'object', access_modifier="private",
                                                       name=f"Cmd_Link_{num_step}_{alg_com}",
                                                       display_name=f"Cmd_Link_{num_step}_{alg_com}",
                                                       uuid=f"{uuid.uuid4()}",
                                                       base_type="Cmd_Link",
                                                       base_type_id=sl_uuid_base.get('Cmd_Link', ''), ver="3")
                        ET.SubElement(object_command, 'designed', target='X', value=f"{x_start_com + dx_com}",
                                      ver="3")
                        ET.SubElement(object_command, 'designed', target='Y', value=f"{y_start_com + dy_com}",
                                      ver="3")
                        ET.SubElement(object_command, 'designed', target='Rotation', value="0", ver="3")
                        ET.SubElement(object_command, 'init', target="Text", ver="3", value=f"{rus_com}")
                        ET.SubElement(object_command, 'init', target="Point", ver="3",
                                      value=f"{num_step}")  # Какое значение?
                        ET.SubElement(object_command, 'init', target="_init_Object", ver="3", value=f"System")
                        ET.SubElement(object_command, 'init', target="_TAG", ver="3",
                                      value=f"GRH.{tuple_mod[0]}_Point")
                        ET.SubElement(object_command, 'init', target="_MOD", ver="3", ref="here._MOD")
                        # Команде даём расширение
                        # (Число строк)=максимум по командам и условиям/количество команд в шаге
                        ET.SubElement(object_command, 'init', target="_Height", ver="3", value=f"{_height}")
                        ET.SubElement(object_command, 'init', target="_init_APSource", ver="3",
                                      ref="here.ApSource_CurrentForm")
                        # Добавляем открытие по клику
                        name_open = f"AlgVisual_{alg_without_prefmod.replace('_START', '')}_{obj[0]}"
                        object_handler = ET.SubElement(
                            object_command, 'do-on', access_modifier="private",
                            name=f"Handler_Open_{name_open}",
                            display_name=f"Handler_Open_{name_open}",
                            ver="5", event="MouseClick", form_action="open", form_by_id="false")
                        object_open_in_handler = ET.SubElement(object_handler, 'object', access_modifier="private",
                                                               uuid=f"{uuid.uuid4()}",
                                                               base_type=f"{name_open}",
                                                               base_type_id=f"{sl_page_uuid.get(name_open, '')}",
                                                               ver="5")
                        ET.SubElement(object_open_in_handler, 'init', target="_AbonentPath", ver="5",
                                      ref=f"here._AbonentPath")
                        ET.SubElement(object_open_in_handler, 'init', target="Link_MainControl", ver="5",
                                      ref=f"here.Link_MainControl")
                        object_open_in_handler_open_from = ET.SubElement(object_open_in_handler,
                                                                         'init', target="OpenFrom", ver="5")
                        el = ET.SubElement(object_open_in_handler_open_from, 'expr')
                        el.text = f'yopta_on![CDATA[here.OpenFrom + ";" + here.WindowCaption]]yopta_off'
                    else:
                        # Если команда не запускает подрежим,
                        # то делаем добавляем обычную команду
                        object_command = ET.SubElement(root_type,
                                                       'object', access_modifier="private",
                                                       name=f"Cmd_{num_step}_{alg_com}",
                                                       display_name=f"Cmd_{num_step}_{alg_com}",
                                                       uuid=f"{uuid.uuid4()}",
                                                       base_type="Cmd",
                                                       base_type_id=sl_uuid_base.get('Cmd', ''), ver="3")
                        ET.SubElement(object_command, 'designed', target='X', value=f"{x_start_com + dx_com}",
                                      ver="3")
                        ET.SubElement(object_command, 'designed', target='Y', value=f"{y_start_com + dy_com}",
                                      ver="3")
                        ET.SubElement(object_command, 'designed', target='Rotation', value="0", ver="3")
                        ET.SubElement(object_command, 'init', target="Text", ver="3", value=f"{rus_com}")
                        ET.SubElement(object_command, 'init', target="_init_Object", ver="3", value=f"System")
                        ET.SubElement(object_command, 'init', target="_TAG", ver="3",
                                      value=f"GRH.{tuple_mod[0]}_Point")
                        ET.SubElement(object_command, 'init', target="Point", ver="3",
                                      value=f"{num_step}")  # Какое значение?
                        ET.SubElement(object_command, 'init', target="_MOD", ver="3", ref="here._MOD")
                        ET.SubElement(object_command, 'init', target="_init_APSource", ver="3",
                                      ref="here.ApSource_CurrentForm")
                        # Команде даём расширение
                        # (Число строк)=максимум по командам и условиям/количество команд в шаге
                        ET.SubElement(object_command, 'init', target="_Height", ver="3", value=f"{_height}")
                        ET.SubElement(object_command, 'designed', target="Opacity", value="1", ver="4")

                    # Переходим к следующей команде, добавляем приращение, если ещё не закончили шагать
                    if len(sl_com) > 1 and list(sl_com.keys())[-1] != alg_com:
                        # Приращение добавляем с учётом расширения шага
                        dy_com += 20 * _height

                # Номеру шага даём расширение(Число строк), равное максимальному из команд и условий перехода
                ET.SubElement(object_num_step, 'init', target="_Height", ver="3", value=f"{max_next_step}")

            ET.SubElement(root_type, 'designed', target='Width', value=f"{gor_base}", ver="2")
            # Высота мнемосхемы - сумма максимумов*20+ величина headlinайна
            ET.SubElement(root_type, 'designed', target='Height', value=f"{max_sum * 20 + 30}",
                          ver="2")  # vert_base
            # size_shirina = 1600
            # window_height = 900
            ET.SubElement(root_type, 'designed', target="WindowWidth", value=f"{gor_base}", ver="2")
            ET.SubElement(root_type, 'designed', target="WindowHeight", value=f"{int(max_sum * 20 + 30)}", ver="2")

            # Добавляем на каждую мнемосхему уведомляющий стринг, откуда открыли
            ET.SubElement(root_type, 'object', access_modifier="private",
                          name=f"OpenFrom",
                          display_name=f"OpenFrom",
                          uuid=f"{uuid.uuid4()}",
                          base_type="notifying_string",
                          base_type_id=sl_uuid_base.get('notifying_string', ''), ver="3")

            # Для каждой мнемосхемы добавляем экшон открытия главного окна 01_FormAlg
            object_open = ET.SubElement(root_type, 'object', access_modifier="private",
                                        name=f"Open_01_FormAlg",
                                        display_name=f"Open_01_FormAlg",
                                        uuid=f"{uuid.uuid4()}",
                                        base_type="Action",
                                        base_type_id=sl_uuid_base.get('Action', ''), ver="3")
            ET.SubElement(object_open, 'designed', target="Enabled", value=f"true", ver="3")
            ET.SubElement(object_open, 'designed', target="InvokeTrigger", value=f"false", ver="3")
            object_handler = ET.SubElement(object_open, 'do-on', access_modifier="private",
                                           name=f"Handler_Open_01_FormAlg",
                                           display_name=f"Handler_Open_01_FormAlg",
                                           ver="3", event="Invoked", form_action="open", form_by_id="false")
            name_open = f"01_FormAlg_{obj[0]}"
            object_open_in_handler = ET.SubElement(object_handler, 'object', access_modifier="private",
                                                   uuid=f"{uuid.uuid4()}",
                                                   base_type=f"{name_open}",
                                                   base_type_id=f"{sl_page_uuid.get(name_open, '')}", ver="3")
            ET.SubElement(object_open_in_handler, 'init', target="_AbonentPath", ver="3",
                          ref=f"here._AbonentPath")
            ET.SubElement(object_open_in_handler, 'init', target="Link_MainControl", ver="5",
                          ref=f"here.Link_MainControl")

            #
            # Добавляем экшоны открытия главных режимов из подрежимов
            for back_mod in sl_object_modes_to_modes[obj][tuple_mod[0]]:
                object_open = ET.SubElement(root_type, 'object', access_modifier="private",
                                            name=f"Open_{back_mod}",
                                            display_name=f"Open_{back_mod}",
                                            uuid=f"{uuid.uuid4()}",
                                            base_type="Action",
                                            base_type_id=sl_uuid_base.get('Action', ''), ver="3")
                ET.SubElement(object_open, 'designed', target="Enabled", value=f"true", ver="3")
                ET.SubElement(object_open, 'designed', target="InvokeTrigger", value=f"false", ver="3")
                object_handler = ET.SubElement(object_open, 'do-on', access_modifier="private",
                                               name=f"Handler_Open_{back_mod}",
                                               display_name=f"Handler_Open_{back_mod}",
                                               ver="3", event="Invoked", form_action="open", form_by_id="false")
                name_back_mod = f"AlgVisual_{back_mod}_{obj[0]}"
                object_open_in_handler = ET.SubElement(
                    object_handler, 'object', access_modifier="private",
                    uuid=f"{uuid.uuid4()}",
                    base_type=name_back_mod,
                    base_type_id=f"{sl_page_uuid.get(name_back_mod, '')}", ver="3")
                ET.SubElement(object_open_in_handler, 'init', target="_AbonentPath", ver="3",
                              ref=f"here._AbonentPath")
                ET.SubElement(object_open_in_handler, 'init', target="Link_MainControl", ver="5",
                              ref=f"here.Link_MainControl")
                ET.SubElement(object_open_in_handler, 'init', target="OpenFrom", ver="5", ref="here.OpenFrom")

            #
            # Добавляем кнопку обратного перехода
            object_button_back = ET.SubElement(root_type, 'object', access_modifier="private",
                                               name=f"Back_Button",
                                               display_name=f"Back_Button",
                                               uuid=f"{uuid.uuid4()}",
                                               base_type="Back",
                                               base_type_id=sl_uuid_base.get('Back', ''), ver="5")
            for target, target_value in {'X': '420', 'Y': '0', 'ZValue': '0', 'Rotation': '0'}.items():
                ET.SubElement(object_button_back, 'designed', target=target, value=target_value, ver="5")
            # Добавляем в кнопку События
            # CDATA('me.BrushColor = 0xffffffff;\nme.BrushStyle = 1;')

            object_mouse_click = ET.SubElement(object_button_back, 'do-on', access_modifier="private",
                                               name=f"Handler_mouse_click",
                                               display_name=f"Handler_mouse_click",
                                               ver="3", event='MouseClick')
            el = ET.SubElement(object_mouse_click, 'body', kind="om")
            el_text = ''
            for back_mod in ('01_FormAlg',) + sl_object_modes_to_modes[obj][tuple_mod[0]]:
                el_text += f'if (String.EndsWith(OpenFrom, "{back_mod}")) Open_{back_mod}.Invoke();\n'
            el_text += f'LIndex : int4 = String.LastIndexOf(OpenFrom, ";");\n'
            el_text += f'if (LIndex yopta_off 0) OpenFrom = ' \
                       f'String.Remove(OpenFrom, LIndex, String.Length(OpenFrom) - LIndex);'
            el.text = f'yopta_on![CDATA[{el_text}]]yopta_off'

            # Нормируем и записываем страницу мнемосхемы
            temp = ET.tostring(root_type).decode('UTF-8')
            check_diff_mnemo(new_data=multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
                                                                                     pretty_print=True,
                                                                                     encoding='unicode')),
                             check_path=os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo'),
                             file_name_check=f"{name_mnemo}.omobj",
                             message_print=f'Требуется заменить мнемосхему {name_mnemo}.omobj'
                             )

            # with open(os.path.join('File_for_Import', 'Mnemo', 'Control_Mnemo',
            #                        f"{name_mnemo}.omobj"),
            #           'w', encoding='UTF-8') as f_out:
            #     f_out.write(multiple_replace_xml_mnemo(lxml.etree.tostring(lxml.etree.fromstring(temp),
            #                                                                pretty_print=True, encoding='unicode')))

            # sl_create[tuple(sorted(tuple(_sl_cpu_obj.keys())))] += (f"AlgVisual_{tuple_mod[0]}",)


# Функция определения указанного количества числа (какое число на указанной по счёту позиции, начиная с нуля)
def digit_count(st: str, num: int):
    list_st = [i for i in st.split('_') if i.isdigit()]
    if len(list_st) - 1 >= num:
        return list_st[num]
    return '0'
