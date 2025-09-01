import time
import json
from typing import Dict, List, Any

class WorkflowLogger:
    def __init__(self):
        self.logs = []
        self.current_phase = ""
        self.status = "idle"
        self.start_time = None
    
    def start_workflow(self):
        self.start_time = time.time()
        self.status = "running"
        self.add_log("system", "Workflow started", "info")
    
    def end_workflow(self):
        self.status = "completed"
        duration = time.time() - self.start_time if self.start_time else 0
        self.add_log("system", f"Workflow completed, duration: {duration:.2f} seconds", "success")
    
    def add_log(self, phase: str, message: str, log_type: str = "info", data: Any = None):
        log_entry = {
            "timestamp": time.time(),
            "phase": phase,
            "message": message,
            "type": log_type,
            "data": data
        }
        self.logs.append(log_entry)
    
    def get_logs_by_phase(self, phase: str) -> List[Dict]:
        return [log for log in self.logs if log["phase"] == phase]
    
    def get_all_logs(self) -> List[Dict]:
        return self.logs
    
    def get_summary(self) -> Dict:
        return {
            "status": self.status,
            "total_logs": len(self.logs),
            "phases": list(set(log["phase"] for log in self.logs)),
            "duration": time.time() - self.start_time if self.start_time else 0
        }
    
    def export_logs(self, format: str = "json") -> str:
        if format == "json":
            return json.dumps(self.logs, ensure_ascii=False, indent=2)
        elif format == "text":
            lines = []
            for log in self.logs:
                timestamp = time.strftime("%H:%M:%S", time.localtime(log["timestamp"]))
                lines.append(f"[{timestamp}] [{log['phase']}] {log['message']}")
            return "\n".join(lines)
        return ""

    def clear_logs(self):
        self.logs = []
        self.current_phase = ""
        self.status = "idle"
        self.start_time = None