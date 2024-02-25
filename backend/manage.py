import os, sys, time, logging
from settings.settings import BASE_DIR
from flutter_locale import APP_LOCALE


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
def main():
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    os.environ['TZ'] = u"MSK-03"
    if hasattr(time, "tzset"):
        time.tzset()
        
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(name)s - [%(filename)s(%(lineno)d) in %(funcName)s] => %(message)s",
        handlers=[
            logging.FileHandler(BASE_DIR / "cache/logs.log"),
            logging.StreamHandler()
        ]
    )
    APP_LOCALE.load()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    args = sys.argv
        
    if len(args) <= 1:
        args.append('runserver')
        args.append('0.0.0.0:8000')
    execute_from_command_line(args)


if __name__ == '__main__':
    main()
else:
    from django import setup
    setup()
