# cuaca aka the Malaysian Weather Service API Wrapper

To use the API first please register the API at https://api.met.gov.my/

example usage

```python
import cuaca

api = cuaca.WeatherAPI("API_KEY")

locations = api.locations("STATE")
states = api.states()
state = api.state("selangor")

forecast = api.forecast("LOCATION:15", "2017-08-12", "2017-08-13")
```
