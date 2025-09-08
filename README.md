## Mock user service

This service provides simple REST API to work with users within the system. It emulates the shifting of user profiles
(Every 5 minutes it creates from 1 to 7 new profiles and deletes from 1 to 3 old profiles randomly).

Default amount of users is 1000.

## Swagger: 
http://localhost:8000/docs