# Shofa Podcast Website

A standalone website for the **Shofa Podcast — A Glance Between Worlds**, hosted by Tara AlSabban.

## Stack

- Pure HTML/CSS/JavaScript (no framework)
- Python `http.server` for static file serving on port 5000

## Project Structure

- `index.html` — The complete single-page website (all styles, scripts, and base64 assets embedded)
- `server.py` — Simple Python static file server on port 5000
- `shofa-standalone.html` — Original standalone HTML source file

## Running

The app is served via the "Start application" workflow which runs `python server.py`.

## Features

- Animated intro screen with logo and "Listen Now" CTA
- Fixed navigation (Gucci-style: left links / centered logo / right utility)
- Hero image grid with hover effects
- About section
- Episodes list
- Host profile
- Campaign/editorial section
- Platform links (Spotify, Apple, etc.)
- Newsletter signup
- Footer
- Scroll-reveal animations
- Film grain overlay effect
- Responsive design
