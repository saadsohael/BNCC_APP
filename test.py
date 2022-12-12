# import sqlite3
#
# test_db = sqlite3.connect('test.db')
# c = test_db.cursor()
#
# # c.execute("CREATE TABLE IF NOT EXISTS 'TEST DATABASE 2' (column1 text)")
# # test_db.commit()
# # column3 = 'column 4'
# # c.execute(f"ALTER TABLE 'TEST DATABASE 2' ADD COLUMN [{column3}]")
# # test_db.commit()
# # test_db.close()
# c.execute("INSERT INTO 'TEST DATABASE 2' VALUES('kuddussya', (?), (?),(?))", ('mridul','chitul','hatul'))
# test_db.commit()
# c.execute("SELECT * FROM 'TEST DATABASE 2'")
# data = c.fetchall()
# print(data)
#
#
# test = '_'.join('my'.split(" "))
# print(test)

text = "father name"
# a = []
# for i in text.split(" "):
#     if i.count("'") > 0:
#         j = i.split("'")
#         a.append(j[0])
#     else:
#         a.append(i)

print('_'.join(text.split(" ")))
