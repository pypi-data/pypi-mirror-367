"""Command Line Interface for Structural Data Extractor using LLMs.

This module provides the main CLI application for sdeul, including commands
for extracting structured JSON data from text and validating JSON files
against schemas. It supports multiple LLM providers and various configuration
options.

Commands:
    extract: Extract structured JSON data from text files
    validate: Validate JSON files against JSON schemas
    serve: Run the FastAPI server for the REST API

Functions:
    main: Main CLI callback function
    extract: CLI command for data extraction
    validate: CLI command for JSON validation
    serve: CLI command for running the API server
    _version_callback: Callback for version option
"""

import typer
from rich import print

from . import __version__
from .api import run_server
from .constants import (
    DEFAULT_API_HOST,
    DEFAULT_API_PORT,
    DEFAULT_API_RELOAD,
    DEFAULT_CONTEXT_WINDOW,
    DEFAULT_MAX_TOKENS,
    DEFAULT_N_BATCH,
    DEFAULT_N_GPU_LAYERS,
    DEFAULT_N_THREADS,
    DEFAULT_REPEAT_LAST_N,
    DEFAULT_REPEAT_PENALTY,
    DEFAULT_SEED,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
)
from .extraction import extract_json_from_text_file
from .utility import configure_logging
from .validation import validate_json_files_using_json_schema

app = typer.Typer()


def _version_callback(value: bool) -> None:
    """Callback function for the --version option.

    Args:
        value (bool): Whether the version option was provided.

    Raises:
        typer.Exit: Always exits after printing version if value is True.
    """
    if value:
        print(__version__)
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version information and exit.",
    ),
) -> None:
    """Structural Data Extractor using Language Learning Models.

    sdeul is a command-line tool for extracting structured JSON data from
    unstructured text using various Language Learning Models including
    OpenAI, Google, Groq, Amazon Bedrock, Ollama, and local models.

    Args:
        version (bool): Show version information and exit.
    """


