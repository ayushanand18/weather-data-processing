# Backend Service

Since this is a data-intensive application, I thought of creating a server based 
utility. This is mostly going to be a mostly-API service, with a swagger editor
so you can preview it before building a UI to integrate with it.


## Database Design
Tables
+ `realtime_weather`

column | datatype | constraint
-------|----------|-----------
dt     | timestamp| UNIQUE, NOT NULL
rain   | number   | NOT NULL
snow   | number   | NOT NULL
clear  | number   | NOT NULL
temp   | decimal  | NOT NULL
feels_like | decimal | NOT NULL

+ `daily_weather`

column | datatype | constraint
-------|----------|-----------
date   | date     | PRIMARY KEY
avg_temp | number | NOT NULL
max_temp | number | NOT NULL
min_temp | number | NOT NULL
dom_condition |str| NOT NULL

+ `alert_events`

column | datatype | constraint
-------|----------|-----------
event_id| UUID    | PRIMARY KEY
dt     | timestamp| UNIQUE, NOT NULL
user_id| UUID     | NOT NULL, FOREIGN KEY users(user_id)
reason | str      | NOT NULL
alert_id| UUID    | NOT NULL, FOREIGN KEY user_alerts(alert_id)

+ `users`

column | datatype | constraint
-------|----------|-----------
user_id| UUID     | PRIMARY KEY
name   | str      | NOT NULL
email  | str      | NOT NULL

+ `user_alerts`

column | datatype | constraint
-------|----------|-----------
alert_id| UUID    | PRIMARY KEY
user_id| UUID     | NOT NULL, FOREIGN KEY users(user_id)
field  | str      | NOT NULL
threshold | number| NOT NULL
disabled | boolean| NOT NULL, DEFAULT true

