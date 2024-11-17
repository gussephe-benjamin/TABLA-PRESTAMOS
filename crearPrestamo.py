import boto3
import json
from datetime import datetime
from decimal import Decimal
import uuid
from botocore.exceptions import ClientError

# Configuración de DynamoDB
dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')
cuentas_table = dynamodb.Table('TABLA-CUENTA')

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
        # Validar que el evento tiene un cuerpo
        if 'body' not in event or not event['body']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Solicitud inválida', 'details': 'No se encontró el cuerpo de la solicitud'})
            }

        # Obtener datos de la solicitud
        data = json.loads(event['body'])
        usuario_id = data.get('usuario_id')
        cuenta_id = data.get('cuenta_id')
        monto = data.get('monto')
        plazo = data.get('plazo')
        tasa_interes = data.get('tasa_interes')

        # Validar que los datos obligatorios están presentes
        if not usuario_id or not cuenta_id or not monto or not plazo or not tasa_interes:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Solicitud inválida', 'details': 'Faltan campos obligatorios'})
            }

        # Convertir monto y tasa de interés a Decimal
        monto = Decimal(str(monto))
        tasa_interes = Decimal(str(tasa_interes))

        # Generar un ID único para el préstamo
        prestamo_id = str(uuid.uuid4())

        # Verificar que la cuenta existe
        try:
            cuenta_response = cuentas_table.get_item(Key={'usuario_id': usuario_id, 'cuenta_id': cuenta_id})
            if 'Item' not in cuenta_response:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Cuenta no encontrada para este usuario.'})
                }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error al consultar la cuenta', 'details': str(e)})
            }

        # Crear el préstamo
        fecha_creacion = datetime.utcnow().isoformat()
        prestamo_item = {
            'usuario_id': usuario_id,
            'prestamo_id': prestamo_id,
            'monto': monto,
            'descripcion': data.get('descripcion', 'Préstamo solicitado'),
            'estado': 'activo',
            'plazo': int(plazo),
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

        # Crear el pago asociado al préstamo
        pago_request = {
            "usuario_id": usuario_id,
            "datos_pago": {
                "titulo": f"Pago del préstamo {prestamo_id}",
                "descripcion": f"Pago relacionado con el préstamo {prestamo_id}",
                "monto": float(monto + (monto * tasa_interes / 100))
            }
        }
        from CrearPagoDeuda import lambda_handler as crearPagoDeuda
        pago_response = crearPagoDeuda({"body": json.dumps(pago_request)}, context)
        pago_data = json.loads(pago_response["body"])

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Préstamo creado exitosamente',
                'prestamo': decimal_to_serializable(prestamo_item),
                'pago_generado': decimal_to_serializable(pago_data)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno al crear el préstamo', 'details': str(e)})
        }
