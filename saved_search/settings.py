from secrets import STAGING_DB_PASSWD, PROD_DB_PASSWD

DATABASES = {
    'geodata': {
        'NAME': 'geodata',
        'ENGINE': 'mysql',
        'USER': 'db_deuser',
        'PASSWORD': PROD_DB_PASSWD,
        'HOST': 'db-directseo3-util.c9shuxvtcmer.us-east-1.rds.amazonaws.com',
        'PORT': ''
    }
}