# sort Greek alphabetically
import csv
import unicodedata
# csv.field_size_limit(500000) # für Pape
with open('Pape-5.4.txt', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    data = list(reader)

def sort_key(row):
    return ''.join(c for item in row for c in unicodedata.normalize("NFD", item.lower()) if unicodedata.category(c) != 'Mn')

data.sort(key=sort_key)

with open('Pape-5.4a.txt', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerows(data)
