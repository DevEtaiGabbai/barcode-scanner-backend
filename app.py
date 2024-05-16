from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from pyzbar.pyzbar import decode
import base64
import requests
import numpy as np
import json

app = Flask(__name__)
CORS(app)

@app.route('/scan', methods=['POST'])
def scan_barcode():
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'error': 'Image not provided'}), 400
        
        image_data = base64.b64decode(data['image'])
        
        nparr = np.fromstring(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        decoded_objects = decode(image)
        
        if not decoded_objects:
            return jsonify({'error': 'No barcode detected'}), 400
        
        barcode_number = decoded_objects[0].data.decode('utf-8')
        
        # Uncomment this line in production
        response = requests.get(f'https://world.openfoodfacts.org/api/v0/product/{barcode_number}.json')
        
        # For development, load example response from file
        # with open('exampleresponse.txt', 'r') as f:
        #     product_info = json.load(f)
        
        if response.status_code != 200:
            return jsonify({'error': 'Product not found'}), 404
        
        product_info = response.json()
        
        return jsonify(product_info), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)