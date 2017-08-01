# Coinbase price quoting service

Flask microservice used to quote the price of all currency pairs on GDAX API.

## Installation

You'll need [pip](https://pip.pypa.io/en/stable/installing/) installed and ready to use.
You will also need [virtualenv](https://virtualenv.pypa.io/en/stable/installation/).

### Step 1: create a virtualenv and install dependencies.

Once in the project root, open a terminal prompt and run the following commands:

```bash
virtualenv env
pip install -r requirements.txt
```

### Step 2: Run the server

```bash
bin/run
```

That's it! Your service should be listening to new connections on http://localhost:5000

### Step 3: Sample request

```bash
curl -H "Content-Type: application/json" -X POST -d '{
    "action": "buy",
    "base_currency": "BTC",
    "quote_currency": "USD",
    "amount": 1
}' localhost:5000/quote
```

## Testing

The service includes a suite of tests that can be run as follows from the project root.

```bash
python -m test
```
