#!/usr/bin/env python3


from tokker import messages
from tokker.models.registry import ModelRegistry
from tokker.utils import get_installed_providers, get_install_commands


def run_list_models() -> None:
    """List available models, grouped by provider with curated messaging."""
    registry = ModelRegistry()

    # New template format output (always use template format)
    print(messages.SEP_MAIN)
    installed = get_installed_providers()

    # Provider sections in canonical order with dynamic headings
    provider_order = [
        ("OpenAI", None),
        ("Google", None),
        ("HuggingFace", None),
    ]

    for idx, (provider_name, install_cmd) in enumerate(provider_order):
        if provider_name in installed:
            heading = f"{provider_name} (installed)"
        else:
            # Resolve install command via mapping helper for consistency with messages
            cmds = get_install_commands([provider_name])
            install_cmd = cmds[0] if cmds else ""
            heading = f"{provider_name} (install with: {install_cmd})"
        print(heading + "\n")

        if provider_name == "OpenAI":
            # Curated descriptions for OpenAI encodings
            for model in registry.list_models("OpenAI"):
                name = model["name"]
                description = messages.OPENAI_DESCRIPTIONS.get(name)
                if description:
                    print(f"  {name:<22}{description}")
        elif provider_name == "Google":
            # List Google models and show auth guidance
            for model in registry.list_models("Google"):
                print(f"  {model['name']}")
            print(messages.MSG_AUTH_REQUIRED)
        else:
            # HuggingFace BYOM guidance and examples
            for line in messages.BYOM_INSTRUCTIONS:
                print(line)
            for example in messages.BYOM_EXAMPLE_MODELS:
                print(f"  {example}")

        # Separator between sections (but not after the last)
        if idx < len(provider_order) - 1:
            print(messages.SEP_SUB)

    print(messages.SEP_MAIN)
