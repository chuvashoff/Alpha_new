# from openpyxl import Workbook
# from openpyxl.workbook.defined_name import DefinedName
# from openpyxl import load_workbook
#
# wb = Workbook()
# ws = wb.active
#
# # Создаем локальную переменную smena
# new_range = DefinedName('smena', attr_text='"1"', comment='2')
# wb.defined_names.add(new_range)
# new_range = DefinedName('reportdate', attr_text='"44987"', comment='0')
# wb.defined_names.add(new_range)
# new_range = DefinedName('dd_key', attr_text='"1"', comment='2')
# wb.defined_names.add(new_range)
# new_range = DefinedName('dd_value', attr_text='"Дневная"', comment='1')
# wb.defined_names.add(new_range)
#
#
# ws.oddFooter.center.text = '_'*25
# ws.oddFooter.center.size = 14
# ws.oddFooter.center.font = "Arial,Bold"
#
# # Сохраняем файл
# wb.save("example.xlsx")
#
#
# # wb = load_workbook("Сменная ведомость ГПА-31_шаблон.xlsx")
# #
# # dd = wb.defined_names
#
# # dests = dd.destinations
# #print(dd.keys())
# # print(dd['reportdate'])
# #print(dd['dd_key'])
# #print(dd['dd_value'])
# wb.close()
#
#
# tt = ""
import time
import shutil

terminal_x, _ = shutil.get_terminal_size((80, 20))


def rprint(line):
    print('\r{:{width}}'.format(line, width=terminal_x), end='')


rprint('123456')
time.sleep(1)
rprint('234')
time.sleep(1)



import alpha_domain_pyclient as ng

#GRH|AOss_Cmd_In_3,B,65535,N,S,R,0       ,,0,5626,0   ,65535,0    ,0,0,0,0,////AOss: Команда
#IVG|T            ,R,65535,N,S,R,0.000000,, ,4097,2673,0    ,65535,0,0,0,0,0,////AT8-1. Температура
#GRH|AObs_Point   ,I,65535,N,S,R,0       ,, ,0   ,2666,0    ,65535,0,0,0,0,0,////: Шаг

