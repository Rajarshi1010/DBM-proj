from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, faculty, books, conferences, journals, admin, upload

app = FastAPI(title="Department API")

# --- CORS (Crucial for React Frontend) ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(faculty.router, prefix="/faculty", tags=["Faculty"])
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(conferences.router, prefix="/conferences", tags=["Conferences"])
app.include_router(journals.router, prefix="/journals", tags=["Journals"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(upload.router, prefix="/upload", tags=["Bulk Upload"])
@app.get("/")
def root():
    return {"message": "API is running"}