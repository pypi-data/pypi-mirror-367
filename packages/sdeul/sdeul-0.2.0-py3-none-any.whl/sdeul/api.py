"""REST API for Structural Data Extractor using LLMs.

This module provides a FastAPI-based REST API for sdeul, offering endpoints
for extracting structured JSON data from text and validating JSON files
against schemas.

Endpoints:
    POST /extract: Extract structured JSON data from text
    POST /validate: Validate JSON data against a JSON schema
"""

import logging
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate
from pydantic import BaseModel, Field

from .constants import (
    DEFAULT_CONTEXT_WINDOW,
    DEFAULT_F16_KV,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_TOKENS,
    DEFAULT_N_BATCH,
    DEFAULT_N_GPU_LAYERS,
    DEFAULT_N_THREADS,
    DEFAULT_REPEAT_LAST_N,
    DEFAULT_REPEAT_PENALTY,
    DEFAULT_SEED,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    DEFAULT_TOKEN_WISE_STREAMING,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DEFAULT_USE_MLOCK,
    DEFAULT_USE_MMAP,
)
from .extraction import extract_structured_data_from_text
from .llm import create_llm_instance
from .utility import configure_logging

app = FastAPI(
    title="SDEUL API",
    description="Structural Data Extractor using LLMs REST API",
    version="0.2.0",
)

configure_logging(debug=False, info=True)
logger = logging.getLogger(__name__)


class ExtractRequest(BaseModel):
    """Request model for the extract endpoint."""

    text: str = Field(..., description="Input text to extract data from")
    json_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema defining the output structure",
    )
    skip_validation: bool = Field(
        default=False,
        description="Skip JSON schema validation",
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Sampling temperature",
    )
    top_p: float = Field(
        default=DEFAULT_TOP_P,
        ge=0.0,
        le=1.0,
        description="Top-p sampling parameter",
    )
    top_k: int = Field(
        default=DEFAULT_TOP_K,
        ge=1,
        description="Top-k sampling parameter",
    )
    repeat_penalty: float = Field(
        default=DEFAULT_REPEAT_PENALTY,
        ge=1.0,
        description="Repeat penalty",
    )
    repeat_last_n: int = Field(
        default=DEFAULT_REPEAT_LAST_N,
        ge=0,
        description="Tokens to consider for repeat penalty",
    )
    n_ctx: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        ge=1,
        description="Context window size",
    )
    max_tokens: int = Field(
        default=DEFAULT_MAX_TOKENS,
        ge=1,
        description="Maximum tokens to generate",
    )
    seed: int = Field(
        default=DEFAULT_SEED,
        description="Random seed (-1 for random)",
    )
    n_batch: int = Field(
        default=DEFAULT_N_BATCH,
        ge=1,
        description="Batch size for processing",
    )
    n_threads: int = Field(
        default=DEFAULT_N_THREADS,
        description="Number of threads (-1 for auto)",
    )
    n_gpu_layers: int = Field(
        default=DEFAULT_N_GPU_LAYERS,
        description="GPU layers to use (-1 for auto)",
    )
    f16_kv: bool = Field(
        default=DEFAULT_F16_KV,
        description="Use half-precision for key/value cache",
    )
    use_mlock: bool = Field(
        default=DEFAULT_USE_MLOCK,
        description="Force model to stay in RAM",
    )
    use_mmap: bool = Field(
        default=DEFAULT_USE_MMAP,
        description="Use memory mapping for model",
    )
    token_wise_streaming: bool = Field(
        default=DEFAULT_TOKEN_WISE_STREAMING,
        description="Enable token-wise streaming",
    )
    timeout: int | None = Field(
        default=DEFAULT_TIMEOUT,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=DEFAULT_MAX_RETRIES,
        ge=0,
        description="Maximum number of retries",
    )

    # Model selection (exactly one should be provided)
    openai_model: str | None = Field(default=None, description="OpenAI model name")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_api_base: str | None = Field(default=None, description="OpenAI API base URL")
    openai_organization: str | None = Field(
        default=None,
        description="OpenAI organization ID",
    )

    google_model: str | None = Field(default=None, description="Google model name")
    google_api_key: str | None = Field(default=None, description="Google API key")

    anthropic_model: str | None = Field(
        default=None,
        description="Anthropic model name",
    )
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_api_base: str | None = Field(
        default=None,
        description="Anthropic API base URL",
    )

    groq_model: str | None = Field(default=None, description="Groq model name")
    groq_api_key: str | None = Field(default=None, description="Groq API key")

    bedrock_model: str | None = Field(default=None, description="AWS Bedrock model ID")
    aws_credentials_profile: str | None = Field(
        default=None,
        description="AWS credentials profile",
    )
    aws_region: str | None = Field(default=None, description="AWS region")
    bedrock_endpoint_url: str | None = Field(
        default=None,
        description="Bedrock endpoint URL",
    )

    ollama_model: str | None = Field(default=None, description="Ollama model name")
    ollama_base_url: str | None = Field(default=None, description="Ollama base URL")

    llamacpp_model_file: str | None = Field(
        default=None,
        description="Path to GGUF model file",
    )


