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
python ./src/monitoring.py ./src/results/results.csv --use_interval
```

Problems
- look at the data in the results.csv file. There was problem that miliseconds were not being written in the row with the rest of data, but the row below. After that monitoring.py has got a problem to read it.
- ![img.png](img.png)

# RoadRunner

## Quick Setup

### Prerequisites
- Miniconda or Anaconda installed on your system
  - [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Automated Setup (Recommended)

#### Windows:
1. Clone this repository
2. Run `setup-env.bat` by double-clicking or from Command Prompt
3. Activate the environment: `conda activate road_runner`

#### Linux/Mac:
1. Clone this repository
2. Make the setup script executable: `chmod +x setup-env.sh`
3. Run the setup script: `./setup-env.sh`
4. Activate the environment: `conda activate road_runner`

### Manual Setup (Alternative)

If the automated setup encounters issues:

pip install tensorflow==2.15.0