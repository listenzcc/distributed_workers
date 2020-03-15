import os

if __name__ == "__main__":
    os.system('start python ./manager/manager.py')
    for j in range(3):
        os.system('start python ./worker/worker.py')