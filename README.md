# 🚀 Adobe Hackathon Submission - Multilingual PDF Processor

## 📁 Project Structure

.
├── collection/
│ ├── challenge1b_input.json # Input JSON file
│ └── pdfs/
│ ├── doc1.pdf
│ ├── doc2.pdf
│ └── ...
├── main.py
├── tokenizer/
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
└── README.md # This file

## 🛠️ Setup Instructions

1. **Create the folder structure**:

   ```bash
   mkdir -p collection/pdfs
   ```

2. **Place your files**:

   ```Place your files:
   Put challenge1b_input.json in the collection/ folder

   Put all PDF documents in the collection/pdfs/ folder
   ```

🐳 Docker Commands

1. Build the Docker image:
   docker build -t adobe-part2-app .
2. Run the processor:
   docker run --rm -v $(pwd)/collection:/app/collection adobe-part2-app

📝 Notes

- The processor will:

  Read input from collection/challenge1b_input.json

  Process PDFs from collection/pdfs/

  Generate output in the same collection/ folder

- Ensure all PDFs referenced in the JSON are present in the pdfs/ folder

This README now:

1. Clearly shows the exact folder structure you requested
2. Provides simple Docker commands for building and running
3. Removes all unnecessary information about local installation
4. Keeps only the essential instructions for running with Docker
5. Maintains clean formatting and organization

The instructions assume the user already has:

- Docker installed
- The input JSON and PDFs ready to be placed in the specified folders
