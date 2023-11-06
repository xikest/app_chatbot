import threading
import time
import queue as q
from function_ai import *

def mainChat(kakaorequest):

    run_flag = False
    start_time = time.time()

    cwd = os.getcwd()
    filename = cwd + "/botlog.txt"
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write("")
    else:
        print("File Exists")

    response_queue = q.Queue()
    request_respond = threading.Thread(target=responseOpenAI,
                                       args=(kakaorequest, response_queue, filename))
    request_respond.start()

    while (time.time() - start_time < 3.5):
        if not response_queue.empty():
            response = response_queue.get()
            run_flag = True
            break
        time.sleep(0.01)

    if run_flag == False:
        response = timeover()

    return  response

