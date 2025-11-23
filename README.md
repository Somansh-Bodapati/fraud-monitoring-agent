# Fraud Monitoring Agent - Quick Start

## Prerequisites
- JDK 17 installed via Homebrew: `/opt/homebrew/opt/openjdk@17`
- Node.js and npm
- Maven

## Starting the Application

### Terminal 1: Backend
```bash
./start-backend.sh
```
Wait for: `Started FraudMonitoringApplication`

### Terminal 2: Frontend  
```bash
./start-frontend.sh
```

## Access
- **Frontend**: http://localhost:4200
- **Backend**: http://localhost:8000
- **Swagger**: http://localhost:8000/swagger-ui.html
- **H2 Console**: http://localhost:8000/h2-console

## Login Credentials
- **Admin**: `admin@example.com` / `admin123`
- **User**: `user@example.com` / `user123`

## Troubleshooting

### Login Issues
1. Check browser console (F12) for errors
2. Verify backend is running: `curl http://localhost:8000/actuator/health`
3. Clear browser cache and localStorage
4. Test login via curl:
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"admin123"}'
   ```

### Backend Won't Start
- Port 8000 in use: `lsof -ti :8000 | xargs kill -9`
- Database locked: Stop all Java processes and restart

### Frontend Issues
- `npm install` if node_modules missing
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
