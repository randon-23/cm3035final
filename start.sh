#!/bin/bash

# Start Nginx (media server) in the background
nginx

# Start Daphne (application) in the foreground
exec daphne -b 0.0.0.0 -p 8000 elearning.asgi:application