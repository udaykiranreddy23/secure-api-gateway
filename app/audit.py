import json
import logging
logger = logging.getLogger("audit")

def record(request_id, username, method, path, status_code):
    logger.info(json.dumps({
        "event": "audit",
        "request_id": request_id,
        "username": username,
        "method": method,
        "path": path,
        "status_code": status_code,
    }))