@app.command()
def extract(
    json_schema_file: str = typer.Argument(..., help="JSON Schema file path."),
    text_file: str = typer.Argument(..., help="Input text file path."),
    output_json_file: str | None = typer.Option(
        default=None,
        help="Output JSON file path.",
    ),
    compact_json: bool = typer.Option(
        default=False,
        help="Compact instead of pretty-printed output.",
    ),
    skip_validation: bool = typer.Option(
        default=False,
        help="Skip output validation using JSON Schema.",
    ),
    temperature: float = typer.Option(
        default=DEFAULT_TEMPERATURE,
        help="Set the temperature for sampling.",
    ),
    top_p: float = typer.Option(
        default=DEFAULT_TOP_P,
        help="Set the top-p value for sampling.",
    ),
    top_k: int = typer.Option(
        default=DEFAULT_TOP_K,
        help="Set the top-k value for sampling.",
    ),
    repeat_penalty: float = typer.Option(
        default=DEFAULT_REPEAT_PENALTY,
        help="Set the penalty to apply to repeated tokens.",
    ),
    repeat_last_n: int = typer.Option(
        default=DEFAULT_REPEAT_LAST_N,
        help="Set the number of tokens to look back when applying the repeat penalty.",
    ),
    n_ctx: int = typer.Option(
        default=DEFAULT_CONTEXT_WINDOW,
        help="Set the token context window.",
    ),
    max_tokens: int = typer.Option(
        default=DEFAULT_MAX_TOKENS,
        help="Set the max tokens to generate.",
    ),
    seed: int = typer.Option(
        default=DEFAULT_SEED,
        help="Set the random seed.",
    ),
    n_batch: int = typer.Option(
        default=DEFAULT_N_BATCH,
        help="Set the number of batch tokens.",
    ),
    n_threads: int = typer.Option(
        default=DEFAULT_N_THREADS,
        help="Set the number of threads to use.",
    ),
    n_gpu_layers: int = typer.Option(
        default=DEFAULT_N_GPU_LAYERS,
        help="Set the number of GPU layers.",
    ),
    openai_model: str | None = typer.Option(
        default=None,
        envvar="OPENAI_MODEL",
        help="Use the OpenAI model.",
    ),
    google_model: str | None = typer.Option(
        default=None,
        envvar="GOOGLE_MODEL",
        help="Use the Google Generative AI model.",
    ),
    anthropic_model: str | None = typer.Option(
        default=None,
        envvar="ANTHROPIC_MODEL",
        help="Use the Anthropic model.",
    ),
    groq_model: str | None = typer.Option(
        default=None,
        envvar="GROQ_MODEL",
        help="Use the Groq model.",
    ),
    bedrock_model: str | None = typer.Option(
        default=None,
        envvar="BEDROCK_MODEL",
        help="Use the Amazon Bedrock model.",
    ),
    ollama_model: str | None = typer.Option(
        default=None,
        envvar="OLLAMA_MODEL",
        help="Use the Ollama model.",
    ),
    ollama_base_url: str | None = typer.Option(
        default=None,
        envvar="OLLAMA_BASE_URL",
        help="Override the Ollama base URL.",
    ),
    llamacpp_model_file: str | None = typer.Option(
        default=None,
        envvar="LLAMACPP_MODEL_FILE",
        help="Use the model GGUF file for llama.cpp.",
    ),
    openai_api_key: str | None = typer.Option(
        default=None,
        envvar="OPENAI_API_KEY",
        help="Override the OpenAI API key.",
    ),
    openai_api_base: str | None = typer.Option(
        default=None,
        envvar="OPENAI_API_BASE",
        help="Override the OpenAI API base URL.",
    ),
    openai_organization: str | None = typer.Option(
        default=None,
        envvar="OPENAI_ORGANIZATION",
        help="Override the OpenAI organization ID.",
    ),
    google_api_key: str | None = typer.Option(
        default=None,
        envvar="GOOGLE_API_KEY",
        help="Override the Google API key.",
    ),
    anthropic_api_key: str | None = typer.Option(
        default=None,
        envvar="ANTHROPIC_API_KEY",
        help="Override the Anthropic API key.",
    ),
    anthropic_api_base: str | None = typer.Option(
        default=None,
        envvar="ANTHROPIC_API_BASE",
        help="Override the Anthropic API base URL.",
    ),
    groq_api_key: str | None = typer.Option(
        default=None,
        envvar="GROQ_API_KEY",
        help="Override the Groq API key.",
    ),
    aws_credentials_profile: str | None = typer.Option(
        default=None,
        envvar="AWS_PROFILE",
        help="Set the AWS credentials profile name for Amazon Bedrock.",
    ),
    debug: bool = typer.Option(default=False, help="Execute with debug messages."),
    info: bool = typer.Option(default=False, help="Execute with info messages."),
) -> None:
    """Extract structured JSON data from text using Language Learning Models.

    This command takes an input text file and a JSON schema, then uses a
    selected Language Learning Model to extract structured data that conforms
    to the provided schema. The output can be saved to a file or printed to
    stdout.

    Args:
        json_schema_file (str): Path to the JSON schema file that defines the
            structure of the expected output.
        text_file (str): Path to the input text file containing unstructured data.
        output_json_file (str | None): Optional path to save the extracted JSON
            output. If not provided, output is printed to stdout.
        compact_json (bool): Output JSON in compact format instead of
            pretty-printed.
        skip_validation (bool): Skip validation of the extracted data against
            the schema.
        temperature (float): Controls randomness in the model's output (0.0-2.0).
        top_p (float): Controls diversity via nucleus sampling (0.0-1.0).
        top_k (int): Controls diversity by limiting token choices.
        repeat_penalty (float): Penalty for repeating tokens (1.0 = no penalty).
        repeat_last_n (int): Number of tokens to consider for repeat penalty.
        n_ctx (int): Size of the token context window.
        max_tokens (int): Maximum number of tokens to generate.
        seed (int): Random seed for reproducible output (-1 for random).
        n_batch (int): Number of tokens to process in parallel (llama.cpp only).
        n_threads (int): Number of CPU threads to use (llama.cpp only).
        n_gpu_layers (int): Number of layers to offload to GPU (llama.cpp only).
        openai_model (str | None): OpenAI model to use.
        google_model (str | None): Google model to use.
        anthropic_model (str | None): Anthropic model to use.
        groq_model (str | None): Groq model to use.
        bedrock_model (str | None): Amazon Bedrock model ID to use.
        ollama_model (str | None): Ollama model to use.
        ollama_base_url (str | None): Custom Ollama API base URL.
        llamacpp_model_file (str | None): Path to local GGUF model file for
            llama.cpp.
        openai_api_key (str | None): OpenAI API key (overrides environment
            variable).
        openai_api_base (str | None): Custom OpenAI API base URL.
        openai_organization (str | None): OpenAI organization ID.
        google_api_key (str | None): Google API key (overrides environment
            variable).
        anthropic_api_key (str | None): Anthropic API key (overrides environment
            variable).
        anthropic_api_base (str | None): Custom Anthropic API base URL.
        groq_api_key (str | None): Groq API key (overrides environment variable).
        aws_credentials_profile (str | None): AWS profile name for Bedrock access.
        debug (bool): Enable debug logging level.
        info (bool): Enable info logging level.
    """
    configure_logging(debug=debug, info=info)
    extract_json_from_text_file(
        json_schema_file_path=json_schema_file,
        text_file_path=text_file,
        output_json_file_path=output_json_file,
        compact_json=compact_json,
        skip_validation=skip_validation,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repeat_penalty=repeat_penalty,
        repeat_last_n=repeat_last_n,
        n_ctx=n_ctx,
        max_tokens=max_tokens,
        seed=seed,
        n_batch=n_batch,
        n_threads=n_threads,
        n_gpu_layers=n_gpu_layers,
        openai_model_name=openai_model,
        google_model_name=google_model,
        anthropic_model_name=anthropic_model,
        groq_model_name=groq_model,
        bedrock_model_id=bedrock_model,
        ollama_model_name=ollama_model,
        llamacpp_model_file_path=llamacpp_model_file,
        openai_api_key=openai_api_key,
        openai_api_base=openai_api_base,
        openai_organization=openai_organization,
        google_api_key=google_api_key,
        anthropic_api_key=anthropic_api_key,
        anthropic_api_base=anthropic_api_base,
        groq_api_key=groq_api_key,
        ollama_base_url=ollama_base_url,
        aws_credentials_profile_name=aws_credentials_profile,
    )


