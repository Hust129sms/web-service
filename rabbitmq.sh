rabbitmq-server
export DEV_DATABASE_URL=mysql+pymysql://root:junge123@localhost:3306/fiiyu
celery worker -A celery_runner --loglevel=info

