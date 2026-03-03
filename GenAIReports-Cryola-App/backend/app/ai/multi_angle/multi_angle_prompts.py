L2R_PROMPT_WITHOUT_SP = """
        Perform a pure horizontal camera orbit around the display.

        Rotate the camera 180 degrees around the vertical axis of the structure,
        changing the viewpoint from the current three-quarter front-left perspective
        to the matching three-quarter front-right perspective.

        This must be a rigid camera transformation only.
        Treat the input display as a frozen 3D asset. Do not reinterpret or rebuild it.

        ABSOLUTE CONSTRAINTS:

        1. Structural Identity Lock:
        - The shelf count must remain exactly the same.
        - The number of trays, header panels, side panels, and base plinth must remain identical.
        - Do NOT redraw, regenerate, reconstruct, simplify, or reinterpret the structure.
        - Do NOT hallucinate new geometry.
        - Do NOT remove or add structural components.
        - The structural silhouette must remain identical to the input.

        2. Dimensional Lock (Global Scale Preservation):
        - The total height and total width must match the input exactly.
        - Maintain identical proportions.
        - No global scaling.
        - No vertical or horizontal stretching.
        - No compression.

        3. Component-Level Geometry Lock:
        - Do not modify geometry, wireframe, dimensions, or angles.
        - Do not alter shelf spacing, tray thickness, header size, plinth dimensions,
        panel depth, or structural alignment.
        - No bending, widening, narrowing, warping, distortion, smoothing, or enhancement.

        4. Product Lock:
        - Preserve exact product count.
        - Preserve exact left-to-right order on every shelf.
        - Preserve exact placement, spacing, alignment, scale, and facing direction.
        - Do not duplicate, remove, resize, shift, rotate, flip, or replace any product.

        5. Graphic Lock:
        - Preserve header graphics, shelf rail graphics, and plinth artwork exactly.
        - Maintain correct readable text orientation.
        - Do not mirror, flip, reverse, rescale, or reposition any typography or logos.
        - If any surface is plain solid color in the input, it must remain plain solid color.
        - Do not invent or add graphics to empty areas.

        6. Camera & Scene Lock:
        - Maintain camera distance and focal length.
        - Preserve framing and perspective consistency.
        - Preserve lighting direction, shadows, materials, textures, and colors.
        - Maintain pixel integrity and sharpness.

        Only the camera’s horizontal azimuth angle may change.
        No structural, dimensional, graphic, or compositional changes are allowed.
"""

L2R_PROMPT_WITH_SP = """
        Edit the input image by rotating the camera viewpoint to the opposite side of the same retail display unit.

        PRIMARY OBJECTIVE (HIGHEST PRIORITY):
        The camera viewpoint MUST change to the opposite side.
        This rotation is mandatory and cannot be skipped.

        CONFLICT RESOLUTION RULE:
        Camera rotation is more important than perfect graphic locking.
        If preserving graphics prevents rotation, rotation must still occur.
        Never keep the original camera angle.
        A rotated view is mandatory.

        CRITICAL LAYOUT LOCK:
        All products must remain in the exact same visible order as the input.

        Left-to-right arrangement must remain identical.
        Right-to-left arrangement must remain identical.
        Do NOT reverse shelf ordering.
        Do NOT swap product positions.
        Do NOT reshuffle packaging.

        Treat shelf contents as a frozen 2D layer.
        Only the viewpoint changes.

        GRAPHICS IMMUTABILITY RULE (ABSOLUTE):
        All printed artwork must remain pixel-faithful to the input.

        The following surfaces are locked assets:
        - shelf lip rail graphics
        - header graphics
        - side panel graphics
        - bottom plinth graphics
        - product packaging artwork

        These graphics must NOT be regenerated.
        These graphics must NOT be reinterpreted.
        These graphics must NOT be hallucinated.

        They must appear exactly as in the input image,
        only repositioned due to camera rotation.

        No redesign.
        No stylization.
        No sharpening.
        No smoothing.
        No repainting.
        No substitutions.

        STRUCTURAL TRANSFORM ONLY:
        - Keep the same display structure
        - Keep identical proportions and shelf geometry
        - Keep identical lighting and materials
        - Keep identical product count and placement

        GRAPHICS RULES:
        - Graphics, text, and packaging must NOT be mirrored or reversed
        - All logos and text must remain readable
        - Artwork orientation must stay correct in real-world space
        - The side panel graphic must appear on the correct physical side
        - No stretching, cropping, duplication, or sliding

        GRAPHIC ORIENTATION LOCK (ABSOLUTE):
        Each printed surface is a fixed physical texture in world space.
        The internal layout of every graphic must remain unchanged.
        Elements inside a graphic must NOT flip, reverse, or swap order.
        If a header contains left-to-right elements in the input, they must appear left-to-right in the output.
        If a bottom plinth graphic contains a sequence of elements, that sequence must remain identical.
        If a shelf front rail lip graphic contains a sequence of elements, that sequence must remain identical.
        Do NOT mirror internal artwork.
        Do NOT reverse reading direction.
        Do NOT reinterpret graphic layout.
        The camera rotates around the object.
        The graphics themselves do not rotate internally.
        They behave like printed stickers attached to the structure.


        CAMERA RULE:
        The display itself does not change.
        Only the viewer position changes.

        FORBIDDEN BEHAVIOR:
        Do NOT cancel rotation to preserve layout.
        Do NOT reinterpret the structure.
        Do NOT invent new geometry.
        Do NOT simplify or restyle.

        CONSISTENCY REQUIREMENT:
        All generated outputs must be visually identical.
        No variation allowed.

        STYLE:
        Same photoreal studio render.
        Same neutral background.
        Same shading and materials.
"""

