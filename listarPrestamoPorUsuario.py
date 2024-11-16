import boto3
import json
from boto3.dynamodb.conditions import Key

# Inicializar DynamoDB
dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')

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

        return {
            'statusCode': 200,
            'body': response.get('Items', [])
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
