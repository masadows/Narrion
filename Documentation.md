# Narrion RPG Master Assisstant

A tool designed to support Game Masters during RPG sessions. The application helps manage information about the game world, characters, and events, while also streamlining session organization and gameplay — both during preparation and throughout the session itself.

## Requirements

- Python **3.12**
- UV
- Make

## Installation steps

1. Clone repository
```bash
git clone https://github.com/masadows/Narrion.git
cd Narrion
```

2. Install dependencies
```bash
make requirements.txt
```

3. (Optional) Configure calendar

    1. Create your credentials to Google calendar API:
    [Google API docs]()
    2. Copy `credentials.json` file to `Narrion/data` location

3. Run app
```bash
make run
```

## Running tests
To run tests use command:
```bash
make test
```