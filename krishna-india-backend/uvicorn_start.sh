#!/bin/bash
exec uvicorn krishna_india.api:app --host 0.0.0.0 --port 8001 --reload
