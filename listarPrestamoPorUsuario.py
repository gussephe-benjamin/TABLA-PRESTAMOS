import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Inicializar DynamoDB
dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')

# Función auxiliar para convertir Decimal a tipos JSON serializables
def decimal_to_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    elif isinstance(obj, list):
        return [decimal_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_serializable(value) for key, value in obj.items()}
    return obj

def lambda_handler(event, context):
    try:
        # Validar el cuerpo de la solicitud
        data = json.loads(event['body'])
        usuario_id = data.get('usuario_id')

        if not usuario_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Solicitud inválida',
                    'details': 'El usuario_id es obligatorio'
                })
            }

        # Consultar préstamos por usuario_id
        response = prestamos_table.query(
            KeyConditionExpression=Key('usuario_id').eq(usuario_id)
        )

        prestamos = response.get('Items', [])

        # Convertir préstamos a tipos serializables
        prestamos_serializables = decimal_to_serializable(prestamos)

        # Verificar si se encontraron préstamos
        if not prestamos_serializables:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'message': 'No se encontraron préstamos para el usuario especificado.',
                    'usuario_id': usuario_id
                })
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Préstamos encontrados',
                'usuario_id': usuario_id,
                'prestamos': prestamos_serializables
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
