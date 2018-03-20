import random
from stroage import DB
from tqdm import tqdm
import time
from collections import Counter


def maxvalue(dic):
    max_value = max(dic.values())  # maximum value
    max_keys = [k for k, v in dic.items() if v == max_value]
    return random.choice(max_keys)

def remove_none(dic):
    if None in dic.keys():
        del dic[None]
    return dic

random.seed(int(time.time()) - random.randint(1000, 100000))

subjects = ['Sinhala', 'Maths', 'Science', 'History', 'Music']
names = ['Ching Morant', 'Rich Edens', 'Salena Sward', 'Yetta Motton', 'Galen Skaggs', 'Marilyn Bean', 'Inell Durst',
         'Rocky Holter', 'Roselia Hosmer', 'Donald Lofland', 'Rosalina Rowden', 'Tasia Wiggs', 'Lucas Haga',
         'Yael Ferrara', 'Lisabeth Songer', 'Karan Fryer', 'Brande Harrold', 'Melony Matheney', 'Nakesha Lugar',
         'Rema Ardoin', 'Elizabet Flick', 'Emmett Tomaszewski', 'Freddy Roosevelt', 'Brianne Hewlett', 'Jacquie Godbee',
         'Renita Toon', 'Mafalda Landgraf', 'Lavona Hagen', 'Clotilde Altamirano', 'Caleb Curran', 'Lona Lirette',
         'Lashandra Sproull', 'Shelley Groom', 'Kathey Borges', 'Cristy Robicheaux', 'Rayford Perham', 'Irvin Toy',
         'Paulette Woolston', 'Lyle Elsey', 'Brady Segrest', 'Julia Rummel', 'Joyce Marcantel', 'Diana Vicario',
         'Sarita Hands', 'Maye Coggins', 'Hana Paiz', 'Frederick Cambridge', 'Yolonda Boyers', 'Karmen Turley',
         'Elliott Negley']
class_list = ['A', 'B', 'C']

for i in tqdm(range(255)):
    name = random.choice(names)
    number = random.randint(100000000, 999999999)
    DB.put('INSERT INTO Teachers(Teacher_ID,Teacher_Name, Telephone_Number) VALUES (?,?,?)', i, name, number)
    for x in range(1, 6):
        for y in range(1, 9):
            class_ = '{}-{}'.format(random.randint(6, 11), random.choice(class_list))
            subject = random.choice(subjects)
            if random.randint(0, 1) == 1:
                DB.put(
                    "UPDATE Teachers SET `D{0}P{1}-C` = '{2}', `D{0}P{1}-S` = '{3}' WHERE Teacher_ID = {4}".format(x, y,
                                                                                                                   class_,
                                                                                                                   subject,
                                                                                                                   i))

    data = DB.get('SELECT * FROM Teachers WHERE Teacher_ID= (?)', i)[0][3:]

    class_ = remove_none(Counter(data[::2]))
    subject = remove_none(Counter(data[1::2]))

    grade = {}
    for cls in class_:
        if cls[:-2].strip('-') in class_.keys():
            grade[cls[:-2].strip('-')] += class_[cls]
        else:
            grade[cls[:-2].strip('-')] = class_[cls]
    section = {'1-5': 0, '6-8': 0, '9-11': 0, '12-13': 0}

    for key in grade:
        if 8 >= int(key) >= 6:
            section['6-8'] += grade[key]
        elif 11 >= int(key) >= 9:
            section['9-11'] += grade[key]
        elif 13 >= int(key) >= 11:
            section['12-13'] += grade[key]
        elif 5 >= int(key) >= 1:
            section['1-5'] += grade[key]

    classes = list(filter(None, data[1::2]))
    classes = ", ".join(str(x) for x in classes)
    DB.put('INSERT INTO Metadata(Teacher_ID,Section,Grade,Subject,Classes) VALUES (?, ?, ?, ?, ?)',
           i, maxvalue(section), int(maxvalue(grade)), maxvalue(subject), classes)