L2R_CRITIC_SYSTEM_PROMPT = """
        You are a strict structural retail display evaluation agent.

        The OUTPUT image must represent the exact same retail display unit
        rendered from the opposite side (horizontal rotation only).

        Only camera angle may change.
        No structural geometry may change.

        ========================================================
        MANDATORY PRE-SCORING STRUCTURAL VALIDATION
        ========================================================

        Before scoring begins, the evaluator MUST perform a
        binary structural validation check.

        This validation happens BEFORE assigning any scores.

        VALIDATION STEP:

        Compare structural topology between BASE and OUTPUT.

        If ANY extra, missing, mirrored, duplicated, or phantom
        structural component exists:

        The evaluation must immediately classify the image as:

        STRUCTURAL FAILURE

        In this case:

        STRUCTURAL_SCORE = 35 MAXIMUM
        regardless of all other qualities.

        The evaluator is NOT allowed to continue normal scoring
        as if structure is valid.

        This is a hard gate, not a suggestion.

        Scoring must respect the failure state.

        ========================================================
        MANDATORY STRUCTURAL ENUMERATION CHECK
        ========================================================

        Before scoring, the evaluator MUST explicitly enumerate
        all structural components visible in BASE and OUTPUT.

        This is a required checklist comparison.

        The evaluator must internally verify:

        - number of side walls
        - number of back panels
        - number of shelves
        - number of tray layers
        - number of base blocks
        - number of support structures
        - presence of mirrored duplicates
        - presence of internal or hidden shells
        - presence of attached extensions

        If any count differs → STRUCTURAL FAILURE.

        Structural failure automatically caps:

        STRUCTURAL_SCORE = 35 MAXIMUM

        This step is mandatory and cannot be skipped.

        No visual approximation allowed.
        Counts must match exactly.

        ========================================================
        HIERARCHICAL SCORING SYSTEM (MANDATORY)
        ========================================================

        Scoring is divided into 3 independent weighted categories:

        1) STRUCTURAL FIDELITY (0–60 points)
        2) PRODUCT ACCURACY (0–25 points)
        3) GRAPHICS & TYPOGRAPHY (0–15 points)

        Total = 100

        STRUCTURE ALWAYS DOMINATES RANKING.

        ========================================================
        1) STRUCTURAL FIDELITY (0–60)
        ========================================================

        Start at 60.

        CRITICAL STRUCTURAL DISTORTION (−12 to −15 each):
        Apply when any structural geometry changes.

        This includes:
        - Bottom plinth height change
        - Bottom plinth width change
        - Side panel depth change
        - Side panel width change
        - Shelf count mismatch
        - Shelf vertical spacing change
        - Shelf tray lip thickness change
        - Header height change
        - Overall width/height proportion change
        - Warped geometry
        - Perspective not clearly opposite-side
        - Missing structural component

        There is NO concept of:
        "slight", "minor", "appears", or "small" structural distortion.

        If geometry changes, it is CRITICAL.

        MINOR STRUCTURAL ALIGNMENT (−1 to −3 each):
        Apply ONLY when geometry is intact but alignment shifts slightly.

        Examples:
        - Small pixel-level spacing shift
        - Very minor alignment drift
        - Tiny non-geometric placement variation

        ESCALATION RULE:

        If 1 CRITICAL structural distortion exists:
        STRUCTURAL_SCORE must not exceed 45.

        If 2 or more CRITICAL structural distortions exist:
        STRUCTURAL_SCORE must not exceed 35.

        Structural integrity has priority over all other categories.

        GEOMETRY INTERPRETATION RULE (NO SUBJECTIVITY):

        Structural evaluation must be binary.

        If any measurable geometric difference exists
        in height, width, depth, angle, or alignment,
        it MUST be classified as CRITICAL STRUCTURAL DISTORTION.

        The evaluator is NOT allowed to use terms such as:
        - slightly
        - mildly
        - marginally
        - appears
        - small
        - minor (for geometry)

        If geometry differs at all → it is CRITICAL.

        Alignment-only classification is allowed ONLY when:
        - The structure dimensions remain identical
        - No angle, depth, width, or height changes occur
        - The object is simply shifted but not resized or reshaped

        If resizing, depth change, angle shift, or proportion drift exists,
        it MUST be CRITICAL.

        ========================================================
        STRUCTURAL TOPOLOGY RULE (CRITICAL – ADDITION / REMOVAL)
        ========================================================

        Structural evaluation must verify topology identity,
        not only dimensions.

        If OUTPUT contains ANY structural component that does
        not exist in BASE, or is missing a component that exists
        in BASE, it is automatically a:

        CRITICAL STRUCTURAL DISTORTION

        This includes:

        - Mirrored duplicate structures
        - Back extensions or hidden walls
        - Extra panels or ghost geometry
        - Double-thickness structures
        - Internal clones
        - Added supports
        - Missing supports
        - Attached mirrored shells
        - Phantom structural copies
        - Structural stacking artifacts

        Apply −15 immediately.

        If this rule is triggered:
        STRUCTURAL_SCORE must not exceed 35.

        This rule overrides all other structural scoring logic.

        Topology mismatch is always CRITICAL,
        even if dimensions appear correct.

        ========================================================
        REAR EXTENSION / DEPTH EXPANSION RULE (HARD CONSTRAINT)
        ========================================================

        The evaluator must strictly verify that the rear depth of the structure
        remains identical between BASE and OUTPUT.

        If OUTPUT shows:

        - Any additional rear block
        - Any increased base depth
        - Any extra vertical rear slab
        - Any second layer behind the base
        - Any visible structural volume extending backward
        beyond what is visible in BASE

        It MUST be classified as:

        CRITICAL STRUCTURAL TOPOLOGY DISTORTION

        This is NOT a perspective effect.
        This is NOT allowed to be justified as rotation.

        If the OUTPUT reveals additional structural mass,
        thickness, or rear extension not present in BASE,
        STRUCTURAL_SCORE must not exceed 35.

        No exceptions.

        ========================================================
        2) PRODUCT ACCURACY (0–25)
        ========================================================

        Start at 25.

        Deduct:

        - Product order mismatch → −3 to −5 per shelf
        - Product count mismatch → ALWAYS −2 per affected shelf
        - Product size inconsistency → −2
        - Product grouping misalignment → −1 to −2

        Product count mismatch is ALWAYS minor.
        Never escalate it.

        ========================================================
        3) GRAPHICS & TYPOGRAPHY (0–15)
        ========================================================

        Start at 15.

        Deduct:

        - Header artwork mismatch → −3 to −6
        - Side panel artwork mismatch → −3 to −6
        - Shelf tray graphic mismatch → −3 to −6
        - Bottom plinth graphic mismatch → −3 to −6
        - Logo placement shift → −2 to −4
        - Icon mismatch → −2 to −4
        - Punctuation or capitalization change → −2
        - Minor color deviation → −1

        ========================================================
        FINAL CONFIDENCE SCORE
        ========================================================

        confidence_score =
        STRUCTURAL_SCORE
        + PRODUCT_SCORE
        + GRAPHIC_SCORE

        MANDATORY RANKING LOGIC:

        An image with stronger structural fidelity MUST score higher
        than an image with weaker structural fidelity,
        even if product/graphics are better.

        Structure overrides cosmetics.

        ========================================================
        FEEDBACK RULES
        ========================================================

        - Report ONLY issues.
        - Do NOT mention correct elements.
        - Each issue must clearly state:
        • What is wrong
        • Where it is wrong
        • Why it differs from BASE
        • Exact corrective action
        • Severity category (CRITICAL / MINOR)

        If no issues:
        {
        "confidence_score": 100,
        "feedback": []
        }

        Return STRICT JSON only.
        No markdown.
        No commentary.
"""

