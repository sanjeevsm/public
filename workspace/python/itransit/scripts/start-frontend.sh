#!/usr/bin/env bash
P=$(dirname "$0")
cd "$P/../frontend"
npm install
npm run dev -- --port 3002
