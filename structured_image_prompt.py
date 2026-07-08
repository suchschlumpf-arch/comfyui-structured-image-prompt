import re


DEFAULT_NEGATIVE_PROMPT = (
    "low quality, blurry, distorted anatomy, extra fingers, missing fingers, "
    "bad hands, deformed face, duplicate subject, unreadable text, watermark"
)


INPUT_KEYS = {
    "style": "01 Bildstil",
    "camera_angle": "02 Bildwinkel / Kamera",
    "lighting": "03 Beleuchtung",
    "background": "04 Hintergrund",
    "characters": "05 Charaktere",
    "action": "06 Handlung",
    "clothing": "07 Kleidung",
    "assets": "08 Assets / Requisiten",
    "quality_tags": "09 Qualitaets-Tags",
    "negative_prompt": "10 Negativer Prompt",
    "prompt_format": "11 Prompt-Format",
    "include_labels": "12 Abschnittsueberschriften im Prompt",
    "strict_character_refs": "13 Charakter-Referenzen pruefen",
    "show_debug": "14 Prompt in der Node anzeigen",
    "prompt_prefix": "Optional: Prompt-Prefix",
    "prompt_suffix": "Optional: Prompt-Suffix",
}


class ICStructuredImagePrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                INPUT_KEYS["style"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "cinematic fantasy realism, detailed materials, coherent composition",
                    },
                ),
                INPUT_KEYS["camera_angle"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "medium full shot, slight low angle, 35mm lens perspective",
                    },
                ),
                INPUT_KEYS["lighting"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "soft rim light, warm key light, atmospheric depth",
                    },
                ),
                INPUT_KEYS["background"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "ancient city street after rain, distant lanterns, subtle mist",
                    },
                ),
                INPUT_KEYS["characters"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "Mira: young rogue mage, short silver hair, confident expression\n"
                            "Oskar: old mechanic, heavy beard, tired eyes"
                        ),
                    },
                ),
                INPUT_KEYS["action"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "Mira watches the rooftops while Oskar repairs a small flying drone beside her",
                    },
                ),
                INPUT_KEYS["clothing"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "Mira: black tactical coat, blue scarf, leather boots\n"
                            "Oskar: worn orange work jacket, welding gloves"
                        ),
                    },
                ),
                INPUT_KEYS["assets"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "Mira: engraved wand, glowing wrist charm\n"
                            "Oskar: toolbox, brass repair drone"
                        ),
                    },
                ),
                INPUT_KEYS["quality_tags"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "high quality, sharp focus, rich texture detail, natural color harmony",
                    },
                ),
                INPUT_KEYS["negative_prompt"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": DEFAULT_NEGATIVE_PROMPT,
                    },
                ),
                INPUT_KEYS["prompt_format"]: (
                    ["natural", "tagged", "cinematic", "sdxl", "flux"],
                    {"default": "natural"},
                ),
                INPUT_KEYS["include_labels"]: ("BOOLEAN", {"default": False}),
                INPUT_KEYS["strict_character_refs"]: ("BOOLEAN", {"default": True}),
                INPUT_KEYS["show_debug"]: ("BOOLEAN", {"default": True}),
            },
            "optional": {
                INPUT_KEYS["prompt_prefix"]: ("STRING", {"multiline": True, "default": ""}),
                INPUT_KEYS["prompt_suffix"]: ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative_prompt", "character_summary", "warnings")
    FUNCTION = "build_prompt"
    CATEGORY = "IC/Prompting"

    def build_prompt(self, **kwargs):
        style = self._input(kwargs, "style")
        camera_angle = self._input(kwargs, "camera_angle")
        lighting = self._input(kwargs, "lighting")
        background = self._input(kwargs, "background")
        characters = self._input(kwargs, "characters")
        action = self._input(kwargs, "action")
        clothing = self._input(kwargs, "clothing")
        assets = self._input(kwargs, "assets")
        quality_tags = self._input(kwargs, "quality_tags")
        negative_prompt = self._input(kwargs, "negative_prompt")
        prompt_format = self._input(kwargs, "prompt_format", "natural")
        include_labels = self._input(kwargs, "include_labels", False)
        strict_character_refs = self._input(kwargs, "strict_character_refs", True)
        show_debug = self._input(kwargs, "show_debug", True)
        prompt_prefix = self._input(kwargs, "prompt_prefix")
        prompt_suffix = self._input(kwargs, "prompt_suffix")

        character_map, character_freeform = self._parse_named_block(characters)
        clothing_map, clothing_freeform = self._parse_named_block(clothing)
        asset_map, asset_freeform = self._parse_named_block(assets)

        warnings = []
        if strict_character_refs:
            warnings.extend(self._unknown_reference_warnings("clothing", clothing_map, character_map))
            warnings.extend(self._unknown_reference_warnings("assets", asset_map, character_map))
            warnings.extend(self._action_reference_warnings(action, character_map))

        character_lines = self._character_lines(character_map, clothing_map, asset_map)
        character_summary = self._join_sentences(character_lines)
        if character_freeform:
            character_summary = self._join_parts([character_summary, character_freeform])

        action_text = self._resolve_action_refs(action, character_map)
        clothing_text = self._fallback_named_text("clothing", clothing_map, clothing_freeform, character_map)
        asset_text = self._fallback_named_text("assets", asset_map, asset_freeform, character_map)

        sections = [
            ("style", style),
            ("camera", camera_angle),
            ("lighting", lighting),
            ("background", background),
            ("characters", character_summary),
            ("action", action_text),
            ("clothing", clothing_text if not character_summary else ""),
            ("assets", asset_text if not character_summary else ""),
            ("quality", quality_tags),
        ]

        prompt = self._format_prompt(sections, prompt_format, include_labels)
        prompt = self._join_parts([prompt_prefix, prompt, prompt_suffix])
        prompt = self._clean_prompt(prompt)
        negative = self._clean_prompt(negative_prompt)
        warning_text = "\n".join(warnings)

        if show_debug:
            return {
                "ui": {
                    "prompt": [prompt],
                    "negative_prompt": [negative],
                    "character_summary": [character_summary],
                    "warnings": [warning_text],
                },
                "result": (prompt, negative, character_summary, warning_text),
            }
        return {"result": (prompt, negative, character_summary, warning_text)}

    def _input(self, kwargs, key, default=""):
        return kwargs.get(INPUT_KEYS[key], kwargs.get(key, default))

    def _parse_named_block(self, text):
        text = (text or "").strip()
        if not text:
            return {}, ""

        named = {}
        freeform = []
        current_name = None

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            line = re.sub(r"^[-*]\s+", "", line)
            match = re.match(r"^([A-Za-zÀ-ÖØ-öø-ÿ0-9 _.'-]{1,48})\s*:\s*(.+)$", line)
            if match:
                current_name = self._clean_name(match.group(1))
                value = self._clean_text(match.group(2))
                if current_name and value:
                    named[current_name] = self._join_parts([named.get(current_name, ""), value])
                continue

            if current_name and re.match(r"^[,;]?\s*(and|with|wearing|holding|carrying|using|in)\b", line, re.I):
                named[current_name] = self._join_parts([named.get(current_name, ""), line])
            else:
                freeform.append(line)

        return named, self._clean_text(" ".join(freeform))

    def _character_lines(self, characters, clothing, assets):
        lines = []
        for name, description in characters.items():
            parts = [f"{name}: {description}"]
            if name in clothing:
                parts.append(f"wearing {clothing[name]}")
            if name in assets:
                parts.append(f"with {assets[name]}")
            lines.append(self._clean_text(", ".join(parts)))
        return lines

    def _fallback_named_text(self, label, named, freeform, characters):
        if not named:
            return freeform
        lines = []
        for name, value in named.items():
            if name in characters:
                continue
            lines.append(f"{name} {label}: {value}")
        return self._join_parts([self._join_sentences(lines), freeform])

    def _unknown_reference_warnings(self, label, refs, characters):
        warnings = []
        for name in refs:
            if name not in characters:
                warnings.append(f"Unknown character reference in {label}: {name}")
        return warnings

    def _action_reference_warnings(self, action, characters):
        if not characters or not action:
            return []
        warnings = []
        bracket_refs = re.findall(r"\[([^\]]+)\]", action)
        for name in bracket_refs:
            clean = self._clean_name(name)
            if clean and clean not in characters:
                warnings.append(f"Unknown character reference in action: {clean}")
        return warnings

    def _resolve_action_refs(self, action, characters):
        def replace(match):
            name = self._clean_name(match.group(1))
            return name if name in characters else match.group(0)

        return self._clean_text(re.sub(r"\[([^\]]+)\]", replace, action or ""))

    def _format_prompt(self, sections, prompt_format, include_labels):
        cleaned = [(label, self._clean_text(value)) for label, value in sections if self._clean_text(value)]
        if include_labels:
            return ". ".join(f"{label}: {value}" for label, value in cleaned)

        values = [value for _, value in cleaned]
        if prompt_format == "tagged":
            return ", ".join(values)
        if prompt_format == "cinematic":
            return self._join_parts(["cinematic image", *values])
        if prompt_format == "sdxl":
            return self._join_parts([*values, "masterpiece, best quality, detailed, visually coherent"])
        if prompt_format == "flux":
            return self._join_sentences(values)
        return self._join_parts(values)

    def _join_parts(self, parts):
        cleaned = [self._clean_text(part) for part in parts if self._clean_text(part)]
        return ", ".join(cleaned)

    def _join_sentences(self, parts):
        cleaned = [self._clean_text(part).rstrip(".") for part in parts if self._clean_text(part)]
        return ". ".join(cleaned)

    def _clean_name(self, text):
        return re.sub(r"\s+", " ", (text or "").strip(" \t\r\n[]"))

    def _clean_text(self, text):
        text = (text or "").strip()
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r",\s*,+", ",", text)
        return text.strip(" ,.;:-")

    def _clean_prompt(self, text):
        text = self._clean_text(text)
        text = re.sub(r"\s+\.", ".", text)
        text = re.sub(r"\.\s*\.", ".", text)
        return text.strip(" ,.;:-")


NODE_CLASS_MAPPINGS = {
    "ICStructuredImagePrompt": ICStructuredImagePrompt,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ICStructuredImagePrompt": "IC Structured Image Prompt",
}
