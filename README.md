# Flask Time Complexity Visualizer

Flask app that analyzes algorithm time complexity and generates corresponding graphs.

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

Optional: copy `.env.example` to `.env` and set Cloudinary options (graph images are uploaded to Cloudinary when set):
- `CLOUDINARY_CLOUD_NAME` (default: igaime)
- `CLOUDINARY_UPLOAD_PRESET` (default: ljpslqnr)

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

## Retrieve analysis

GET `/retrieve_analysis?analysis_id=<id>` returns the same JSON as the analyze endpoint for a given analysis. Use the `analysis_id` from the analyze response.

Example:
```
http://localhost:3000/retrieve_analysis?analysis_id=abc123def456...
```

## Supported Algorithms

- `bubble` - O(n²)
- `linear` - O(n)
- `binary` - O(log n)
- `nested/exponential` - O(2^n)

## Response Format

Returns JSON with:
- `analysis_id` - use this with `/retrieve_analysis` to fetch the same result later
- `algo` - algorithm name
- `items` - max input size
- `steps` - number of steps
- `start_time` - start timestamp (microseconds)
- `end_time` - end timestamp (microseconds)
- `total_time_ms` - total analysis time in milliseconds
- `time_complexity` - Big O notation
- `path_to_graph` - clickable URL to the graph image (Cloudinary URL when upload is enabled, otherwise local download URL)

Example response:
```json
{
  "analysis_id": "ad29315a92fdd7cb5cc6b0d8e1e1698a",
  "algo": "bubble",
  "items": 1000,
  "steps": 10,
  "start_time": 36458241,
  "end_time": 239759234,
  "total_time_ms": 3.45,
  "time_complexity": "O(n²)",
  "path_to_graph": "https://res.cloudinary.com/igaime/image/upload/..."
}
```

## Graph storage

When Cloudinary is configured, graphs are uploaded to your cloud bucket and `path_to_graph` is the Cloudinary URL. Otherwise it falls back to a local download URL.
