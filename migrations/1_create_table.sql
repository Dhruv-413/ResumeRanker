CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL
);
