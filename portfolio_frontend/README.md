# Riley Benjamin Chapman Portfolio

## Project Overview
Photo portfolio project to showcase my skills as a full stack developer and to get some hands on experience working with python

## Technologies
- **Backend**: Django 5.1.4
- **Frontend**: Vue 3 + TypeScript
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Database**: SQLite (Development)

## Features
- Responsive photo portfolio display
- Campaigns showcase
- Dynamic photo carousels
- Detailed photographer attribution

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip
- npm

### Backend Setup
1. Clone the repository
2. Create a virtual environment
    ```
    python -m venv venv
    source venv/bin/activate 
    ```
3. Install Python dependencies
    ```
    pip install -r requirements.txt
    ```
4. Set up environment variables
    ```
    cp .env.example .env
    ```
    Update with your configuration
5. Run migrations
    ```
    python manage.py migrate
    ```
6. Start Django development server
    ```
    python manage.py runserver
    ```

### Frontend Setup
1. Navigate to frontend directory
2. Install npm dependencies
    ```
    npm install
    ```
3. Start Vue development server
    ```
    npm run dev
    ```

## Environment Configuration
Refer to `.env.example` for required environment variables

## Deployment
(Future documentation)

## Status
🚧 Work in Progress 🚧