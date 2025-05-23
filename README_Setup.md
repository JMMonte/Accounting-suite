# Setup Guide

## Environment Configuration

This application requires private company and personal information, as well as authentication credentials, to be configured via environment variables for security reasons.

### Local Development Setup

1. **Copy the example environment file:**

   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file** with your actual information:

   ```
   # Company and Personal Information
   COMPANY_NAME=Your Actual Company Name
   COMPANY_NIPC=Your_Company_Tax_Number
   COMPANY_ADDRESS=Your Company Address, City, Country
   GESTOR_NAME=Your Full Name
   GESTOR_ADDRESS=Your Personal Address, City, Country
   GESTOR_NIFPS=Your_Personal_Tax_Number
   GESTOR_CATEGORIA=Gestor

   # Authentication Credentials
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_admin_password
   GESTOR_USERNAME=gestor
   GESTOR_PASSWORD=your_secure_gestor_password

   # Application Settings
   SESSION_TIMEOUT=3600
   ```

3. **Install dependencies:**

   ```bash
   uv sync
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

### Production/Cloud Deployment Setup

For deploying to cloud platforms (Streamlit Cloud, Heroku, etc.), set the following environment variables in your platform's configuration:

**Company & Personal Information:**

- `COMPANY_NAME`: Your company's legal name
- `COMPANY_NIPC`: Your company's tax identification number
- `COMPANY_ADDRESS`: Your company's official address
- `GESTOR_NAME`: The manager's full name
- `GESTOR_ADDRESS`: The manager's address
- `GESTOR_NIFPS`: The manager's personal tax number
- `GESTOR_CATEGORIA`: The manager's category (usually "Gestor")

**Authentication Credentials:**

- `ADMIN_USERNAME`: Administrator login username (default: "admin")
- `ADMIN_PASSWORD`: Secure password for administrator access
- `GESTOR_USERNAME`: Manager login username (default: "gestor")
- `GESTOR_PASSWORD`: Secure password for manager access

**Application Settings:**

- `SESSION_TIMEOUT`: Session timeout in seconds (default: 3600 = 1 hour)

### Security Notes

- **NEVER commit the `.env` file** to version control
- The `.env` file is already listed in `.gitignore`
- Use strong, unique passwords for authentication
- Default placeholder values are used if environment variables are not set
- All sensitive information is kept out of the source code

### Streamlit Cloud Deployment

1. Push your code to GitHub (without the `.env` file)
2. Connect your GitHub repository to Streamlit Cloud
3. In Streamlit Cloud settings, add each environment variable in the "Environment Variables" section
4. Deploy the app

**Note:** The `.streamlit/secrets.toml` file is no longer used. All configuration is now done via environment variables for better security and deployment flexibility.

The application will automatically use the environment variables for company, personal, and authentication information while keeping your data private.
