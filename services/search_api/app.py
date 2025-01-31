# services/search_api/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from minio import Minio
import json
import gzip
from io import BytesIO
import datetime
import traceback

app = Flask(__name__)
CORS(app)

# Configure MinIO client
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
def parse_log_line(line):
    """Parse a tab-separated log line into a structured format"""
    try:
        # Split by tabs
        parts = line.strip().split('\t')
        if len(parts) != 3:
            return None
            
        json_data = parts
        
        # Parse the JSON part
        log_data = json.loads(json_data)
        return log_data
        
    except Exception as e:
        print(f"Error parsing log line: {e}")
        return None
    
def process_log_file(obj):
    print(f"\nProcessing file: {obj.object_name}")
    logs = []
    
    try:
        # Get object data
        data = minio_client.get_object('logs', obj.object_name)
        content = data.read()
        print(f"Read {len(content)} bytes")
        
        # Decompress if gzipped
        if obj.object_name.endswith('.gz'):
            try:
                # print("Decompressing gzip content...")
                with gzip.GzipFile(fileobj=BytesIO(content)) as gz:
                    content = gz.read()
                print(f"Decompressed size: {len(content)} bytes")
            except Exception as e:
                print(f"Gzip decompression error: {e}")
                traceback.print_exc()
                return []
        
        # Decode and split into lines
        try:
            text_content = content.decode('utf-8')
            lines = text_content.splitlines()
            # print(f"Found {len(lines)} lines")

            
            for line in lines:
                log_entry = parse_log_line(line)
                if log_entry:
                    logs.append(log_entry)
                
        except UnicodeDecodeError as e:
            print(f"Unicode decode error: {e}")
            return []
            
    except Exception as e:
        print(f"Error reading object: {e}")
        traceback.print_exc()
        return []
    print(f"Successfully parsed {len(logs)} logs")    
    return logs

def search_logs(query, start_time=None, end_time=None, log_level=None, limit=100):
    matching_logs = []
    # print(f"\nStarting search - query: '{query}', level: {log_level}")
    
    try:
        # List all objects
        objects = list(minio_client.list_objects('logs', recursive=True))
        objects.sort(key=lambda x: x.object_name, reverse=True)  # Most recent first
        print(f"Found {len(objects)} files")
        
        for obj in objects:
            logs = process_log_file(obj)
            print(f"Processed {len(logs)} logs from file")
            
            # Apply filters
            for log in logs:
                try:
                    # Check query match
                    if query and query.lower() not in json.dumps(log).lower():
                        continue
                        
                    # Check log level
                    if log_level and log.get('level') != log_level:
                        continue
                        
                    # Check time range
                    if start_time or end_time:
                        log_time = datetime.datetime.fromisoformat(
                            log['timestamp'].replace('Z', '+00:00')
                        )
                        
                        if start_time and log_time < start_time:
                            continue
                        if end_time and log_time > end_time:
                            continue
                    
                    matching_logs.append(log)
                    
                    if len(matching_logs) >= limit:
                        print(f"Reached limit of {limit} logs")
                        return matching_logs
                        
                except Exception as e:
                    print(f"Error filtering log: {e}")
                    continue
                    
    except Exception as e:
        print(f"Search error: {e}")
        traceback.print_exc()
        
    print(f"Returning {len(matching_logs)} matches")
    return matching_logs

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    start = request.args.get('start')
    end = request.args.get('end')
    level = request.args.get('level')
    limit = int(request.args.get('limit', 100))
    
    print(f"\nSearch request - query: {query}, start: {start}, end: {end}, level: {level}")
    
    try:
        start_time = datetime.datetime.fromisoformat(start) if start else None
        end_time = datetime.datetime.fromisoformat(end) if end else None
        
        results = search_logs(query, start_time, end_time, level, limit)
        return jsonify({"results": results})
        
    except Exception as e:
        print(f"API error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/sample', methods=['GET'])
def get_sample():
    """Get a sample of raw logs for debugging"""
    try:
        objects = list(minio_client.list_objects('logs', recursive=True))
        if not objects:
            return jsonify({"error": "No log files found"})
            
        # Get the latest file
        latest_obj = objects[-1]
        print(f"Reading sample from: {latest_obj.object_name}")
        
        data = minio_client.get_object('logs', latest_obj.object_name)
        content = data.read()
        
        if latest_obj.object_name.endswith('.gz'):
            with gzip.GzipFile(fileobj=BytesIO(content)) as gz:
                content = gz.read()
                
        text_content = content.decode('utf-8')
        lines = text_content.splitlines()[:5]  # First 5 lines
        
        return jsonify({
            "filename": latest_obj.object_name,
            "sample_lines": lines
        })
        
    except Exception as e:
        print(f"Sample error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)