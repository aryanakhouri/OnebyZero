from fastapi import *
from typing import List
import os
import threading

app = FastAPI()

router = APIRouter()

class Histogram:
    def __init__(self):
        self.histogram_intervals = []
        self.outliers = []
        self.interval_counts = {}
        self.sum = 0
        self.squared_sum = 0
        self.total_input = 0
        self.lock = threading.Lock()
    
    def get_interval(self, target:float):
        for i in self.histogram_intervals:
            if(i[0]<=target and i[1]>target ):
                return i
    

histogram=Histogram()
    

async def read_file_on_startup():
    try:
         file_path=os.getenv('FILE_PATH')
         intervals=[]
        #  if not file_path:
        #      return
        #  print(f"INTERVALS_FILE_PATH: {file_path}")
         with open(file_path, 'r') as read_file:
            for line in read_file:
                start, end = map(float, line.strip().split())
                intervals.append((start, end))

            for child in intervals:
                if (child[0]>=child[1]):
                    continue
                
                overlap_flag=0

                for interval in histogram.histogram_intervals:
                    if(child[0]<interval[1] and child[1]>interval[0]):
                        overlap_flag=1
                        break
                if overlap_flag==1:
                    continue   
                histogram.histogram_intervals.append(child)
                histogram.interval_counts[child]=0           
    except FileNotFoundError:
        print("File not found")

@router.post('/insert_samples')
async def insert_samples(input:List[float]):
    print (histogram.histogram_intervals)
    with histogram.lock:
            for sample in input:
                target_interval = histogram.get_interval(sample)
                # if sample >= target_interval[0] and sample < target_interval[1]:
                if target_interval is not None:
                    histogram.interval_counts[target_interval] += 1
                    histogram.total_input += 1
                    histogram.sum += sample
                    histogram.squared_sum += sample ** 2
                else:
                    histogram.outliers.append(sample)
    return {'message': 'Successfully altered histogram'}

@router.get('/metrics')
async def metrics():
    with histogram.lock:
        statistics=[]
        for child in histogram.histogram_intervals:
            statistics.append(f'{child}:{histogram.interval_counts[child]}')
        
        if histogram.total_input>0:
            sample_mean=histogram.sum/histogram.total_input
        else:
            sample_mean=0

        if histogram.total_input>1:
            variance= (
                (histogram.squared_sum - (histogram.sum ** 2) / histogram.total_input)
                    / (histogram.total_input - 1)
            )
        else:
            variance=0
        
        statistics.append(f'sample mean: {sample_mean}')
        statistics.append(f'sample variance: {variance}')

        print(histogram.outliers)

        if histogram.outliers:
                outliers = ', '.join(map(str, histogram.outliers))
                statistics.append(f'outliers: {outliers}')
        return {'statistics':statistics}
    

@router.get("/hello")
async def hello():
    return {"everything":'successful'}


app.add_event_handler("startup", read_file_on_startup)
app.include_router(router)