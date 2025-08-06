import re

text = "Вот пример текста с ссылкой: https://example.com\nhttp://test.org/page"

# Регулярное выражение для поиска ссылок
pattern = r'https?://[^\'"\\<>|\s,]+'

# Поиск всех ссылок
links = re.findall(pattern, text)

print(links)
