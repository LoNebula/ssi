import subprocess
import os
import threading
import queue

# 環境のパスがご自身のものと合っているか確認してください
PYTHON_EXE = r"C:\Users\shogo\anaconda3\envs\movella\python.exe"
SCRIPT_PATH = r"C:\ssi\lonebula\movella_worker.py"

def getOptions(opts, vars):
    pass

def getChannelNames(opts, vars):
    return { 'sensor' : 'Movella DOT 9-ch (Time, Quat, FreeAcc, Status)' }

def initChannel(name, channel, types, opts, vars):
    if name == 'sensor':
        channel.dim = 9
        channel.type = types.FLOAT
        channel.sr = 60.0

def enqueue_output(out, q):
    for line in iter(out.readline, b''):
        line_str = line.decode('utf-8', errors='ignore').strip()
        if not line_str:
            continue
        try:
            vals = [float(x) for x in line_str.split(',')]
            if len(vals) == 9:
                q.put(vals)
            else:
                print(f"[Movella Worker] {line_str}")
        except ValueError:
            print(f"[Movella Worker] {line_str}")
    out.close()

def connect(opts, vars):
    print(f">>> [SSI] Starting Movella in isolated conda environment...")
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONHOME", None)
    clean_env.pop("PYTHONPATH", None)
    
    try:
        proc = subprocess.Popen(
            [PYTHON_EXE, "-u", SCRIPT_PATH],
            env=clean_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    except Exception as e:
        print(f"[Movella Error] Failed to start subprocess: {e}")
        return False
        
    q = queue.Queue()
    t = threading.Thread(target=enqueue_output, args=(proc.stdout, q))
    t.daemon = True
    t.start()
    
    print(">>> [SSI] Waiting for Movella hardware scan to complete. This may take up to 20 seconds...")
    
    try:
        # 【重要】最初のデータパケットが来るまでSSIの進行をブロック（最大60秒待機）
        first_data = q.get(block=True, timeout=60.0)
    except queue.Empty:
        print("[Movella Error] Timeout waiting for Movella to start streaming.")
        proc.terminate()
        return False
    
    print(">>> [SSI] Movella is fully connected and streaming!")
    
    vars['proc'] = proc
    vars['queue'] = q
    vars['last_data'] = first_data
    return True

def read(name, sout, reset, board, opts, vars):
    q = vars['queue']
    last_data = vars['last_data']
    
    while not q.empty():
        try:
            last_data = q.get_nowait()
        except queue.Empty:
            break
            
    vars['last_data'] = last_data
    
    for i in range(sout.num):
        for d in range(9):
            sout[i, d] = last_data[d]

def disconnect(opts, vars):
    if 'proc' in vars:
        print(">>> [SSI] Stopping Movella worker...")
        vars['proc'].terminate()