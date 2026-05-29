# Image Search

## The Problem

Over a decade of being a Dad, when they were born, I snapped it. If they moved, slept, ate, or just happened to be in my eye line - I took a picture. Google Photos storage hasn't kept up so more than 100,000 photos are going local but I still want to be able to find the photo of them on their 3rd birthday, or sat in the red car, or the day we visited a castle.

## What's it do?

Replaces how I've used Google Photos search feature all these years. Search terms can include a thing (castle, red car), place (I'll have to retrieve the decimal lat/long coords), date (2026, 2026 May, 2026 May 29

## Tech Stack

- Docker: containing Nginx, Redis, PostgreSQL, and the app - for portability.
- The app: Python, indexes the photos via Google Vision API, stores results in PostgreSQL.
- Nginx: serves web front end.
- Redis: caches previous search results.
- PostgreSQL: stores Google Vision API tags.

## Architecture

User search -> Nginx -> Python FastAPI (Jinja2 html templating/processing) -> Redis -> PostgreSQL

Manual indexing -> Python -> Vision API -> PostgreSQL

## Running it

See setup docs

## Searching

Interpreted search terms:
- 'Things': castle, red car, elephant, sunset
- Date: With increasing granularity - Year, or Year and Month, or Year and Month and Day
- Location: lat,long (eg 54.0025,-0.1103), shows results within 5 miles **Location search requires decimal coords, place names are out of scope for V1**

Once results are returned, these can be sorted.

## Design Decisions

### Tiny VPS

Initial build is for my GitHub portfolio, which is supported by a tiny VPS, so...
- indexing of new images is triggered manually (the most process-heavy task)
- memory limits of Docker containers not set as there are few resources available to start with

### Authentication

For portfolio purposes the sample set of images have been chosen to exclude any private images so no authentication is required. If my live version of this image search is ever made available on the internet it will be behind basic auth through Nginx.

## Status

In Development.
