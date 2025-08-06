import os

DATALAKE_MYSQL_HOST = os.getenv("DATALAKE_MYSQL_HOST","127.0.0.1")  # 表示本地的地址
DATALAKE_MYSQL_PORT = os.getenv("DATALAKE_MYSQL_PORT",3306)  # 端口号
DATALAKE_MYSQL_USER = os.getenv("DATALAKE_MYSQL_USER","root")  # mysql用户名（需自行修改！！！）
DATALAKE_MYSQL_PASSWD = os.getenv("DATALAKE_MYSQL_PASSWD","")  # mysql密码（需自行修改！！！）
DATALAKE_MYSQL_DB = os.getenv("DATALAKE_MYSQL_DB","")  # mysql中创建的数据库名称（需自行修改！！！）

# Redis连接配置
DATALAKE_REDIS_HOST = os.getenv("DATALAKE_REDIS_HOST","127.0.0.1")
DATALAKE_REDIS_PORT = os.getenv("DATALAKE_REDIS_PORT",6379)
DATALAKE_REDIS_DB = os.getenv("DATALAKE_REDIS_DB",13)
DATALAKE_REDIS_PASSWORD = os.getenv("DATALAKE_REDIS_PASSWORD","hubredis2022")
DATALAKE_REDIS_EXPIRE_TIME = os.getenv("DATALAKE_REDIS_EXPIRE_TIME",3600)  # 缓存过期时间（秒）
DATALAKE_REDIS_CACHE_PREFIX = os.getenv("DATALAKE_REDIS_CACHE_PREFIX","mysql_cache:")

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = '3306'
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME",'root')
MYSQL_PASSWORD = 'seentaodata'

datalakes = {
    'minio':{
        'ENDPOINT':'192.168.179.1:9010',
        'ACCESS_KEY':'admin',
        'SECRET_KEY':'adminadmin',
    },
    's3':{
        'AWS_ACCESS_KEY_ID':"",
        'AWS_SECRET_ACCESS_KEY':""
    },
    'gcs':{
        'GOOGLE_APPLICATION_CREDENTIALS_PATH':''
    },
    'azureblob':{
        'ACCOUNT_NAME':'',
        'ACCOUNT_KEY':''}
}

datawarehouses = {
    
    'snowflake':{
        'ACCOUNT_NAME':"",
        'USERNAME':"",
        'PASSWORD':"",
        'HOST':"",
        'PORT':"",
        'DATABASE':"",
        'SCHEMA':"",
        'WAREHOUSE':"",
        'ROLE':""
    },
    
    'bigquery':{
        'GOOGLE_APPLICATION_CREDENTIALS_PATH':''
    },
    
    'redshift':{
        'USERNAME':'',
        'PASSWORD':'',
        'HOST':'',
        'PORT':'',
        'DATABASE':''
    },
    
    'starrocks':{
        'USERNAME':'',
        'PASSWORD':'',
        'HOST':'',
        'PORT':'',
        'DATABASE':''
    }
}

databases = {
    'ailab':{
        'USERNAME':'root',
        'PASSWORD':'seentaodata',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DATABASE':'ailab'
    },
    'postgresql':{
        'USERNAME':'',
        'PASSWORD':'',
        'HOST':'',
        'PORT':'',
        'DATABASE':''
    },
    'mysql':{
        'USERNAME':'root',
        'PASSWORD':'seentaodata',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DATABASE':''
    },
    'mssql':{
        'USERNAME':'sa',
        'PASSWORD':'sa',
        'HOST':'192.168.110.52',
        'PORT':'1433',
        'DATABASE':'UFSystem'
    },
    'oracle':{
        'USERNAME':'root',
        'PASSWORD':'seentaodata',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'DATABASE':'ailab'
    }
}
nosql = {
    
    'elasticsearch':{
        'HOST':"192.168.179.1",
        'USERNAME':"elastic",
        'PASSWORD':"ailab100",
        'PORT':"9200",
        'API_KEY':''
        
    },
    'dynamodb':{
        'AWS_ACCESS_KEY_ID':"",
        'AWS_SECRET_ACCESS_KEY':""
    },
    
    'mongodb':{
        'USERNAME':'root',
        'PASSWORD':'root',
        'HOST':'127.0.0.1',
        'PORT':'27017',
    },
    
    'redis':{
        'HOST':DATALAKE_REDIS_HOST,
        'PORT':DATALAKE_REDIS_PORT,
        'PASSWORD':DATALAKE_REDIS_PASSWORD
    }
    
}
