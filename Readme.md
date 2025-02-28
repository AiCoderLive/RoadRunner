Start the project with the following command:
```bash
pip install -r requirements.txt
```
Example of command to send a request to VictimServer.
```bash
url -X POST -H "Content-Type: application/json" -d '{"key":"value"}' http://192.168.56.103:5000/api/basic
```
Execute monitoring.py with the following command:
```bash
python ./src/monitoring.py ./src/results/results.csv --max_time=1
```
```bash
python ./src/monitoring.py ./src/results.csv --use_interval
```

Problems
- look at the data in the results.csv file. There was problem that miliseconds were not being written in the row with the rest of data, but the row below. After that monitoring.py has got a problem to read it.
- ![img.png](img.png)

To start the project"
```bash
conda env create -f environment.yml
```
```bash
conda activate response-predictor
```