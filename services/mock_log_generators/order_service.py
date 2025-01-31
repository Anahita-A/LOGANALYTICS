# services/order_service.py
import time
import random
import json
import os
from fluent import sender
from datetime import datetime

# Configure Fluentd logger
logger = sender.FluentSender('order-service', host='fluentd', port=24224)

def generate_order():
    order_id = f"ORD-{random.randint(10000, 99999)}"
    products = random.randint(1, 5)
    total = round(random.uniform(10, 500), 2)
    
    return {
        "order_id": order_id,
        "products": products,
        "total": total,
        "customer_id": f"CUST-{random.randint(1000, 9999)}"
    }

def log_event(level, event_type, data):
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "event": event_type,
        "data": data
    }
    
    logger.emit(event_type, log_data)
    # Also print to stdout for debugging
    print(json.dumps(log_data))

def simulate_orders():
    error_rate = float(os.getenv('ERROR_RATE', '0.1'))
    orders_per_minute = int(os.getenv('ORDERS_PER_MINUTE', '10'))
    sleep_time = 60 / orders_per_minute

    log_event('info', 'service_started', {
        "config": {
            "error_rate": error_rate,
            "orders_per_minute": orders_per_minute
        }
    })

    while True:
        try:
            order = generate_order()
            
            # Log order creation
            log_event('info', 'order_created', order)
            
            # Simulate random errors
            if random.random() < error_rate:
                error_types = [
                    "PAYMENT_FAILED",
                    "INVENTORY_UNAVAILABLE",
                    "VALIDATION_ERROR",
                    "SYSTEM_ERROR"
                ]
                error = random.choice(error_types)
                
                log_event('error', 'order_failed', {
                    "error": error,
                    "order_id": order["order_id"]
                })
            else:
                # Log successful order
                log_event('info', 'order_completed', {
                    "order_id": order["order_id"],
                    "processing_time": round(random.uniform(0.1, 2.0), 2)
                })
            
            time.sleep(sleep_time)
        except Exception as e:
            log_event('error', 'system_error', {
                "error": str(e)
            })
            time.sleep(1)  # Wait a bit before retrying

if __name__ == "__main__":
    simulate_orders()