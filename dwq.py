import json
from pydisque.client import Client

disque = None

class Disque(object):
    def connect(servers):
        global disque
        disque = Client(servers)
        disque.connect()

class Job(object):
    def __init__(s, job_id, body, queue_name):
        s.job_id = job_id
        s.body = body
        s.queue_name = queue_name
        s.status_queues = body.get("status_queues") or []

    def get(queues):
        global disque
        jobs = []
        _jobs = disque.get_job(queues)
        for queue_name, job_id, json_body in _jobs:
            queue_name = queue_name.decode("ascii")
            job_id = job_id.decode("ascii")
            body = json.loads(json_body.decode("utf-8"))
            jobs.append(Job(job_id, body, queue_name))

        return jobs

    def working(s, status):
        global disque
        disque.working(s.job_id)

    def done(s, result):
        for queue in s.status_queues:
            if queue=="$jobid":
                queue = s.job_id
            print("worker: reporting done to %s" % queue)
            disque.add_job(queue, json.dumps({"job_id" : s.job_id, "state" : "done", "result" : result }))

        disque.ack_job(s.job_id)

    def add(queue, body, status_queues=None, **kwargs):
        body["status_queues"] = status_queues or []

        json_body = json.dumps(body)
        return disque.add_job(queue, json_body, **kwargs).decode("ascii")

    def wait(queue):
        _jobs = disque.get_job([queue])
        for queue_name, job_id, json_body in _jobs:
            queue_name = queue_name.decode("ascii")
            job_id = job_id.decode("ascii")
            body = json.loads(json_body.decode("utf-8"))
            disque.fast_ack(job_id)
            return body