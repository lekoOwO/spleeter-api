import os
import shutil
import pathlib

import falcon
from falcon_multipart.middleware import MultipartMiddleware

import uuid as _uuid

from Split import Split

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=int(os.getenv('PROCESSES', "4")))

# 定期清理
from threading import Timer
clean_time = int(os.getenv('CLEAN_TIME', "3600")) # An hour

statuses = {}

TMP_DIR = os.getenv('TMP_DIR', '/tmp/spleeter-api/tmp')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp/spleeter-api/output')

pathlib.Path(TMP_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def get_id():
    return _uuid.uuid4().hex

def clean(uuid):
    global OUTPUT_DIR
    zip_path = os.path.join(OUTPUT_DIR, f'{uuid}.zip')
    os.remove(zip_path)

    global statuses
    statuses.pop(uuid, None) # Remove data

def add_task(uuid, task):
    global statuses
    statuses[uuid] = task

    global clean_time
    t = Timer(clean_time, clean, args=(uuid))
    t.start()

class Status:
    def on_post(self, req, resp):
        global statuses

        uuid = req.media['id']
        
        if uuid not in statuses:
            resp.status = falcon.HTTP_404
            return

        t = statuses[uuid]
        resp.media = {'id': uuid, 'status': 1} # Waiting

        if t.ready():
            data = t.get()
            resp.media['status'] = 0 # Arrived
            resp.media["url"] = f"/download/{uuid}"

        resp.status = falcon.HTTP_200

class Seperate:
    def on_post(self, req, resp):
        global statuses
        global pool
        global OUTPUT_DIR
        global TMP_DIR

        input_file = req.get_param('file')
        if input_file.filename:
            filename = input_file.filename
            file_path = os.path.join(TMP_DIR, filename)
            temp_file_path = file_path + '~'
            open(temp_file_path, 'wb').write(input_file.file.read())
            shutil.move(temp_file_path, file_path)

            uuid = get_id()
            
            stems = req.get_param('stems', '2')
            high_freq = req.get_param_as_bool('highFreq', default=True)

            t = pool.apply_async(Split.split, (file_path, stems, uuid, high_freq))
            add_task(uuid, t)

            resp.media = {'id': uuid}
            resp.status = falcon.HTTP_200

class Download(object):
    def on_get(self, req, resp, uuid):
        global OUTPUT_DIR
        zip_path = os.path.join(OUTPUT_DIR, f'{uuid}.zip')

        if not os.path.exists(zip_path):
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_200
        resp.content_type = 'application/zip'
        with open(zip_path, 'rb') as f:
            resp.body = f.read()

api = falcon.API(middleware=[MultipartMiddleware()])
api.add_route('/status', Status())
api.add_route('/seperate', Seperate())
api.add_route('/download/{uuid}', Download())