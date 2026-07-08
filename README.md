# ComfyUI Structured Image Prompt

A small ComfyUI custom node for building strong image prompts from separate, structured fields:

- style
- camera angle
- lighting
- background
- characters
- action
- clothing
- assets
- quality tags
- negative prompt

The node is deterministic and does not require an LLM or external Python packages.

## Node

Display name:

```text
IC Structured Image Prompt
```

Category:

```text
IC/Prompting
```

Outputs:

- `prompt`
- `negative_prompt`
- `character_summary`
- `warnings`

## Inputs

The ComfyUI node uses english lower-case widget names and visible field prefixes
inside the default text values:

- `style`
- `camera angle`
- `lighting`
- `background`
- `characters`
- `action`
- `clothing`
- `assets`
- `quality tags`
- `negative prompt`
- `prompt format`
- `include labels`
- `check character refs`
- `show debug`

ComfyUI can hide multiline widget names in the expanded node body. To keep the
fields readable, new nodes start their text values with prefixes like
`style:`, `camera angle:`, `characters:`, and `negative prompt:`. These prefixes
are stripped automatically and will not appear in the generated prompt.

## Character References

Use a YAML-like character block:

```text
Mira: young rogue mage, short silver hair, confident expression
Oskar: old mechanic, heavy beard, tired eyes
```

You can then reference characters in action, clothing, and assets:

```text
action:
[Mira] watches the rooftops while [Oskar] repairs a small flying drone

clothing:
Mira: black tactical coat, blue scarf, leather boots
Oskar: worn orange work jacket, welding gloves

assets:
Mira: engraved wand, glowing wrist charm
Oskar: toolbox, brass repair drone
```

Unknown character references are reported through the `warnings` output when `strict_character_refs` is enabled.

## Installation

Clone this repository into your ComfyUI `custom_nodes` folder:

```powershell
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/YOUR-USER/comfyui-structured-image-prompt.git
```

Restart ComfyUI. The node will appear under `IC/Prompting`.

## Prompt Formats

The `prompt_format` input supports:

- `natural`
- `tagged`
- `cinematic`
- `sdxl`
- `flux`

`prompt_prefix` and `prompt_suffix` can be used for model-specific tokens, LoRA triggers, or house style tags.

## License

MIT
