#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
from transliterate import translit, get_available_language_codes


class PasswordGenerator:
    Big = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    Low = 'qwertyuiopasdfghjklzxcvbnm'
    Num = '1234567890'
    Spe = '!@#$%^&*()'

    BI = True  # Пароль должен содержать символы в верхнем регистре (True - да | False - нет)
    LO = True  # Пароль должен содержать символы в нижнем регистре (True - да | False - нет)
    NU = True  # Пароль должен содержать цифры (True - да | False - нет)
    PS = True  # Пароль должен содержать спец символы (True - да | False - нет)

    Password_len = 8
    Password_cou = 1

    def __init__(self):
        """

        :rtype: object
        """
        pass

    def generate(self):

        Pass_Symbol = []
        if self.BI == True:
           Pass_Symbol.extend(list(self.Big))

        if self.LO == True:
           Pass_Symbol.extend(list(self.Low))

        if self.NU == True:
           Pass_Symbol.extend(list(self.Num))

        if self.PS == True:
           Pass_Symbol.extend(list(self.Spe))

        random.shuffle(Pass_Symbol)

        return (''.join([random.choice(Pass_Symbol) for x in range(self.Password_len)]))


class LoginGenerator:

    language = 'ru'
    max_length = 8
    min_length = 3
    separator = (' ', '-', '\'', '"', )
    layouts = ('ооо', 'общество', 'ограниченной', 'ответственностью', 'дополнительной',
               'товарищество', 'производственный', 'кооператив', 'унитарное', 'предприятие',
               'акционерное', 'открытое', 'закрытое', 'зао', 'пао', 'оао', 'пао', 'публичное', )

    def create(self, login, postfix=''):

        if login:
            login = str(login)
        else:
            return -1

        string = []
        flag = False
        for i in self.separator:
            if len(login.split(i)) > 1 and not flag:
                string = login.split(i)
                flag = True
            else:
                continue

        for layout in self.layouts:
            if layout in string:
                string.remove(layout)
            if layout.upper() in string:
                string.remove(layout.upper())
        i = 0
        flag = False

        while i < len(string):
            if len(string[i]) > self.min_length and not flag:

                for li in self.separator:
                    if string[i].find(li) > -1:
                        string[i] = string[i].replace(li, '')

            if postfix:
                result = ''.join(string[i].lower()[:4]) + str(postfix)[:4]
            else:
                result = ''.join(string[i].lower())

            flag = True
            i += 1

        return str(translit(result, language_code=self.language, reversed=True))

    def translit(self, string):
        if string:
            string = str(string)
        else:
            return -1
        return str(translit(string, language_code=self.language, reversed=True)).replace(' ', '_').lower()