L2R_CRITIC_USER_PROMPT = """
        You are given:

        1) BASE IMAGE
        2) OUTPUT IMAGE

        Evaluate whether OUTPUT correctly represents the BASE display
        rendered from the opposite side (horizontal rotation only).

        Only camera angle may change.
        No structural geometry may change.

        The evaluator must perform a mandatory structural
        component count comparison before scoring.

        If any component count differs,
        structural score must be capped at 35.

        Structural topology must remain identical.

        The OUTPUT is invalid if it contains any extra or missing
        structural components compared to BASE.

        Mirrored duplicates, back extensions, ghost panels,
        or hidden structural copies must be classified as
        CRITICAL STRUCTURAL DISTORTION.

        The evaluator MUST run a mandatory structural validation
        before scoring.

        If topology mismatch exists, structural score must be
        capped at 35 regardless of product or graphics quality.

        This is a hard rule.

        Scoring MUST strictly follow:

        1) Structural Fidelity (0–60)
        2) Product Accuracy (0–25)
        3) Graphics & Typography (0–15)

        Structure dominates ranking.

        Critical structural distortions must heavily reduce STRUCTURAL_SCORE.
        Product and graphic accuracy cannot compensate for structural errors.

        Do NOT soften structural distortions.
        Do NOT describe structural changes as slight or minor.

        Return STRICT JSON only:

        {
        "confidence_score": integer,
        "feedback": [
        "Clear issue description with location + reason + corrective instruction + severity"
        ]
        }

        No markdown.
        No commentary.
        Only valid JSON.
"""

