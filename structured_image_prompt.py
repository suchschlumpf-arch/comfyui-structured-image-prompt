import re


DEFAULT_NEGATIVE_PROMPT = (
    "low quality, blurry, distorted anatomy, extra fingers, missing fingers, "
    "bad hands, deformed face, duplicate subject, unreadable text, watermark"
)


INPUT_KEYS = {
    "style": "style",
    "camera_angle": "camera angle",
    "lighting": "lighting",
    "background": "background",
    "characters": "characters",
    "action": "action",
    "clothing": "clothing",
    "assets": "assets",
    "quality_tags": "quality tags",
    "negative_prompt": "negative prompt",
    "prompt_format": "prompt format",
    "include_labels": "include labels",
    "strict_character_refs": "check character refs",
    "show_debug": "show debug",
    "prompt_prefix": "prompt prefix",
    "prompt_suffix": "prompt suffix",
}


FIELD_HEADINGS = {
    "BILDSTIL",
    "BILDSTIL / LOOK",
    "KAMERA",
    "KAMERA / BILDWINKEL",
    "BELEUCHTUNG",
    "HINTERGRUND",
    "HINTERGRUND / SETTING",
    "CHARAKTERE",
    "HANDLUNG",
    "HANDLUNG / POSE",
    "KLEIDUNG",
    "ASSETS",
    "ASSETS / REQUISITEN",
    "QUALITAET",
    "QUALITAET / DETAILS",
    "NEGATIVER PROMPT",
    "PROMPT-PREFIX",
    "PROMPT-SUFFIX",
    "STYLE",
    "CAMERA ANGLE",
    "LIGHTING",
    "BACKGROUND",
    "CHARACTERS",
    "ACTION",
    "CLOTHING",
    "ASSETS",
    "QUALITY TAGS",
    "NEGATIVE PROMPT",
    "PROMPT PREFIX",
    "PROMPT SUFFIX",
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
                        "default": "style: cinematic fantasy realism, detailed materials, coherent composition",
                        "tooltip": "Overall visual style: genre, medium, render look, era, and detail level.",
                    },
                ),
                INPUT_KEYS["camera_angle"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "camera angle: medium full shot, slight low angle, 35mm lens perspective",
                        "tooltip": "Camera perspective, framing, lens feel, composition, and viewing angle.",
                    },
                ),
                INPUT_KEYS["lighting"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "lighting: soft rim light, warm key light, atmospheric depth",
                        "tooltip": "Light sources, mood, shadows, contrast, time of day, and atmosphere.",
                    },
                ),
                INPUT_KEYS["background"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "background: ancient city street after rain, distant lanterns, subtle mist",
                        "tooltip": "Location, environment, weather, architecture, depth, and visible background elements.",
                    },
                ),
                INPUT_KEYS["characters"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "characters:\n"
                            "Mira: young rogue mage, short silver hair, confident expression\n"
                            "Oskar: old mechanic, heavy beard, tired eyes"
                        ),
                        "tooltip": "Characters as name: description. Reuse these names in action, clothing, and assets.",
                    },
                ),
                INPUT_KEYS["action"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "action: [Mira] watches the rooftops while [Oskar] repairs a small flying drone beside her",
                        "tooltip": "What happens in the image. Use [name] to reference characters clearly.",
                    },
                ),
                INPUT_KEYS["clothing"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "clothing:\n"
                            "Mira: black tactical coat, blue scarf, leather boots\n"
                            "Oskar: worn orange work jacket, welding gloves"
                        ),
                        "tooltip": "Clothing per character as name: clothing. Names should match the characters field.",
                    },
                ),
                INPUT_KEYS["assets"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "assets:\n"
                            "Mira: engraved wand, glowing wrist charm\n"
                            "Oskar: toolbox, brass repair drone"
                        ),
                        "tooltip": "Objects, weapons, props, companions, or important items per character.",
                    },
                ),
                INPUT_KEYS["quality_tags"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "quality tags: high quality, sharp focus, rich texture detail, natural color harmony",
                        "tooltip": "Quality and detail terms appended near the end of the positive prompt.",
                    },
                ),
                INPUT_KEYS["negative_prompt"]: (
                    "STRING",
                    {
                        "multiline": True,
                        "default": f"negative prompt: {DEFAULT_NEGATIVE_PROMPT}",
                        "tooltip": "Terms that should be avoided in the image.",
                    },
                ),
                INPUT_KEYS["prompt_format"]: (
                    ["natural", "tagged", "cinematic", "sdxl", "flux"],
                    {"default": "natural", "tooltip": "Controls how the sections are assembled into one prompt."},
                ),
                INPUT_KEYS["include_labels"]: (
                    "BOOLEAN",
                    {"default": False, "tooltip": "When enabled, section labels such as style/background remain in the final prompt."},
                ),
                INPUT_KEYS["strict_character_refs"]: (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Warns when clothing, assets, or [name] references do not match a character."},
                ),
                INPUT_KEYS["show_debug"]: (
                    "BOOLEAN",
                    {"default": True, "tooltip": "Shows prompt, negative prompt, character summary, and warnings in the node output."},
                ),
            },
            "optional": {
                INPUT_KEYS["prompt_prefix"]: (
                    "STRING",
                    {"multiline": False, "default": "", "tooltip": "Text placed before the final prompt, for example a LoRA trigger."},
                ),
                INPUT_KEYS["prompt_suffix"]: (
                    "STRING",
                    {"multiline": False, "default": "", "tooltip": "Text placed after the final prompt."},
                ),
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
            if self._is_heading_line(line):
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
            parts = [f"{name} is {description}"]
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
            if clean.upper() in FIELD_HEADINGS:
                continue
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
            return self._format_descriptive_prompt(cleaned, "Create a cinematic image")
        if prompt_format == "sdxl":
            return self._format_sdxl_prompt(cleaned)
        if prompt_format == "flux":
            return self._format_flux_prompt(cleaned)
        return self._format_descriptive_prompt(cleaned, "Create a coherent image")

    def _format_sdxl_prompt(self, cleaned_sections):
        sections = {label: value for label, value in cleaned_sections}
        parts = [
            "masterpiece",
            "best quality",
            "highly detailed",
            "visually coherent",
        ]
        ordered_labels = (
            "style",
            "characters",
            "action",
            "clothing",
            "assets",
            "background",
            "camera",
            "lighting",
            "quality",
        )
        for label in ordered_labels:
            value = sections.get(label)
            if value:
                parts.append(self._tag_friendly(value))
        return self._join_parts(parts)

    def _format_flux_prompt(self, cleaned_sections):
        sections = {label: value for label, value in cleaned_sections}
        action = sections.get("action")
        background = sections.get("background")
        characters = sections.get("characters")
        style = sections.get("style")
        camera = sections.get("camera")
        lighting = sections.get("lighting")
        quality = sections.get("quality")

        sentences = []
        if action and background:
            sentences.append(f"A clear image of a scene where {action}, set in {background}")
        elif action:
            sentences.append(f"A clear image of a scene where {action}")
        elif characters and background:
            sentences.append(f"A clear image of {characters} in {background}")
        elif characters:
            sentences.append(f"A clear image of {characters}")
        elif background:
            sentences.append(f"A clear image set in {background}")
        else:
            sentences.append("A clear image")

        if characters and action:
            sentences.append(f"{characters}")
        if camera:
            sentences.append(f"The composition uses {camera}")
        if lighting:
            sentences.append(f"The lighting is {lighting}")
        if style:
            sentences.append(f"The visual style is {style}")
        if quality:
            sentences.append(f"Keep the image {quality}")

        return self._join_sentences(sentences)

    def _tag_friendly(self, text):
        text = self._clean_text(text)
        text = re.sub(r"\.\s+", ", ", text)
        return text.strip(" ,.;:-")

    def _format_descriptive_prompt(self, cleaned_sections, opener):
        sections = {label: value for label, value in cleaned_sections}
        sentences = []

        action = sections.get("action")
        background = sections.get("background")
        characters = sections.get("characters")
        style = sections.get("style")
        camera = sections.get("camera")
        lighting = sections.get("lighting")
        quality = sections.get("quality")

        if action:
            if background:
                sentences.append(f"{opener} of a scene where {action}, set in {background}")
            else:
                sentences.append(f"{opener} of a scene where {action}")
        elif characters:
            if background:
                sentences.append(f"{opener} of {characters} in {background}")
            else:
                sentences.append(f"{opener} of {characters}")
        elif background:
            sentences.append(f"{opener} set in {background}")
        else:
            sentences.append(opener)

        if characters and action:
            sentences.append(f"Character details: {characters}")
        clothing = sections.get("clothing")
        if clothing:
            sentences.append(f"Wardrobe details: {clothing}")
        assets = sections.get("assets")
        if assets:
            sentences.append(f"Important props and assets: {assets}")
        if camera:
            sentences.append(f"Frame the shot as {camera}")
        if lighting:
            sentences.append(f"Use {lighting}")
        if style:
            sentences.append(f"Render it in {style}")
        if quality:
            sentences.append(f"Emphasize {quality}")

        return self._join_sentences(sentences)

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
        text = self._strip_leading_heading(text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r",\s*,+", ",", text)
        return text.strip(" ,.;:-")

    def _strip_leading_heading(self, text):
        while True:
            stripped = text.lstrip()
            match = re.match(r"^\[([^\]]+)\]\s*", stripped)
            if match and match.group(1).strip().upper() in FIELD_HEADINGS:
                text = stripped[match.end():]
                continue
            match = re.match(r"^([A-Za-z /-]{3,40})\s*:\s*", stripped)
            if match and match.group(1).strip().upper() in FIELD_HEADINGS:
                text = stripped[match.end():]
                continue
            return text

    def _is_heading_line(self, line):
        stripped = line.strip()
        bracketed = re.match(r"^\[([^\]]+)\]$", stripped)
        if bracketed:
            return bracketed.group(1).strip().upper() in FIELD_HEADINGS
        colon = re.match(r"^([A-Za-z /-]{3,40})\s*:$", stripped)
        if colon:
            return colon.group(1).strip().upper() in FIELD_HEADINGS
        return stripped.upper() in FIELD_HEADINGS

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
