# Strava Analysis

Strava Analysis is a Python-based tool designed to analyze your running workouts using Strava's API. It provides detailed insights into your activities, including streams, weekly reports, and more.

## Features

- **Activity Streams**: Fetch and process detailed activity streams such as time, distance, and heart rate.
- **Weekly Reports**: Generate reports for the current and previous weeks.
- **Activity Details**: Retrieve detailed information about specific activities.
- **Database Integration**: Store and manage data using Supabase.
- **Token Management**: Securely handle access tokens with encryption.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/AlexAlgarate/strava_analisys.git
   cd strava_analisys
   ```

2. Set up the environment using `uv`:

   ```bash
   uv init
   ```

3. Install the dependencies specified in the `pyproject.toml` file:

   ```bash
   uv add [PACKAGES] (e.g., `ruff>=0.11.7`)
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following variables:

   ```env
   STRAVA_CLIENT_ID=<your_client_id>
   STRAVA_SECRET_KEY=<your_secret_key>
   SUPABASE_URL=<your_supabase_url>
   SUPABASE_API_KEY=<your_supabase_api_key>
   FERNET_KEY=<your_fernet_key>
   ```

## Usage

1. Run the main script:

   ```bash
   uv run main.py 
   ```

2. Follow the on-screen instructions to interact with the menu and analyze your Strava activities.

## Testing

Run the test suite using pytest:

```bash
uv run pytest tests/ -vv
```

## Project Structure

```text
strava_analisys/
├── src/
│   ├── activities/          # Activity fetchers
│   ├── database/            # Database integration
│   ├── interfaces/          # Abstract interfaces
│   ├── menu/                # Menu and user interaction
│   ├── strava_api/          # Strava API integration
│   ├── utils/               # Utility functions
│   ├── access_token.py      # Token management
│   ├── credentials.py       # Environment variable handling
│   ├── encryptor.py         # Data encryption
│   ├── oauth_code.py        # OAuth code retrieval
│   ├── strava_service.py    # Service layer
│   ├── token_handler.py     # Token handling logic
│   ├── token_manager.py     # Token management
├── tests/                   # Test suite
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Strava API](https://developers.strava.com/) for providing the data.
- [Supabase](https://supabase.com/) for database integration.
- [Fernet Encryption](https://cryptography.io/en/latest/fernet/) for secure data handling.