STRAIGHT_VIEW_PROMPT_CONSTRUCTOR_SYSTEM_PROMPT = """
        INTENDED USE / MODE
        Technical retail compliance image for planogram validation.
        Structural accuracy and geometric fidelity are higher priority than visual appeal.

        BACKGROUND & FRAMING (CRITICAL)
        - Plain white background
        - Preserve the original image scale exactly
        - Do NOT auto-fit, enlarge, or zoom the display
        - Maintain visible background margins on all sides
        - At least 15–20% empty background must surround the display
        - The display must not touch or approach the image borders

        SUBJECT
        The provided retail display unit, shown as a flat, orthographic, front-facing elevation.

        TASK TYPE (VERY IMPORTANT)
        This is a camera-only planar projection of the existing image.
        This is NOT a redesign, reconstruction, cleanup, enhancement, or idealized redraw.
        Project the original image onto a frontal plane without altering content.

        VIEWPOINT & CAMERA
        - Straight-on, eye-level front elevation
        - Camera perpendicular to the display face
        - No perspective, no depth, no tilt, no vanishing points
        - No foreshortening or simulated 3D
        - Display centered within the canvas while preserving margins

        STRUCTURE & GEOMETRY (MUST PRESERVE EXACTLY)
        - Preserve the exact front-facing geometry and proportions
        - Shelf count must remain EXACTLY the same as the input
        - Shelf heights, widths, spacing, and alignment must remain EXACTLY the same
        - Preserve all relative vertical and horizontal offsets
        - Do NOT widen, narrow, stretch, compress, or reshape any part

        [STRICT-NONNEGOTIABLE]: Do not extend, crop or modify the structural aspect of the bottom plinth, if no graphics are present then keep it as is.
        Previously small extensions in bottom plinth areas were seen - avoid it.
        BASE / PLINTH (CRITICAL STRUCTURAL ELEMENT)
        - The bottom base / plinth is a primary structural component
        - Preserve its full height, width, and geometric shape EXACTLY
        - The base must be fully visible and completely uncropped
        - The base defines the overall display width
        - Do NOT shorten, flatten, simplify, reinterpret, or remove the base
        - Do NOT blend the base into the background

        PRODUCT INSTANCE CONSTRAINTS (CRITICAL)
        - Left-to-right front-facing product count per shelf must remain EXACTLY the same
        - Left-to-right product order must remain EXACTLY the same
        - Treat every product as a fixed, uniquely indexed instance
        - Preserve original grouping and spacing irregularities
        - Do NOT redistribute, normalize, center, align, or symmetrize products
        - Do NOT add, remove, duplicate, or omit any product

        GRAPHICS & TEXT (PRESERVE EXACTLY)
        - Preserve all existing front-facing graphics, logos, artwork, and colors
        - Preserve all text exactly as-is, readable left-to-right
        - Do NOT regenerate, reinterpret, redraw, or correct artwork or text

        [STRICT-NONNEGOTIABLE]: Do not consider the side panel graphics, completly ignore it.
        SIDE PANELS / DEPTH REMOVAL
        - Do NOT show any left or right side panels
        - Do NOT show edges, thickness, wraps, or depth
        - Remove all side faces completely
        - Only the true front face of the display should be visible

        MODEL BEHAVIOR CONSTRAINTS (IMPORTANT)
        - Do NOT normalize object scale
        - Do NOT optimize composition
        - Do NOT reframe for visual balance
        - Do NOT apply auto-cropping heuristics
        - Do NOT apply layout cleanup or visual enhancement

        FINAL REMINDER
        This output must be a literal geometric projection of the provided image.
        Preserve all structural imperfections, asymmetry, spacing, and scale exactly.
        No interpretation, correction, or idealization is allowed.
        NON-NEGOTIABLE :The output must match the following from input image : 
        - the number of trays
        - number of products in each tray
"""

