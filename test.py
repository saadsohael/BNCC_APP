from random import randint

temp_list = []
cadet_id = ''
std_pass = randint(100001, 199999)
if std_pass in temp_list:
    while std_pass in temp_list:
        std_pass = randint(100001, 199999)
temp_list.append(std_pass)
cadet_id = temp_list[-1]
print(temp_list)