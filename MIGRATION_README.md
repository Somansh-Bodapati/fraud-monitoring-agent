# Migration to Java Spring Boot + Angular

This project has been migrated from Python/FastAPI + React to Java Spring Boot + Angular.

## Project Structure

```
fraud-monitoring-agent/
├── backend-java/          # Spring Boot backend
├── frontend-angular/      # Angular frontend
├── backend/               # Original Python backend (legacy)
└── frontend/              # Original React frontend (legacy)
```

## Backend (Spring Boot)

### Setup

1. **Prerequisites:**
   - Java 17+
   - Maven 3.8+

2. **Build and Run:**
   ```bash
   cd backend-java
   mvn clean install
   mvn spring-boot:run
   ```

3. **Configuration:**
   - Edit `src/main/resources/application.yml`
   - Set `OPENAI_API_KEY` environment variable or in application.yml

4. **Default Admin User:**
   - Email: `admin@example.com`
   - Password: `admin123`

### Features

- ✅ JWT Authentication
- ✅ RESTful API endpoints
- ✅ Multi-agent system (Classifier, Anomaly Detection, Decision, Notifier)
- ✅ H2 Database (can switch to PostgreSQL)
- ✅ Spring Security
- ✅ Async processing

## Frontend (Angular)

### Setup

1. **Prerequisites:**
   - Node.js 18+
   - Angular CLI: `npm install -g @angular/cli`

2. **Install Dependencies:**
   ```bash
   cd frontend-angular
   npm install
   ```

3. **Run Development Server:**
   ```bash
   ng serve
   ```
   Navigate to `http://localhost:4200`

### Features

- ✅ Angular 18
- ✅ Angular Material UI
- ✅ JWT Authentication
- ✅ Dashboard with statistics
- ✅ Transaction management with modal
- ✅ Alerts system
- ✅ Responsive design

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/{id}` - Get transaction

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Alerts
- `GET /api/alerts` - List alerts
- `PATCH /api/alerts/{id}/read` - Mark alert as read

## Migration Notes

### Key Changes

1. **Backend:**
   - Python → Java 17
   - FastAPI → Spring Boot 3.2
   - SQLAlchemy → JPA/Hibernate
   - Pydantic → Bean Validation
   - Python async → Spring @Async

2. **Frontend:**
   - React → Angular 18
   - React Router → Angular Router
   - React Query → Angular HTTP Client
   - Tailwind CSS → Angular Material

### Database

- Uses H2 in-memory database by default
- Can be switched to PostgreSQL by changing `application.yml`
- Database schema is auto-created on startup

### Agent System

The multi-agent system has been preserved:
- **ClassifierAgentService** - Classifies transactions
- **AnomalyAgentService** - Detects anomalies using Z-score
- **DecisionAgentService** - Makes risk decisions
- **NotifierAgentService** - Sends alerts
- **AgentOrchestratorService** - Coordinates agents

## Running Both Services

### Option 1: Manual

**Terminal 1 - Backend:**
```bash
cd backend-java
mvn spring-boot:run
```

**Terminal 2 - Frontend:**
```bash
cd frontend-angular
ng serve
```

### Option 2: Script (Coming Soon)

A startup script will be added to run both services together.

## Environment Variables

### Backend
- `OPENAI_API_KEY` - Your OpenAI API key
- `JWT_SECRET` - Secret key for JWT (min 256 bits)

### Frontend
- API URL is configured in services (default: `http://localhost:8000`)

## Next Steps

1. Complete remaining controllers (Alerts, Reports, Dashboard)
2. Add receipt upload functionality
3. Implement full OpenAI integration
4. Add more agent services (Parser, Reconciler, Reporter, Feedback)
5. Add unit and integration tests
6. Configure for production deployment

## License

MIT

