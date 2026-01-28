# Flask Time Complexity Visualizer

Flask app that analyzes algorithm time complexity and generates corresponding graphs.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the app:
```bash
python app.py
```

Server runs on `http://localhost:3000`

## Usage

Send GET request to `/analyze` with query parameters:

- `algo` - algorithm name (required)
- `n` - max input size (required)
- `steps` - number of steps to test (required)

Example:
```
http://localhost:3000/analyze?algo=bubble&n=1000&steps=10
```

## Supported Algorithms

- `bubble` - O(n²)
- `linear` - O(n)
- `binary` - O(log n)
- `nested/exponential` - O(2^n)

## Response Format

Returns JSON with:
- `algo` - algorithm name
- `items` - max input size
- `steps` - number of steps
- `start_time` - start timestamp (microseconds)
- `end_time` - end timestamp (microseconds)
- `total_time_ms` - total analysis time in milliseconds
- `time_complexity` - Big O notation
- `path_to_graph` - base64 encoded PNG graph image

Example response:
```json
{
  "algo": "bubble",
  "items": 1000,
  "steps": 10,
  "start_time": 36458241,
  "end_time": 239759234,
  "total_time_ms": 3.45,
  "time_complexity": "O(n²)",
  "path_to_graph": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```