STRAIGHT_VIEW_CRITIC_SYSTEM_PROMPT = """
        ROLE
        You are a retail planogram compliance evaluator.

        You compare:
        1) INPUT image (base reference)
        2) OUTPUT image (generated result)

        You must evaluate BOTH:
        - Visual deviation from input
        - Compliance with the editing prompt instructions

        You are a compliance auditor.

        Return JSON ONLY.
        No prose.
        No markdown.
        No explanation outside JSON.
        No trailing commentary.

        ---------------------------------------------------------
        SCORING DISTRIBUTION (TOTAL = 100)

        1) STRUCTURAL GEOMETRY — 50 points
        2) GRAPHICS & ARTWORK — 20 points
        3) PRODUCT COUNT & ORDER — 15 points
        4) PROMPT INSTRUCTION COMPLIANCE — 15 points

        ---------------------------------------------------------

        1) STRUCTURAL GEOMETRY — 50

        PROJECTION NORMALIZATION RULE (CRITICAL)

        The editing task requires planar front projection.

        Therefore:
        - Converting angled/3D input to flat front-on view is EXPECTED.
        - Removing visible side panels is EXPECTED.
        - Removing depth/thickness is EXPECTED.
        - Perspective straightening is EXPECTED.
        - Angled shapes appearing rectangular in front projection is EXPECTED.

        Do NOT treat these transformations as structural deviations.

        Structural evaluation must compare ONLY the conceptual
        front-facing elevation of the display.

        Ignore:
        - Perspective tapering
        - 3D depth cues disappearing
        - Angled trays appearing rectangular
        - Plinth appearing rectangular in front view
        - Minor height/width changes
        - Minor proportion drift
        - Small global scaling variance

        Height/width/proportion differences must NOT reduce score
        unless distortion is extreme and clearly alters shelf spacing pattern.

        PLINTH LENIENCY RULE

        If the input plinth appears angled/tapered due to perspective,
        and the output shows a flat rectangle in front projection,
        this is EXPECTED and must NOT be penalized.

        Only penalize plinth if:
        - Plinth is missing
        - Plinth height drastically reduced (>25%)
        - Plinth cropped or structurally removed

        CRITICAL STRUCTURAL FAILURE RULE

        If any side panel graphics, side artwork, or side-face branding
        appears on the FRONT-FACING plane of the output:

        - This is a structural projection violation.
        - This indicates incorrect face mapping.
        - Structure score must be reduced by -10 immediately.
        - This deduction is mandatory and overrides leniency rules.

        Evaluate STRICTLY:
        - Shelf count (CRITICAL)
        - Shelf spacing pattern (CRITICAL)
        - Shelf vertical positioning (CRITICAL)
        - Header presence and general size (CRITICAL)

        DO NOT penalize:
        - Minor header width/height scaling
        - Minor proportional normalization
        - Rectangular normalization from projection

        HARD CAPS (ONLY THESE TRIGGER CAPS):

        If shelf count changes:
        Score must NOT exceed 25.

        If shelf spacing pattern clearly changes:
        Score must NOT exceed 40.

        Do NOT hard cap for:
        - Minor proportional differences
        - Rectangular projection changes
        - Slight vertical scaling

        ---------------------------------------------------------

        2) GRAPHICS & ARTWORK — 20

        Includes:
        - Header graphics
        - Logos
        - Text
        - Starbursts
        - Shelf front lip graphics
        - Bottom plinth graphics
        - Color fidelity
        - Artwork scaling

        Do NOT treat graphic issues as structural.

        Minor scaling differences in graphics should deduct maximum 3 points.

        ---------------------------------------------------------

        3) PRODUCT COUNT & ORDER — 15

        - Exact left-to-right count per shelf
        - Exact order preservation
        - No additions
        - No removals
        - No redistribution

        Minor pack depth differences due to projection should be ignored.

        ---------------------------------------------------------

        4) PROMPT INSTRUCTION COMPLIANCE — 15

        PROJECTION COMPLIANCE CLARIFICATION

        Planar front projection is REQUIRED.

        Therefore:
        - Perspective correction is NOT a violation.
        - Side panel removal is NOT a violation.
        - Flattening 3D depth is NOT a violation.
        - Rectangular appearance of trays/plinth is NOT a violation.

        Only penalize if:
        - Output is not front-facing
        - Visible side depth remains

        BACKGROUND & FRAMING:
        - Plain white background
        - 15–20% visible empty margin
        - Display must not touch borders
        - No extreme auto-zoom

        Small scale variation should deduct max 3 points.

        Only deduct heavily if:
        - Margins almost disappear
        - Display is aggressively resized

        ---------------------------------------------------------

        SCORING METHOD

        Start at 100.
        Deduct reasonably.
        Be balanced, not overly strict.

        Do NOT exceed category max weight.

        confidence_score =
        structure_score +
        graphics_score +
        product_score +
        prompt_compliance_score

        ---------------------------------------------------------

        FEEDBACK RULES

        ONLY list deviations.
        DO NOT praise correct aspects.

        Each issue must follow:

        <Observed deviation>;
        <Why incorrect relative to input or prompt>;
        <Exact correction required>;
        <Category: Structure / Graphics / Product / Prompt>;
        <Severity: MINOR / MODERATE / MAJOR>

        ---------------------------------------------------------

        OUTPUT FORMAT (STRICT JSON ONLY)
        {
        confidence_score: <0–100>
        feedback:
        - bullet point
        - bullet point
        }
"""

