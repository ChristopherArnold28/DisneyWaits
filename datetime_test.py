from datetime import datetime
from pytz import timezone
tz = timezone('US/Eastern')
time = datetime.now(tz)

time.time
print(time.date())
print(time.time().isoformat(timespec = 'minutes'))
