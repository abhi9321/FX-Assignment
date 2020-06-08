# FX-Assignment
Visit the website https://exchangeratesapi.io/

A. Write a python code to get historic exchange rate for getting of USD INR, USD GBP, USD EUR.
Output expected is a csv file with the following columns
1. Date
2. From Currency
3. To Currency
4. Rate
5. Write a python code to incrementally update the the above created CSV


code usage:


python3 -m venv venv

source venv/bin/activate

pip install -r requirement.txt



`Usage: exchange_rate.py <load_type> <num_days_optional>`

load_type : can be -> latest or history

num_day : for load_type = history, num_day can be in the range of 1 to 15

`sync latest data:`
`python exchange.py latest`

`sync historical data: `
`python exchange.py history 10`
