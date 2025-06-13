import os
import re
import pandas as pd

def parse_isotherm_file(filename):
    with open(filename, encoding='utf-16') as f:
        content = f.read()
    sample_info = {}

    def safe_search(pattern, text, default='Не найдено'):
        match = re.search(pattern, text)
        return match.group(1) if match else default

    sample_info['Sample'] = safe_search(r'Sample:\s+(.*?)\s*(?:\n|$)', content)
    sample_info['Started'] = safe_search(r'Started:\s+([^\n]+?)\s+Analysis', content)
    sample_info['Completed'] = safe_search(r'Completed:\s+([^\n]+?)\s+Analysis', content)
    sample_info['Sample mass'] = safe_search(r'Sample mass:\s+([^\s]+)\s+g', content)

    def parse_isotherm(section_title):
        # Регулярное выражение для поиска таблицы
        pattern = rf'Relative Pressure \(p/p°\)\s+Quantity Adsorbed \(mmol/g\)[\s\S]+?((?:\d+\.\d+\s+\d+\.\d+\n)+)'  # Захватывает таблицу с числовыми значениями
        match = re.search(pattern, content)

        if match:
            # Извлекаем таблицу (все строки после заголовка)
            table_text = match.group(1).strip()  # Текст таблицы
            lines = table_text.splitlines()  # Разбиваем по строкам

            # Преобразуем каждую строку в пару значений (p/p0, Quantity Adsorbed)
            data = [list(map(float, line.split())) for line in lines if line.strip()]

            # Создаем DataFrame
            df = pd.DataFrame(data, columns=['p/p0', 'Quantity Adsorbed (mmol/g)'])
            return df
        else:
            print(f'Раздел "{section_title}" не найден.')
            return pd.DataFrame()


    adsorption_df = parse_isotherm('Adsorption')
    print(adsorption_df)
    desorption_df = parse_isotherm('Desorption')
    print(desorption_df)

    def add_metadata(df, info):
        meta = pd.DataFrame({
            'p/p0': ['Sample:', 'Started:', 'Completed:', 'Sample mass:'],
            'Quantity Adsorbed (mmol/g)': [info['Sample'], info['Started'], info['Completed'], info['Sample mass']]
        })
        return pd.concat([meta, pd.DataFrame(columns=df.columns), df], ignore_index=True)

    adsorption_df = add_metadata(adsorption_df, sample_info)
    desorption_df = add_metadata(desorption_df, sample_info)
    #print(adsorption_df)
    # output_file = 'isotherm_data.xlsx'
    # with pd.ExcelWriter(output_file) as writer:
    #     adsorption_df.to_excel(writer, sheet_name='Adsorption', index=False)
    #     desorption_df.to_excel(writer, sheet_name='Desorption', index=False)

folders = [f"\\DATA{i}" for i in range(1, 41)]
for folder in folders:
    folder_path = "C:\\Users\\user\\Downloads\\2400" + folder
    smp_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".txt")]
    for file in smp_files:
        file_path = folder_path+"\\"+file
        parse_isotherm_file(file_path)
        break
    break