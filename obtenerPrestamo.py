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
        prestamo_id = data.get('prestamo_id')

        if not usuario_id or not prestamo_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Solicitud inválida',
                    'details': 'El usuario_id y el prestamo_id son obligatorios'
                })
            }

        # Obtener el préstamo de DynamoDB
        response = prestamos_table.get_item(Key={'usuario_id': usuario_id, 'prestamo_id': prestamo_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Préstamo no encontrado'})
            }

        return {
            'statusCode': 200,
            'body': response['Item']
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
