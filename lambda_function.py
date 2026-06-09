import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('WebAppData')

def lambda_handler(event, context):
    # Configurar CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    # Manejar preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps('OK')
        }
    
    try:
        method = event['httpMethod']
        
        if method == 'POST':
            # Crear nuevo registro
            body = json.loads(event['body'])
            item_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            item = {
                'id': item_id,
                'timestamp': timestamp,
                'data': body,
                'status': 'active'
            }
            
            table.put_item(Item=item)
            
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Item created successfully',
                    'id': item_id,
                    'timestamp': timestamp
                })
            }
            
        elif method == 'GET':
            # Obtener registros
            response = table.scan()
            items = response['Items']
            
            # Convertir Decimal a float para JSON serialization
            for item in items:
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'items': items,
                    'count': len(items)
                })
            }
            
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
