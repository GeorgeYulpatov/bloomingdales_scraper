import pandas as pd

# Загрузка данных из файла input.xlsx в DataFrame
df = pd.read_excel('input.xlsx')

# Создание нового столбца для хранения ссылок из столбца my_link, которых нет в столбце cdek_link
df['missing_links'] = df['my_link'][~df['my_link'].isin(df['cdek_link'])]

# Сохранение обновленного DataFrame в файл
df.to_excel('output.xlsx', index=False)