@app.command()
def validate(
    json_schema_file: str = typer.Argument(..., help="JSON Schema file path."),
    json_files: list[str] = typer.Argument(..., help="JSON file paths."),
    debug: bool = typer.Option(default=False, help="Set DEBUG log level."),
    info: bool = typer.Option(default=False, help="Set INFO log level."),
) -> None:
    """Validate JSON files against a JSON Schema.

    This command validates one or more JSON files against a provided JSON schema.
    It reports validation results for each file and exits with a non-zero status
    code if any files are invalid.

    Args:
        json_schema_file (str): Path to the JSON schema file used for validation.
        json_files (list[str]): List of paths to JSON files to validate.
        debug (bool): Enable debug logging level.
        info (bool): Enable info logging level.

    Exit Codes:
        0: All files are valid
        N: N files failed validation (where N > 0)
    """
    configure_logging(debug=debug, info=info)
    validate_json_files_using_json_schema(
        json_schema_file_path=json_schema_file,
        json_file_paths=json_files,
    )


@app.command()
def serve(
    host: str = typer.Option(
        default=DEFAULT_API_HOST,
        help="Host to run the server on.",
    ),
    port: int = typer.Option(
        default=DEFAULT_API_PORT,
        help="Port to run the server on.",
    ),
    reload: bool = typer.Option(
        default=DEFAULT_API_RELOAD,
        help="Enable auto-reload on code changes.",
    ),
    debug: bool = typer.Option(default=False, help="Set DEBUG log level."),
    info: bool = typer.Option(default=False, help="Set INFO log level."),
) -> None:
    """Run the FastAPI server for the SDEUL REST API.

    This command starts a FastAPI server that provides REST API endpoints
    for extracting structured JSON data from text and validating JSON data
    against schemas.

    Args:
        host (str): The host IP address to bind the server to.
        port (int): The port number to run the server on.
        reload (bool): Enable automatic reloading when code changes are detected.
        debug (bool): Enable debug logging level.
        info (bool): Enable info logging level.
    """
    configure_logging(debug=debug, info=info)
    run_server(host=host, port=port, reload=reload)
