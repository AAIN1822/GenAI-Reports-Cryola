# ==========================================
# CENTRALIZED PROMPTS
# ==========================================

def theme_prompt(hex_code, outline_hex):
    return f"""
        Recolor the display unit in the provided image using the exact theme color {hex_code}.

        Apply the hex color strictly and uniformly across all visible surfaces of the display unit.

        CRITICAL STRUCTURE PRESERVATION:
        – Preserve 100% of the original structure, geometry, proportions, edges, alignment, and perspective.
        – Preserve original lighting behavior (do NOT modify it), shadows, reflections, line weight, thickness, angles, and graphical details.
        – Do NOT redraw, re-render, stylize, enhance, smooth, or reinterpret the display unit.
        – Do NOT alter camera angle, crop, zoom, rotate, distort, or resize.
        – Do NOT modify the background in any way.

        COLOR APPLICATION RULES:
        – Apply the EXACT hex code {hex_code} as a solid, flat, uniform fill.
        – No gradients, no shading variation, no tonal differences.
        – No highlights, glow, reflections, texture overlays, or material changes.
        – The color must match the hex value precisely across all surfaces.

        WIRE FRAME / OUTLINE RULE:
        – Convert ALL wireframe and outline lines to EXACTLY {outline_hex}.
        – The outline color must be a pure solid value (no transparency, no glow, no blending).
        – Do NOT change outline thickness, position, sharpness, edge precision, or geometry.
        – Do NOT introduce new outlines.
        – Only replace the existing outline color with {outline_hex}.

        POSITIONING RULE:
        – The display unit must remain perfectly centered in the frame exactly as in the original image.
        – Do NOT shift, offset, crop, or reposition the unit.
        – Maintain identical margins and spacing relative to the canvas edges.

        This must be a strict pixel-level surface color replacement only.
        The final output must be visually identical to the input image in every structural and graphical aspect, with only:
        1) The surface color replaced by {hex_code}, and  
        2) The outline/wireframe color replaced by {outline_hex}.
"""

EVALUATOR_INSTRUCTIONS = """ 

        You are the Evaluator Agent.

        Your task is to evaluate recolored display-unit images generated from a theme-application workflow.

        You will receive:
        - one reference image
        - one theme prompt (containing the target surface hex color and required outline color)
        - one or more generated output images

        Your evaluation must be deterministic, rule-based, and rely only on visible evidence in the images.

        PRIMARY OBJECTIVE
        For each generated output image, assign a confidence score from 0 to 100 that measures how accurately the image satisfies the theme prompt.

        SCORING BREAKDOWN
        - Structure & Geometry Accuracy: 60%
        - Color & Theme Accuracy: 40%

        STRUCTURE & GEOMETRY RULES (60%)
        Evaluate how closely the generated image preserves the reference:
        - Overall shape, proportions, layout, and perspective must match.
        - Shelf positions, spacing, and alignment must match the reference.
        - Edges, outlines, and structural boundaries must remain intact.
        - Camera angle must be preserved.
        - Structural outlines must remain in identical positions and must not be removed or newly added.
        - Minor variations in line thickness (1–2 px) are acceptable.
        - Minor smoothing or simplification of outlines is acceptable.
        Penalize if any structural part is missing, warped, misaligned, stretched, or visibly changed.

        COLOR & THEME RULES (40%)

        This category includes BOTH surface color compliance and outline color compliance.

        A) Surface Color Compliance (30%)

        - Recolored surfaces must use the same hue family as the target surface hex color.
        - Any lighter or darker version of the same hue is fully acceptable.
        - Brightness differences must NOT affect the score.
        - Shadows, shading, reflections, and lighting gradients must NOT affect the score.
        - Penalize only if there are major hue shifts into a different color family.
        - Recolor must apply exclusively to valid display-unit surfaces.
        - There must be no hue mixing, unintended colors, or visible patchiness in hue.
        - Background must remain untouched.

        B) Outline / Wireframe Compliance (10%)

        - All visible outlines and wireframe lines must exactly match the required outline hex color specified in the theme prompt.
        - Outline color must be uniform and consistent across the entire unit.
        - No partial recoloring of outlines is allowed.
        - Do NOT penalize minor thickness variation (1–2 px).
        - Penalize if:
            - Outline color does not match the required hex color.
            - Some outlines are recolored while others are not.
            - New outlines are introduced.
            - Original outlines are missing.


        Do NOT evaluate for surface color:
        - luminance or brightness
        - lightness or darkness
        - shading or surface gradients
        - reflections or lighting artifacts

        However, outline color must match the exact required hex value regardless of luminance.

        IMPROVEMENT REQUIREMENT
        For each image, provide exactly one actionable sentence describing what visible change would raise the score to 100.

        REGENERATION DECISION RULE
        After evaluating all output images:
        - If all confidence scores are below 85 = "regenerate_required": "yes"
        - If at least one score is 85 or above = "regenerate_required": "no"

        OUTPUT FORMAT
        Return ONLY valid JSON in the following format:

        {
        "evaluation": [
            {
            "image_id": "v1",
            "confidence_score": <number>,
            "feedback": "<one-sentence improvement>"
            }
        ],
        "regenerate_required": "yes" or "no"
        }

        Assign image_id values as "v1", "v2", "v3", … in the order received.

        Do not include analysis, commentary, or markdown outside the JSON.
        """

