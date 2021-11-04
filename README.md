# synchronization

Django app to handle record synchronization using the same idea as SSE (server-sent events)

## Installation instructions

Use the package manager [pipenv](https://pypi.org/project/pipenv/)
 

1. Install pipenv using pip:
```bash
pip install pipenv
```
2. Enter pipenv shell:
```bash
pipenv shell
```
3. Install dependencies in the virtual environment: 
```bash
pipenv install
```
4. Run the migrations: 
```bash
python manage.py migrate
```
5. Run the server: 
```bash
python manage.py runserver
```

## Running tests

```bash
pytest
```

---
## Algorithm

The app depends on the same principle as server-sent events (in which the client sends the last known message_id when he reconnects to get the latest messages)

Here the client will send the `last_sync_date` and he will only get the records that get updated since `last_sync_date`

#### Steps

 
1. the client sends the `last_sync_date`, the app responds with the records that get updated since this time

2. if the client wants to send edited records, he will send it with the `last_sync_date`, the app will sync the sent data , and only return the new data to the user (data that the user does not have, or have but not updated so the client can update it)

3. the client should update
   - his records (override any records returned by the server) 
   - `last_sync_date` 

for more explanation please refer to the code as it has some useful comments on how the endpoint deals with each scenario

---

## Endpoints
there are two endpoints

1. the sync endpoint `https://synchro-v1.herokuapp.com/v1/sync/`

it takes two parameter

- last_sync_date: is a string that represents a DateTime which represent the last_time the client synced with the server

- newly_created_records: optional array of updated records that the client wants to sync with the server

```curl
curl --location --request POST 'https://synchro-v1.herokuapp.com/v1/sync/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "last_sync_date": "2021-10-10T10:40:10",
    "newly_created_records": [{"gtin": "test_4", "updated_at": "2021-11-12T01:11:00", "expiration_date": "2022-05-01T01:11:00"}]
}'
```


this endpoint returns the data which the clients does not have (updated since the last sync)

---

2. `https://synchro-v1.herokuapp.com/v1/readings/`  for returning all the readings for a shop
 

```curl
curl --location --request GET 'https://synchro-v1.herokuapp.com/v1/readings/'
```

---
## Notes

1- The client is responsible for generating `last_sync_date` and keeping it updated.

2- The server will only return new data that the client does not have (if the client generated a new data and synced it with the server, the server will not return this data to this client as it already has it)

3- I did not create the Shop model to keep the app simple, as the synchronization step can be shown and tested using the StockReading model only. 

4- I wrote lots of comments in the code just to make the task review easier (i don't write this amount of comments in daily work)

5- I did not document the endpoints using swagger as I don't have much time ( i only finished this in 5 hours)

----
## Scaling
To scale this endpoint we can

1. having more compute units behind a load balancer (horizontal scaling)

2. as this app is read-heavy , the database will be the bottleneck,  we can add more database replicas to handle the read operations.

3. instead of the polling method used in this endpoint we can use bi-directional communication (WebSockets) so the client won't hammer the server asking for updates (as the server will send newly updated records to the clients as soon as it happens)  ( the same technique used for synchronized online games between players)

4. instead of the half-baked solutions like this one, we can rely on proven technology to handle the synchronization steps  (What about CouchDB ??)

