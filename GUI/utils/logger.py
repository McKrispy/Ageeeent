"""
工作流日志记录器
"""
import time
import json
from typing import Dict, List, Any

class WorkflowLogger:
    """工作流日志记录器"""
    
    def __init__(self):
        self.logs = []
        self.current_phase = ""
        self.status = "idle"
        self.start_time = None
    
    def start_workflow(self):
        """开始工作流"""
        self.start_time = time.time()
        self.status = "running"
        self.add_log("system", "工作流开始", "info")
    
    def end_workflow(self):
        """结束工作流"""
        self.status = "completed"
        duration = time.time() - self.start_time if self.start_time else 0
        self.add_log("system", f"工作流完成，耗时: {duration:.2f}秒", "success")
    
    def add_log(self, phase: str, message: str, log_type: str = "info", data: Any = None):
        """添加日志"""
        log_entry = {
            "timestamp": time.time(),
            "phase": phase,
            "message": message,
            "type": log_type,
            "data": data
        }
        self.logs.append(log_entry)
    
    def get_logs_by_phase(self, phase: str) -> List[Dict]:
        """获取指定阶段的日志"""
        return [log for log in self.logs if log["phase"] == phase]
    
    def get_all_logs(self) -> List[Dict]:
        """获取所有日志"""
        return self.logs
    
    def get_summary(self) -> Dict:
        """获取工作流摘要"""
        return {
            "status": self.status,
            "total_logs": len(self.logs),
            "phases": list(set(log["phase"] for log in self.logs)),
            "duration": time.time() - self.start_time if self.start_time else 0
        }
    
    def export_logs(self, format: str = "json") -> str:
        """导出日志"""
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
        """清除日志"""
        self.logs = []
        self.current_phase = ""
        self.status = "idle"
        self.start_time = None