## CLI Commands

### Start BacklogMD
- backlog browser 

### Start Flutter App
First start simulator and then run the app (defaults to `API_BASE=http://localhost:8000`). One flutter run process only drives one device, so if you want to run the app on multiple simulators, you need to run multiple flutter run processes (in different terminals).

- open -a Simulator
- flutter run --dart-define=API_BASE=http://localhost:8000

- flutter pub get  
- flutter test                                            
- flutter analyze                                             


### Start FastAPI Server
- cd backend && source .venv/bin/activate 
- uvicorn app.main:app --reload -port 8001

- pytest
- ruff check .

## Everything at once (hot-reload dev mode)
- scripts/run-local-multiplayer.sh