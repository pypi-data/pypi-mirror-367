#!/usr/bin/env python3
"""
Script to generate model configuration files for HELM.
Generates model_deployments.yaml and model_metadata.yaml based on CLI parameters.
"""

import argparse
import yaml
import os
from datetime import datetime, date
from pathlib import Path


def generate_model_metadata(model_name: str) -> dict:
    """Generate model metadata configuration."""
    return {
        "models": [
            {
                "name": model_name,
                "display_name": f"{model_name.split('/')[-1]} (Generated)",
                "description": f"Auto-generated model configuration for {model_name}. This is a placeholder description.",
                "creator_organization_name": "Generated",
                "access": "open",
                "num_parameters": 1000000000,  # 1B parameters as dummy value
                "release_date": date.today(),
                "tags": ["TEXT_MODEL_TAG", "PARTIAL_FUNCTIONALITY_TEXT_MODEL_TAG"]
            }
        ]
    }


def generate_model_deployments(model_name: str, base_url: str, openai_model_name: str) -> dict:
    """Generate model deployments configuration."""
    return {
        "model_deployments": [
            {
                "name": model_name,
                "model_name": model_name,
                "tokenizer_name": "simple/tokenizer1",
                "max_sequence_length": 128000,
                "max_request_length": 128001,
                "client_spec": {
                    "class_name": "helm.clients.openai_client.OpenAIClient",
                    "args": {
                        "base_url": base_url,
                        "openai_model_name": openai_model_name
                    }
                }
            }
        ]
    }


def write_yaml_file(data: dict, filepath: str):
    """Write data to YAML file with proper formatting."""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate model configuration files for HELM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_dynamic_model_configs.py \\
    --model-name "myorg/mymodel" \\
    --base-url "https://api.myorg.com/v1" \\
    --openai-model-name "myorg/mymodel" \\
    --output-dir "./generated-configs"
        """
    )
    
    parser.add_argument(
        "--model-name",
        required=True,
        help="Model name (e.g., 'myorg/mymodel')"
    )
    
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL for the API endpoint"
    )
    
    parser.add_argument(
        "--openai-model-name",
        required=True,
        help="OpenAI model name for the client"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./generated-configs",
        help="Output directory for generated files (default: ./generated-configs)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_metadata = generate_model_metadata(args.model_name)
    model_deployments = generate_model_deployments(
        args.model_name, 
        args.base_url, 
        args.openai_model_name
    )
    
    metadata_path = output_dir / "model_metadata.yaml"
    deployments_path = output_dir / "model_deployments.yaml"
    
    write_yaml_file(model_metadata, metadata_path)
    write_yaml_file(model_deployments, deployments_path)
    
    print(f"✅ Generated configuration files:")
    print(f"   📄 {metadata_path}")
    print(f"   📄 {deployments_path}")
    print(f"\n📋 Configuration summary:")
    print(f"   Model name: {args.model_name}")
    print(f"   Base URL: {args.base_url}")
    print(f"   OpenAI model name: {args.openai_model_name}")


if __name__ == "__main__":
    main()
