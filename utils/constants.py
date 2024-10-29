import os 
import configparser


# Crear una instancia de ConfigParser para leer el archivo de configuración
parser = configparser.ConfigParser()

# Leer el archivo de configuración ubicado en '../config/config.conf'
# La ruta del archivo se construye utilizando el directorio del archivo actual (__file__)
parser.read(os.path.join(os.path.dirname(__file__), '../config/config.conf'))

# Obtener los valores de 'reddit_secret_key' y 'reddit_client_id' en la sección 'api_keys'
SECRET = parser.get('api_keys', 'reddit_secret_key')
CLIENT_ID = parser.get('api_keys', 'reddit_client_id')

# Obtener los valores de la conexión a la base de datos
DATABASE_HOST = parser.get('database', 'database_host')
DATABASE_NAME = parser.get('database', 'database_name')
DATABASE_PORT = parser.get('database', 'database_port')
DATABASE_USER = parser.get('database', 'database_username')
DATABASE_PASSWORD = parser.get('database', 'database_password')

# Obtener las rutas de entrada y salida
INPUT_PATH = parser.get('file_paths', 'input_path')
OUTPUT_PATH = parser.get('file_paths', 'output_path')

# Obtener los valores de AWS
AWS_ACCESS_KEY = parser.get('aws', 'aws_access_key_id')
AWS_SECRET_KEY = parser.get('aws', 'aws_secret_access_key')
AWS_BUCKET_NAME = parser.get('aws', 'aws_bucket_name')
AWS_REGION = parser.get('aws', 'aws_region')

# Exportar las credenciales como variables de entorno
os.environ['AWS_ACCESS_KEY_ID'] =AWS_ACCESS_KEY
os.environ['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_KEY

#Define the fileds to extract from the reddit API
POST_FIELDS = (
    'id',
    'title',
    'selftext',
    'score',
    'num_comments',
    'author',
    'created_utc',
    'url',
    'over_18',
    'edited',
    'spoiler',
    'stickied'
)