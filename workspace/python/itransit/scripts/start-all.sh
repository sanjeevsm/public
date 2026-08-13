#!/usr/bin/env bash
P=$(dirname "$0")
cd "$P"
./start-backend.sh &
./start-frontend.sh &