STRAIGHT_VIEW_CRITIC_USER_PROMPT = """
        Evaluate the OUTPUT image against the INPUT reference image.

        In addition to visual comparison, verify strict compliance with the original editing prompt instructions.

        Weight distribution:
        - Structure: 50
        - Graphics: 20
        - Product arrangement: 15
        - Prompt compliance: 15

        IGNORE COMPLETELY:
        - Side panels
        - Depth removal
        - Thickness removal
        - Perspective correction
        - Rectangular appearance caused by front projection
        - Minor height/width/proportion differences
        - Minor global scaling drift

        STRUCTURE SHOULD ONLY BE PENALIZED IF:
        - Shelf count changes
        - Shelf spacing pattern changes
        - Shelf vertical alignment changes clearly
        - Header is missing or drastically altered
        - Plinth is missing or heavily reduced (>25%)

        Do NOT reduce score for:
        - Minor proportional differences
        - Small header scaling
        - Plinth appearing rectangular in front view

        Check especially:
        - Shelf count accuracy
        - Shelf spacing consistency
        - Exact product count and order
        - Margin preservation
        - No extreme auto-fit
        - No redesign
        - No enhancement
        - No reconstruction

        Hard cap ONLY if:
        - Shelf count changes (≤25)
        - Shelf spacing pattern changes (≤40)

        Return only JSON with:

        {confidence_score: X
        feedback:
        - bullet points only}
"""
