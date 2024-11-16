import boto3
import json
from datetime import datetime

# Inicializar DynamoDB
dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')

def lambda_handler(event, context):
    try:
        # Validar el cuerpo de la solicitud
        data = json.loads(event['body'])
        usuario_id = data.get('usuario_id')
        prestamo_id = data.get('prestamo_id')
        nuevo_estado = data.get('estado')

        if not usuario_id or not prestamo_id or not nuevo_estado:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Solicitud inválida',
                    'details': 'El usuario_id, prestamo_id y el nuevo estado son obligatorios'
                })
            }

        # Actualizar el estado del préstamo
        prestamos_table.update_item(
            Key={'usuario_id': usuario_id, 'prestamo_id': prestamo_id},
            UpdateExpression="SET estado = :estado, fecha_actualizacion = :fecha",
            ExpressionAttributeValues={
                ':estado': nuevo_estado,
                ':fecha': datetime.utcnow().isoformat()
            }
        )

        return {
            'statusCode': 200,
            'body': {
                'message': f'Préstamo {prestamo_id} actualizado correctamente',
                'nuevo_estado': nuevo_estado
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
