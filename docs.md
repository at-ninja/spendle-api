## New User

**POST** `/user`

### Request

```
{
	"phone":"+170828700004",
	"account_info":{
	    "first":"Jake",
	    "last":"Zarobsky",
	    "zip":"35401"
	}
}
```

### Response

```
{
	"auth_token":"guid",
	"message":null
	"status": 200
}
```

## Heartbeat/LocationUpdate

**POST** `/location`

### Request

```
{
	"auth_token":"guid",
	"lat":0.0,
	"lng":0.0,
}
```

### Response

```
{
	"message":null,
	"status":200
}
```

## AroundMe

**POST** `/aroundme`

### Request

```
{
	"auth_token":"guid",
	"lat":0.0,
	"lng":0.0,
	"limit":10
}
```

### Response

```
{
	"message":null,
	"status":200,
	"locations":[
		{
			"name":"Some name",
			"lat": 0.0,
			"lng": 0.0,
			"frequency":1,
			"spent":0.0
		},
		...
	]
}
```
