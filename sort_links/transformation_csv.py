import os
import pandas as pd
from tqdm import tqdm

df = pd.read_csv('all_collected_links.csv', engine='python')  # Читает файл CSV bloom.csv в pandas DataFrame,
# который является двухмерной таблицей данных с метками строк и столбцов

for i in tqdm(range(len(df))):  # Проходит по каждой строке в DataFrame в цикле. Индекс каждой строки представлен
    # переменной i, которая используется для поиска значения столбца URL в текущей строке с помощью df.loc[i, 'URL'].
    # Затем код проверяет, содержит ли URL строку #color=, и если да, изменяет URL, удаляя все, что идет после #color=
    url = df.loc[i, 'Full URL']

    if '&CategoryID=' in url:
        # modified_url = url[:url.index('&CategoryID=')]
        modified_url = url.split('&CategoryID=')[0]
    else:
        modified_url = url

    df.loc[i, 'URL'] = modified_url  # Измененный URL записывается обратно в столбец URL текущей строки в DataFrame

df.to_csv('all_collected_links_modified_2.csv', index=False)  # Записывает измененный DataFrame в новый файл CSV
# bloom_modified.csv. Параметр index=False убеждается, что индексы строк не включены в выходном файле