FEEDBACK_ANALYZER_INSTRUCTIONS = """
        You are preparing a precise GPT-IMAGE-1 editing prompt.

        You will receive:
        - An input image selected by the client
        - Client feedback describing desired modifications

        Your task:
        Rewrite the client's feedback into a clear, production-ready GPT-IMAGE-1 edit prompt.

        Non-destructive constraints that must always be respected:
        • Preserve the exact structure, shape, edges, proportions, and geometry of the display unit.
        • Preserve all original lighting, shadows (unless the requested edit involves shadows), reflections, and perspective.
        • Preserve all line art, outlines, thicknesses, angles, and graphical details.
        • Do NOT add or remove elements unless the client explicitly requested it.
        • Do NOT change the camera angle, proportions, brightness, contrast, or shading unless specifically requested.
        • Do NOT re-render, smooth, stylize, or redraw the display unit.
        • Do NOT modify or replace the background unless the feedback clearly requires it.
        • Apply edits ONLY to the regions explicitly described in the client's feedback; all other areas must remain pixel-accurate to the input image.

        General principle:
        Apply only what the client asked for. Everything else in the image must remain unchanged.

        Strict Output Format:
        Return ONLY a JSON object exactly like this:

        {
        "refined_prompt": "<complete GPT-IMAGE-1 edit prompt>"
        }

        The value of refined_prompt must be a complete GPT-IMAGE-1 edit prompt that:
        - references the input image,
        - describes exactly what to change,
        - states what must be preserved,
        - and clearly describes the intended final appearance.

        Do not include explanations, reasoning, or any fields other than refined_prompt.
        """

REFINEMENT_EVALUATOR_PROMPT = """
        You are the Evaluator Agent.

        Your role is to judge whether the Feedback-Generated Image correctly follows:
        1. All explicit instructions in the Refined Prompt.
        2. All structure, geometry, and proportions of the First Output Image.

        You will receive:
        1. First Output Image – the initial generated image before feedback.
        2. Refined Prompt – the feedback-integrated instructions describing the required visual edits.
        3. Feedback-Generated Image – the new image produced after applying the refined prompt.

        Your evaluation must rely only on visible evidence, be deterministic, and follow the rules below.

        ------------------------------------------------------------
        STRUCTURE FIDELITY — 60%
        Compare the Feedback-Generated Image to the First Output Image.

        Check for:
        - Identical geometry and silhouette
        - Matching proportions and layout
        - Same perspective and camera angle
        - Preserved shelves, walls, dividers, lips, outlines, and edges
        - No distortion, warping, softening, stretching, or missing structure
        - No added shapes, removed shapes, or structural edits

        Ignore:
        - Colors
        - Graphics
        - Patterns
        - Brightness or shading
        - Texture differences
        - Artistic variations

        The structure must match perfectly even if the theme changes completely.

        ------------------------------------------------------------
        THEME / INSTRUCTION ACCURACY — 40%
        Compare the Feedback-Generated Image to the Refined Prompt.

        Check for:
        - All requested theme edits applied
        - No missing changes
        - No incorrect modifications
        - Theme elements placed only where instructed
        - Recolors, textures, or patterns added only where specified

        Brightness, luminance, shading, reflections, or lightness differences must never reduce the score.

        Do not penalize:
        - Large theme changes
        - New graphics or patterns
        - Complete recolors
        unless the Refined Prompt forbids them.

        Penalize only:
        - Missing required theme edits
        - Wrong surfaces recolored
        - Theme applied to unintended areas
        - Instructions not followed

        ------------------------------------------------------------
        REGENERATION DECISION RULE
        If final score < 85 = "regeneration_required": "yes"
        If final score ≥ 85 = "regeneration_required": "no"

        ------------------------------------------------------------
        OUTPUT FORMAT
        Return only this JSON object:

        {
        "confidence_score": <0-100>,
        "explanation": "<single objective explanation based on visible evidence>",
        "regeneration_required": "yes" or "no"
        }

        Do not include any reasoning steps, chain-of-thought, or additional fields.
        """

# --- UTILITY FOR PROMPTS ---
def create_updated_prompt(base_prompt: str, feedback: str) -> str:
    """Restores the Delta Corrections logic"""
    return f"""{base_prompt}\n\
            ---
            REGENERATION ATTEMPT - DELTA CORRECTIONS:
            The previous rendering attempt(s) were evaluated and the following specific issues were identified:
            {feedback}
            INSTRUCTION: Apply ONLY these corrections while keeping everything else from the base requirements unchanged.
            """