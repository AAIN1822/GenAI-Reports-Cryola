# Graphics Automation Module

This module automates the generation and compositing of graphics onto retail display units using Azure OpenAI (`gpt-1.5` for vision and `o3` for reasoning).

## Directory Structure

- **`config.py`**: Configuration management. Handles Azure credentials, model names, and region specifications.
- **`logger.py`**: Structured logging implementation (file and console) with context tracking (project, account, etc.).
- **`main.py`**: Command-line entry point for running the pipeline locally or via script.
- **`pipelines.py`**: Orchestrates the high-level workflow: Download Assets -> Annotate -> Generate Prompt -> Render -> Critique & Refine.
- **`services.py`**: Core business logic and AI agent interactions (Annotation Agent, Prompt Agent, Rendering Client, Critic Agent).
- **`storage.py`**: `BlobManager` class for abstracting I/O. Supports Azure Blob Storage with a local filesystem fallback for testing.
- **`prompts.py`**: Central repository for all system prompts used by the AI agents.
- **`utils.py`**: Helper functions for image usage encoding (Base64/Data URI) and file handling.

## specific Configuration

This module relies on environment variables or a `.env` file in the project root.

```ini
AZURE_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_API_KEY="your-api-key"
AZURE_API_VERSION="2025-04-01-preview"

# Storage
AZURE_STORAGE_ACCOUNT_NAME="yourstorageaccount"
AZURE_STORAGE_ACCOUNT_KEY="yourstoragekey"
AZURE_BLOB_CONTAINER_NAME="your-container-name"
```

## Usage

To run the pipeline from the `backend` directory:

```bash
# Run as a module to resolve imports correctly
python -m app.ai.graphics.main initial
python -m app.ai.graphics.main refinement
```

You can modify `main.py` to change the input image URLs (Base Shelf, Header, etc.) for testing different scenarios.

## Pipeline Workflow

### Initial Generation Phase

1.  **Asset Retrieval**: Downloads the base display image and any existing graphics (Header, Lip, Side Panel) from Azure Blob Storage.
2.  **Annotation**: The `AnnotationAgent` analyzes the base shelf image and existing assets to generate a JSON map of spatial regions and perspective usage.
3.  **Prompt Generation**: The `PrompterAgent` converts the annotation JSON into a detailed text prompt for the image generation model.
4.  **rendering**: The image model (`gpt-1.5`) renders 3 initial variants based on the prompt.
5.  **Critique Loop**:
    *   The `CriticAgent` (`o3`) evaluates each variant against the original requirements (Placement, Integrity, Aesthetics).
    *   If the score is below the threshold, the critic provides specific recommendations.
    *   The prompt is refined, and new variants are generated.
    *   This repeats until a threshold is met or `MAX_RETRY` is reached.
6.  **Output**: The best-scoring images are returned (URLs to blob storage or local paths).

### User Refinement Phase

The refinement pipeline allows users to request specific changes to a generated output (e.g., "Add a logo to the header", "Fix the color of the rail").

1.  **Input**: Accepts User Feedback, Original Base Image, Current Generated Output, and Graphic Assets.
2.  **Orchestration**: The `OrchestratorAgent` analyzes the feedback and images to create a `RefinementPlan`. This includes:
    *   `edit_prompt`: A specific instruction for the image model.
    *   `image_inputs`: Which images are needed for context (Base, Output, Assets).
3.  **Semantic Mapping**: The `ImagePromptMapper` ensures intelligent selection of input images by mapping semantic keywords (e.g., "header", "side", "lip") in the feedback to the correct file assets.
4.  **Rendering**: Generates **3 variants** of the refined image.
5.  **Evaluation**: The `RefinementEvaluator` scores all variants on how well they addressed the feedback while maintaining image integrity.
6.  **Selection**: The best variant is selected. If the score meets the `GRAPHIC_REFINEMENT_THRESHOLD`, it is returned. Otherwise, it acts as the input for the next refinement attempt.

## Dependencies

- `openai`
- `semantic-kernel`
- `azure-storage-blob`
- `pydantic-settings`
