from flask import Flask, request, jsonify, send_file
import time
import os
import io
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
image_cache = {}
analysis_cache = {}

CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', 'igaime')
CLOUDINARY_UPLOAD_PRESET = os.environ.get('CLOUDINARY_UPLOAD_PRESET', 'ljpslqnr')

def upload_to_cloudinary(img_data, public_id_prefix='complexity_graph'):
    url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/upload"
    files = {'file': (f'{public_id_prefix}.png', img_data, 'image/png')}
    data = {'upload_preset': CLOUDINARY_UPLOAD_PRESET}
    try:
        r = requests.post(url, files=files, data=data, timeout=30)
        if r.status_code == 200:
            return r.json().get('secure_url')
    except Exception:
        pass
    return None

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

def nested_exponential(n):
    result = 0
    for i in range(n):
        for j in range(2 ** i):
            result += 1
    return result

def analyze_algorithm(algo_name, n, steps, base_url):
    algorithms = {
        'bubble': lambda size: bubble_sort(list(range(size, 0, -1))),
        'linear': lambda size: linear_search(list(range(size)), size - 1),
        'binary': lambda size: binary_search(list(range(size)), size - 1),
        'nested/exponential': lambda size: nested_exponential(size)
    }
    
    algo_func = algorithms.get(algo_name.lower())
    if not algo_func:
        return None
    
    start_time = time.time()
    input_sizes = []
    execution_times = []
    
    step_size = max(1, n // steps) if steps > 0 else 1
    current_n = step_size
    
    while current_n <= n:
        algo_start = time.time()
        algo_func(current_n)
        algo_end = time.time()
        
        input_sizes.append(current_n)
        execution_times.append((algo_end - algo_start) * 1000)
        current_n += step_size
    
    end_time = time.time()
    total_time_ms = (end_time - start_time) * 1000
    
    complexity_map = {
        'bubble': 'O(n²)',
        'bubblesort': 'O(n²)',
        'linear': 'O(n)',
        'linear search': 'O(n)',
        'binary': 'O(log n)',
        'nested': 'O(2^n)',
        'exponential': 'O(2^n)',
        'nested/exponential': 'O(2^n)'
    }
    
    time_complexity = complexity_map.get(algo_name.lower(), 'O(unknown)')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(input_sizes, execution_times, 'o-', linewidth=2, markersize=4)
    ax.set_xlabel('Input size (n)', fontsize=12)
    ax.set_ylabel('Running time (ms)', fontsize=12)
    ax.set_title(f'Time Complexity Analysis: {algo_name}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_data = img_buffer.getvalue()
    
    image_id = hashlib.md5(f"{algo_name}_{n}_{steps}_{start_time}".encode()).hexdigest()
    image_cache[image_id] = img_data
    
    plt.close()
    
    cloud_url = upload_to_cloudinary(img_data, public_id_prefix=f'complexity_graph_{image_id}')
    path_to_graph = cloud_url if cloud_url else f"{base_url}/download/{image_id}"
    
    result = {
        'analysis_id': image_id,
        'algo': algo_name,
        'items': n,
        'steps': steps,
        'start_time': int(start_time * 1000000),
        'end_time': int(end_time * 1000000),
        'total_time_ms': round(total_time_ms, 2),
        'time_complexity': time_complexity,
        'path_to_graph': path_to_graph
    }
    analysis_cache[image_id] = result
    return result

@app.route('/analyze', methods=['GET'])
def analyze():
    algo = request.args.get('algo')
    n = request.args.get('n', type=int)
    steps = request.args.get('steps', type=int)
    
    if not algo:
        return jsonify({'error': 'Missing required parameter: algo'}), 400
    if n is None:
        return jsonify({'error': 'Missing required parameter: n'}), 400
    if steps is None:
        return jsonify({'error': 'Missing required parameter: steps'}), 400
    
    if n <= 0 or steps <= 0:
        return jsonify({'error': 'Parameters n and steps must be positive integers'}), 400
    
    base_url = request.url_root.rstrip('/')
    result = analyze_algorithm(algo, n, steps, base_url)
    if result is None:
        return jsonify({'error': f'Unknown algorithm: {algo}'}), 400
    
    return jsonify(result)

@app.route('/retrieve_analysis', methods=['GET'])
def retrieve_analysis():
    analysis_id = request.args.get('analysis_id')
    if not analysis_id:
        return jsonify({'error': 'Missing required parameter: analysis_id'}), 400
    if analysis_id not in analysis_cache:
        return jsonify({'error': 'Analysis not found'}), 404
    return jsonify(analysis_cache[analysis_id])

@app.route('/download/<image_id>', methods=['GET'])
def download_image(image_id):
    if image_id not in image_cache:
        return jsonify({'error': 'Image not found'}), 404
    
    img_data = image_cache[image_id]
    img_buffer = io.BytesIO(img_data)
    img_buffer.seek(0)
    
    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'complexity_graph_{image_id}.png'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
