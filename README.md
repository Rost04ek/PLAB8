# Лабораторна робота №8
## Варіант 14: Система керування завданнями (Task Management System)
Студент: Козачок Ростислав

### Архітектура:
HTTP Client -> FastAPI REST API -> Service Layer -> Repository Layer -> Database

### Запуск:
```bash
pip install -e ".[test]"
uvicorn task_manager.api:app --reload
```
