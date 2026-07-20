"""Generate CEASA app icon using Gemini Nano Banana."""
import asyncio
import base64
import os
import sys
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv("/app/backend/.env")

PROMPT = (
    "A modern, clean, minimalist app icon for a produce/greengrocer B2B ordering platform called 'CEASA'. "
    "Square 1:1 aspect ratio, centered composition, vibrant emerald-green background gradient. "
    "In the center: a stylized flat-design illustration combining a leaf and a wooden crate/box of fresh vegetables and fruits "
    "(tomato, carrot, lettuce) with a small subtle price-tag or checkmark indicating orders. "
    "Bold, professional, high contrast, crisp edges, no text, no letters, no words. "
    "Style: flat vector, iOS/Android app icon aesthetic, safe padding around the edges (15%), "
    "solid rounded-square feel. Rich saturated colors, glossy finish, drop shadow. "
    "Rendered as a high-resolution square icon suitable for a Progressive Web App launcher."
)


async def main():
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        print("ERROR: EMERGENT_LLM_KEY not set", file=sys.stderr)
        sys.exit(1)

    chat = LlmChat(
        api_key=api_key,
        session_id="ceasa-icon-gen",
        system_message="You are an expert graphic designer generating professional app icons.",
    )
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(
        modalities=["image", "text"]
    )

    msg = UserMessage(text=PROMPT)
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"Text: {text[:120] if text else '(none)'}")
    if not images:
        print("ERROR: No image returned", file=sys.stderr)
        sys.exit(2)

    out_path = "/app/icon-source.png"
    image_bytes = base64.b64decode(images[0]["data"])
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved raw icon to {out_path} ({len(image_bytes)} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
