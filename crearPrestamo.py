import boto3
import json
from datetime import datetime
from decimal import Decimal
import uuid

dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')
cuentas_table = dynamodb.Table('TABLA-CUENTAS')
pagos_table = dynamodb.Table('TABLA-PAGOS')

# Función auxiliar para convertir Decimal a tipos serializables
def decimal_to_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
    elif isinstance(obj, list):
        return [decimal_to_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_serializable(value) for key, value in obj.items()}
    return obj

def lambda_handler(event, context):
    try:
        # Obtener datos de la solicitud
        data = json.loads(event['body'])
        usuario_id = data['usuario_id']
        cuenta_id = data['cuenta_id']
        monto = Decimal(data['monto'])
        plazo = int(data['plazo'])
        tasa_interes = Decimal(data['tasa_interes'])
        descripcion = data.get('descripcion', '')

        # Verificar que la cuenta exista
        cuenta_response = cuentas_table.get_item(Key={'usuario_id': usuario_id, 'cuenta_id': cuenta_id})
        if 'Item' not in cuenta_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Cuenta no encontrada para este usuario.'})
            }

        # Verificar si el préstamo ya existe
        response = prestamos_table.get_item(Key={'usuario_id': usuario_id, 'prestamo_id': prestamo_id})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'El préstamo ya existe.'})
            }
        
        # Crear el préstamo
        fecha_creacion = datetime.utcnow().isoformat()
        prestamo_item = {
            'usuario_id': usuario_id,
            'prestamo_id': str(uuid.uuid4()),
            'monto': monto,
            'descripcion': descripcion,
            'estado': 'activo',
            'plazo': plazo,
            'tasa_interes': tasa_interes,
            'fecha_creacion': fecha_creacion,
            'fecha_vencimiento': (datetime.utcnow().replace(year=datetime.utcnow().year + int(plazo / 12))).isoformat()
        }

        prestamos_table.put_item(Item=prestamo_item)

        # Actualizar el saldo de la cuenta asociada
        cuenta_actual = cuenta_response['Item']
        nuevo_saldo = cuenta_actual['cuenta_datos']['saldo'] + monto
        cuentas_table.update_item(
            Key={'usuario_id': usuario_id, 'cuenta_id': cuenta_id},
            UpdateExpression='SET cuenta_datos.saldo = :nuevo_saldo',
            ExpressionAttributeValues={':nuevo_saldo': nuevo_saldo}
        )

        # Generar un pago asociado al préstamo
        pago_id = str(uuid.uuid4())
        pago_item = {
            'usuario_id': usuario_id,
            'pago_id': pago_id,
            'titulo': f'Pago del préstamo {prestamo_id}',
            'descripcion': f'Relacionado con el préstamo {prestamo_id}',
            'tipo': 'préstamo',
            'monto': monto + (monto * tasa_interes / 100),  # Incluyendo intereses
            'estado': 'pendiente',
            'fecha': fecha_creacion
        }
        pagos_table.put_item(Item=pago_item)

        return {
            'statusCode': 200,
            'body': {
                'message': 'Préstamo creado exitosamente',
                'prestamo': decimal_to_serializable(prestamo_item),
                'pago_generado': decimal_to_serializable(pago_item)
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno al crear el préstamo', 'details': str(e)})
        }
