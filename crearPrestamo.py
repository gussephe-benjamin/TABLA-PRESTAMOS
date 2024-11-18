import boto3
import json
from datetime import datetime
from decimal import Decimal, getcontext
import uuid

# Configurar contexto para Decimal
getcontext().prec = 28  # Configurar precisión global

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')

# Función auxiliar para convertir Decimal a tipos JSON serializables
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
        print(f"Datos recibidos: {data}")
        
        usuario_id = data['usuario_id']
        cuenta_id = data['cuenta_id']
        monto = Decimal(str(data['monto']))  # Asegurar que monto sea string antes de convertir
        plazo = int(data['plazo'])
        tasa_interes = Decimal(str(data['tasa_interes']))  # Asegurar que tasa_interes sea string
        descripcion = data.get('descripcion', 'Préstamo solicitado')

        # Generar un ID único para el préstamo
        prestamo_id = str(uuid.uuid4())

        # Cálculo del monto total con intereses
        monto_total = monto + (monto * tasa_interes / Decimal('100'))
        monto_total = monto_total.quantize(Decimal('0.01'))  # Redondear a 2 decimales

        # Crear el préstamo
        fecha_creacion = datetime.utcnow().isoformat()
        prestamo_item = {
            'usuario_id': usuario_id,
            'prestamo_id': prestamo_id,
            'cuenta_id': cuenta_id,
            'monto': monto_total,
            'descripcion': descripcion,
            'estado': 'activo',
            'plazo': plazo,
            'tasa_interes': tasa_interes,
            'fecha_creacion': fecha_creacion,
            'fecha_vencimiento': (datetime.utcnow().replace(year=datetime.utcnow().year + plazo // 12)).isoformat()
        }
        print(f"Préstamo a registrar: {prestamo_item}")

        prestamos_table.put_item(Item=prestamo_item)

        # # Preparar la solicitud para actualizar la cuenta
        # actualizar_cuenta_payload = {
        #     "usuario_id": usuario_id,
        #     "cuenta_id": cuenta_id,
        #     "cuenta_datos": {
        #         "saldo": monto_total,  # Incrementar el saldo de la cuenta
        #         "descripcion": "Actualización por creación de préstamo"
        #     }
        # }

        # # Invocar la función Lambda ModificarCuenta
        # response = lambda_client.invoke(
        #     FunctionName="arn:aws:lambda:us-east-1:316129865556:function:api-cuentas-dev-ModificarCuenta",  # Cambia al ARN si es necesario
        #     InvocationType="RequestResponse",
        #     Payload=json.dumps({"body": actualizar_cuenta_payload})
        # )
        
        # # Leer la respuesta de la invocación
        # cuenta_response = json.loads(response['Payload'].read())
        # if cuenta_response.get('statusCode') != 200:
        #     raise Exception(f"Error al actualizar la cuenta: {cuenta_response.get('body')}")
        

        return {
            'statusCode': 200,
            'body': {
                'message': 'Préstamo creado exitosamente y cuenta actualizada',
                'prestamo': decimal_to_serializable(prestamo_item)
                 # Detalles de la cuenta actualizada
            }
        }

 except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno al crear el préstamo', 'details': str(e)})
        }
