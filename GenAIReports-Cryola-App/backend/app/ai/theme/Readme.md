# AI Theme Engine

This module provides an AI-powered pipeline for recoloring and theming display unit images. It utilizes Azure OpenAI (GPT-5 / GPT-Image-1) for generation and Semantic Kernel for evaluation and refinement.

## Project Structure

Ensure your files are organized as follows:

```text
backend/
└── app/
    └── Theme_AI/
        ├── __init__.py
        ├── config.py           # Configuration & Credentials
        ├── logger.py           # Context-aware logging
        ├── main.py             # Entry point (CLI)
        ├── models.py           # Pydantic data models
        ├── pipelines.py        # Core logic (Initial & Refinement flows)
        ├── prompts.py          # Centralized prompt templates
        ├── services.py         # OpenCV & GPT Rendering tools
        ├── storage.py          # Azure Blob & Local file handling
        └── requirements.txt    # Dependencies

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 Setup & Installation :

    1. Install Dependencies Navigate to your project root (where backend is located) and run:

        pip install -r backend/app/Theme_AI/requirements.txt


    2. Environment Variables The project relies on environment variables. You can set them in a .env file or export them in your terminal.
        -Required variables :
            AZURE_OPENAI_API_KEY="<your-key>"
            AZURE_OPENAI_ENDPOINT="https://<your-resource>[.openai.azure.com/]
            AZURE_STORAGE_ACCOUNT_NAME="<storage-account-name>"
            AZURE_STORAGE_ACCOUNT_KEY="<your-key>"
            AZURE_BLOB_CONTAINER="<blob - container>"


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


How to Run

    The main.py script automatically handles python path imports, so you can run it directly from your project root.

    1. Run Initial Generation
        -This phase takes a source image and applies a color theme (e.g., #B711A6).

            python backend/app/Theme_AI/main.py initial


    2. Run Refinement
        -This phase takes a specific generated image URL and applies natural language feedback (e.g., "Recolor the shelves black").

             Open backend/app/Theme_AI/main.py.

        -Update the chosen_url variable inside the test_refinement() function with a valid URL from the Initial step.

        -Run the command:

            python backend/app/Theme_AI/main.py refinement

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Logs

Logs are generated in a local logs/ folder and automatically uploaded to Azure Blob Storage upon completion.

    Log Format: Account_Structure_SubBrand_Season_Campaign.log

    Blob Path: cont-md-images/logs/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Troubleshooting

    ModuleNotFoundError: Ensure you are running the command using python path/to/main.py (e.g., from the root). The script includes logic to find the project root automatically.

    ImportError: attempted relative import...: Do not run pipelines.py or services.py directly. Always use main.py as the entry point.

    Unknown.log created: This happens if a logger is initialized before the context is set. The current codebase fixes this by initializing loggers lazily inside functions.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
