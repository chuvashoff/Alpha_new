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
import re
pattern = r"GRH\|.*?_"
print(re.sub(r'_START$', '', re.sub(pattern, '', 'GRH|HP_SMD_HP_START')))
