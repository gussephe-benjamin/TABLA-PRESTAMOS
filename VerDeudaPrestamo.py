import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
prestamos_table = dynamodb.Table('TABLA-PRESTAMOS')

def lambda_handler(event, context):
    data = event['body']
    usuario_id = data['usuario_id']
    prestamo_id = data['prestamo_id']

    response = prestamos_table.get_item(
        Key={'usuario_id': usuario_id, 'prestamo_id': prestamo_id}
    )

    prestamo = response.get('Item')
    if not prestamo:
        return {'statusCode': 404, 'body': 'Préstamo no encontrado'}

    # Lógica para calcular el interés acumulado si está fuera del plazo
    fecha_creacion = datetime.fromisoformat(prestamo['fecha_creacion'])
    plazo = int(prestamo['plazo'])
    tasa_interes = float(prestamo['tasa_interes'])
    fecha_limite = fecha_creacion + timedelta(days=plazo)

    if datetime.utcnow() > fecha_limite:
        dias_vencidos = (datetime.utcnow() - fecha_limite).days
        interes_extra = dias_vencidos * (tasa_interes / 30)  # Interés diario acumulado

        return {
            'statusCode': 200,
            'body': {
                'prestamo': prestamo,
                'interes_extra': interes_extra
            }
        }

    return {
        'statusCode': 200,
        'body': prestamo
    }
