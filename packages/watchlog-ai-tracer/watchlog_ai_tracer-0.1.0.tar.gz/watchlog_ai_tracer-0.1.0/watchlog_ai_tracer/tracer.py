import os
import sys
import json
import time
import uuid
import socket
import logging
import tempfile
import threading
import requests
from datetime import datetime, timezone, timedelta
from filelock import FileLock

LOG = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "app": None,
    "agent_url": None,
    "batch_size": 50,
    "flush_on_span_count": 50,
    "max_retries": 3,
    "max_queue_size": 10000,
    "max_field_length": 256,
    "sensitive_fields": ["password", "api_key", "token"],
    "auto_flush_interval": 1.0,    # seconds
    "max_in_memory_spans": 5000,
    "request_timeout": 5.0,        # seconds
    "queue_item_ttl": 10 * 60.0    # seconds
}

def is_running_in_k8s():
    # 1) ServiceAccount token
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        return True
    # 2) cgroup
    try:
        with open("/proc/1/cgroup") as f:
            if "kubepods" in f.read():
                return True
    except IOError:
        pass
    # 3) DNS lookup
    try:
        socket.gethostbyname("kubernetes.default.svc.cluster.local")
        return True
    except socket.error:
        return False

_cached_agent_url = None
def get_agent_url(override=None):
    global _cached_agent_url
    if override:
        return override
    if _cached_agent_url:
        return _cached_agent_url
    if is_running_in_k8s():
        _cached_agent_url = "http://watchlog-node-agent.monitoring.svc.cluster.local:3774"
    else:
        _cached_agent_url = "http://127.0.0.1:3774"
    return _cached_agent_url

class WatchlogTracer:
    def __init__(self, **config):
        self.config = {**DEFAULT_CONFIG, **config}
        if not self.config["app"]:
            raise ValueError("`app` is required in WatchlogTracer config")
        fn = f"watchlog-queue-{self.config['app']}.jsonl"
        self.queue_file = os.path.join(tempfile.gettempdir(), fn)
        self.trace_id = None
        self.active_spans = []
        self.completed_spans = []
        self._lock = FileLock(self.queue_file + ".lock")

        interval = self.config["auto_flush_interval"]
        if interval and interval > 0:
            t = threading.Thread(target=self._background_flush, daemon=True)
            t.start()

    def start_trace(self):
        self.trace_id = f"trace-{uuid.uuid4()}"
        return self.trace_id

    def start_span(self, name, metadata=None):
        if metadata is None:
            metadata = {}
        if not self.trace_id:
            self.start_trace()
        span_id = f"span-{uuid.uuid4()}"
        span = {
            "traceId": self.trace_id,
            "spanId": span_id,
            "app": self.config["app"],
            "parentId": metadata.get("parentId"),
            "name": name,
            "startTime": datetime.now(timezone.utc).isoformat(),
            "metadata": {**{"feature":"","step":"","promptVersion":"","userId":"","label":""}, **metadata}
        }
        self.active_spans.append(span)
        return span_id

    def child_span(self, parent_span_id, name, metadata=None):
        md = {"parentId": parent_span_id}
        if metadata:
            md.update(metadata)
        return self.start_span(name, md)

    def end_span(self, span_id, data=None):
        if data is None:
            data = {}
        idx = next((i for i,s in enumerate(self.active_spans) if s["spanId"]==span_id), None)
        if idx is None:
            LOG.warning("end_span: unknown span %s", span_id)
            return
        span = self.active_spans.pop(idx)
        now = datetime.now(timezone.utc)
        span["endTime"] = now.isoformat()
        span["duration"] = int((now - datetime.fromisoformat(span["startTime"])).total_seconds()*1000)
        span["tokens"]   = data.get("tokens",0)
        span["cost"]     = data.get("cost",0)
        span["model"]    = data.get("model","")
        span["provider"] = data.get("provider","")
        span["input"]    = self._sanitize("input", data.get("input",""))
        span["output"]   = self._sanitize("output", data.get("output",""))
        span["status"]   = self._determine_status(span)
        self.completed_spans.append(span)

        if len(self.completed_spans) >= self.config["flush_on_span_count"]:
            batch = self.completed_spans[:self.config["flush_on_span_count"]]
            self.completed_spans = self.completed_spans[self.config["flush_on_span_count"]:]
            self._enqueue(batch)

    def send(self):
        # end all open
        for s in list(self.active_spans):
            self.end_span(s["spanId"])
        # enqueue all remaining
        if self.completed_spans:
            all_spans = self.completed_spans[:]
            self.completed_spans.clear()
            self._enqueue(all_spans)
            # attempt an immediate flush
            try:
                self.flush_queue()
            except Exception as e:
                LOG.error("send flush failed: %s", e)

    def _enqueue(self, spans):
        try:
            with self._lock:
                lines = []
                if os.path.exists(self.queue_file):
                    with open(self.queue_file,"r") as f:
                        lines = [l for l in f.read().splitlines() if l.strip()]
                # purge TTL
                now = time.time()
                ttl = self.config["queue_item_ttl"]/1000.0
                kept = []
                for l in lines:
                    try:
                        span = json.loads(l)
                        ts = datetime.fromisoformat(span["startTime"]).timestamp()
                        if now - ts <= ttl:
                            kept.append(l)
                    except:
                        pass
                # append new
                for s in spans:
                    kept.append(json.dumps(s))
                # rotate if too big
                if len(kept) > self.config["max_queue_size"]:
                    kept = kept[-self.config["max_queue_size"]:]
                with open(self.queue_file,"w") as f:
                    f.write("\n".join(kept)+"\n")
        except Exception as e:
            LOG.error("enqueue error: %s", e)

    def flush_queue(self):
        if not os.path.exists(self.queue_file):
            return
        with self._lock:
            with open(self.queue_file,"r") as f:
                lines = [l for l in f.read().splitlines() if l.strip()]
            spans = [json.loads(l) for l in lines]
            if spans:
                url = f"{get_agent_url(self.config['agent_url'])}/ai-tracer"
                for i in range(0, len(spans), self.config["batch_size"]):
                    chunk = spans[i:i+self.config["batch_size"]]
                    self._retry_post(url, chunk)
            # clear file
            try:
                os.remove(self.queue_file)
            except OSError:
                pass

    def _background_flush(self):
        while True:
            time.sleep(self.config["auto_flush_interval"])
            try:
                self.flush_queue()
            except Exception:
                pass

    def _retry_post(self, url, data):
        for attempt in range(self.config["max_retries"]):
            try:
                requests.post(
                    url, json=data,
                    headers={"Content-Type":"application/json"},
                    timeout=self.config["request_timeout"]
                )
                return
            except Exception as e:
                time.sleep((2**attempt)*0.1)
        LOG.error("failed to POST after %d retries", self.config["max_retries"])

    def _determine_status(self, span):
        if not span.get("output"):
            return "Error"
        if span.get("duration",0) > 10000:
            return "Timeout"
        return "Success"

    def _sanitize(self, field, value):
        # redact sensitive fields & truncate
        v = value
        if isinstance(v, dict):
            v = v.get(field, "")
        s = json.dumps(v)
        for fld in self.config["sensitive_fields"]:
            s = s.replace(fld, "[REDACTED]")
        if len(s) > self.config["max_field_length"]:
            s = s[:self.config["max_field_length"]] + "...[TRUNCATED]"
        return s
