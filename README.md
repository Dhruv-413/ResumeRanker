# Job Recommendation System

The **Job Recommendation System** is a project designed to match candidates with job opportunities based on their resumes and job descriptions. It uses advanced natural language processing (NLP) techniques and machine learning models to evaluate resumes, compute similarity scores, and recommend the best candidates for a given job.

## Features

- **Resume Quality Evaluation**: Analyzes grammar, readability, and structure of resumes.
- **Experience Extraction**: Extracts skills and work experience details from resumes.
- **Location Matching**: Computes location compatibility between candidates and job locations.
- **Similarity Scoring**: Uses BERT embeddings to calculate the relevance of resumes to job descriptions.
- **Candidate Ranking**: Ranks candidates based on weighted scores for quality, experience, relevance, and location.

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL
- **NLP Libraries**: SpaCy, Transformers (BERT), TextStat
- **Geolocation**: Geopy, PyCountry
- **File Parsing**: PyMuPDF (PDF), python-docx (DOCX)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/job-recommendation-system.git
   cd job-recommendation-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   - Create a database named `job_recommendation`.
   - Update the `DATABASE_URL` in `backend/db.py` if necessary.

5. Run database migrations:
   ```bash
   python -m backend.db
   ```

6. Start the FastAPI server:
   ```bash
   uvicorn backend.main:app --reload
   ```

## API Endpoints

### 1. Create a Job
**POST** `/job`

Request Body:
```json
{
  "description": "Job description here",
  "location": "City, Country"
}
```

### 2. Upload a Resume
**POST** `/apply`

Form Data:
- `job_id`: ID of the job.
- `resume`: Resume file (PDF or DOCX).

### 3. Calculate Score
**GET** `/calculate_score/{resume_id}`

Calculates the total score for a resume based on quality, relevance, experience, and location.

### 4. View Resume
**GET** `/resumes/{resume_id}`

Downloads the resume file.

### 5. Recommend Candidates
**GET** `/recommend_candidate/{job_id}`

Recommends the best candidates for a specific job based on their total scores.

## Scoring Weights

The scoring system uses the following weights:
- **Quality**: 5%
- **Relevance**: 50%
- **Years of Experience**: 10%
- **Location**: 10%

## Folder Structure

```
Job Recommendation System/
├── backend/                # Backend logic
│   ├── db.py               # Database operations
│   ├── extract_text.py     # Resume text extraction
│   ├── main.py             # FastAPI application
│   ├── model.py            # Database models
│   ├── scoring.py          # Scoring and recommendation logic
├── migrations/             # SQL migrations
├── data/                   # Uploaded resumes
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .gitignore              # Git ignore file
```

## Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [SpaCy](https://spacy.io/)
- [TextStat](https://github.com/shivam5992/textstat)
- [Geopy](https://geopy.readthedocs.io/)
