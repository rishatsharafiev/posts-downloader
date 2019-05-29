# posts-downloader

# virtualenv
Создание
```
virtualenv venv -p python3
```

Активация
```
. venv/bin/activate
```

Деактивация
```
deactivate
```


# Тестирование
```
python -m unittest test_api.TestApi.test_multiple_process_access
python -m unittest test_api.TestApi.test_multiple_threads_access
```