class ExtractResponse(BaseModel):
    """Response model for the extract endpoint."""

    data: Any = Field(..., description="Extracted structured data")
    validated: bool = Field(
        ...,
        description="Whether the data was validated against the schema",
    )


class ValidateRequest(BaseModel):
    """Request model for the validate endpoint."""

    data: Any = Field(..., description="JSON data to validate")
    json_schema: dict[str, Any] = Field(
        ...,
        description="JSON Schema to validate against",
    )


class ValidateResponse(BaseModel):
    """Response model for the validate endpoint."""

    valid: bool = Field(..., description="Whether the data is valid")
    error: str | None = Field(
        default=None,
        description="Validation error message if invalid",
    )


@app.post("/extract")
async def extract_data(request: ExtractRequest) -> ExtractResponse:
    """Extract structured JSON data from text using LLMs.

    This endpoint takes input text and a JSON schema, then uses a Language
    Learning Model to extract structured data that conforms to the provided schema.

    Args:
        request (ExtractRequest): The extraction request containing text, schema,
            and model configuration.

    Returns:
        ExtractResponse: The extracted data and validation status.

    Raises:
        HTTPException: If extraction fails or no model is specified.
    """
    try:
        llm = create_llm_instance(
            ollama_model_name=request.ollama_model,
            ollama_base_url=request.ollama_base_url,
            llamacpp_model_file_path=request.llamacpp_model_file,
            groq_model_name=request.groq_model,
            groq_api_key=request.groq_api_key,
            bedrock_model_id=request.bedrock_model,
            google_model_name=request.google_model,
            google_api_key=request.google_api_key,
            anthropic_model_name=request.anthropic_model,
            anthropic_api_key=request.anthropic_api_key,
            anthropic_api_base=request.anthropic_api_base,
            openai_model_name=request.openai_model,
            openai_api_key=request.openai_api_key,
            openai_api_base=request.openai_api_base,
            openai_organization=request.openai_organization,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repeat_penalty=request.repeat_penalty,
            repeat_last_n=request.repeat_last_n,
            n_ctx=request.n_ctx,
            max_tokens=request.max_tokens,
            seed=request.seed,
            n_batch=request.n_batch,
            n_threads=request.n_threads,
            n_gpu_layers=request.n_gpu_layers,
            f16_kv=request.f16_kv,
            use_mlock=request.use_mlock,
            use_mmap=request.use_mmap,
            token_wise_streaming=request.token_wise_streaming,
            timeout=request.timeout,
            max_retries=request.max_retries,
            aws_credentials_profile_name=request.aws_credentials_profile,
            aws_region=request.aws_region,
            bedrock_endpoint_base_url=request.bedrock_endpoint_url,
        )
        extracted_data = extract_structured_data_from_text(
            input_text=request.text,
            schema=request.json_schema,
            llm=llm,
            skip_validation=request.skip_validation,
        )
        response = ExtractResponse(
            data=extracted_data,
            validated=not request.skip_validation,
        )
    except ValueError as e:
        logger.exception("Invalid request")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except JsonSchemaValidationError as e:
        logger.exception("Validation error")
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {e.message}",
        ) from e
    except Exception as e:
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e!s}") from e
    else:
        logger.info("Data extracted successfully")
        return response


@app.post("/validate")
async def validate_data(request: ValidateRequest) -> ValidateResponse:
    """Validate JSON data against a JSON Schema.

    Args:
        request (ValidateRequest): The validation request containing data
            and schema.

    Returns:
        ValidateResponse: The validation result.

    Raises:
        HTTPException: If validation encounters an unexpected error.
    """
    try:
        validate(instance=request.data, schema=request.json_schema)
        return ValidateResponse(valid=True, error=None)
    except JsonSchemaValidationError as e:
        return ValidateResponse(valid=False, error=e.message)
    except Exception as e:
        logger.exception("Validation error")
        raise HTTPException(status_code=500, detail=f"Validation error: {e!s}") from e


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict[str, str]: Health status.
    """
    return {"status": "healthy"}


def run_server(
    host: str = "0.0.0.0",  # noqa: S104
    port: int = 8000,
    reload: bool = True,
) -> None:
    """Run the FastAPI server using uvicorn.

    Args:
        host (str): The host to run the server on.
        port (int): The port to run the server on.
        reload (bool): Whether to enable auto-reload on code changes.
    """
    uvicorn.run(
        "sdeul.api:app",
        host=host,
        port=port,
        reload=reload,
    )
