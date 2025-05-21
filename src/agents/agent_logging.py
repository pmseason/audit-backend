#!/usr/bin/env python3

#
# Client to record and save Browser-Use activity.
# Save this code to client.py and run with `python client.py`
#

import asyncio
import requests
from dotenv import load_dotenv
from pyobjtojson import obj_to_json
from langchain_openai import ChatOpenAI
from browser_use import Agent
import json
import base64
from pathlib import Path
import prettyprinter
from loguru import logger


# Load environment variables (for API keys)
load_dotenv(override=True)
prettyprinter.install_extras(exclude=['ipython_repr_pretty', 'django', 'ipython', 'numpy'])


async def record_activity(agent_obj):
    """Hook function that captures and records agent activity at each step"""
    website_html = None
    website_screenshot = None
    urls_json_last_elem = None
    model_thoughts_last_elem = None
    model_outputs_json_last_elem = None
    model_actions_json_last_elem = None
    extracted_content_json_last_elem = None

    print('--- ON_STEP_START HOOK ---')
    
    # Capture current page state
    website_html = await agent_obj.browser_context.get_page_html()
    website_screenshot = await agent_obj.browser_context.take_screenshot()

    # Make sure we have state history
    if hasattr(agent_obj, "state"):
        history = agent_obj.state.history
    else:
        history = None
        print("Warning: Agent has no state history")
        return

    # Process model thoughts
    model_thoughts = obj_to_json(
        obj=history.model_thoughts(),
        check_circular=False
    )
    if len(model_thoughts) > 0:
        model_thoughts_last_elem = model_thoughts[-1]

    # Process model outputs
    model_outputs = agent_obj.state.history.model_outputs()
    model_outputs_json = obj_to_json(
        obj=model_outputs,
        check_circular=False
    )
    if len(model_outputs_json) > 0:
        model_outputs_json_last_elem = model_outputs_json[-1]

    # Process model actions
    model_actions = agent_obj.state.history.model_actions()
    model_actions_json = obj_to_json(
        obj=model_actions,
        check_circular=False
    )
    if len(model_actions_json) > 0:
        model_actions_json_last_elem = model_actions_json[-1]

    # Process extracted content
    extracted_content = agent_obj.state.history.extracted_content()
    extracted_content_json = obj_to_json(
        obj=extracted_content,
        check_circular=False
    )
    if len(extracted_content_json) > 0:
        extracted_content_json_last_elem = extracted_content_json[-1]

    # Process URLs
    urls = agent_obj.state.history.urls()
    urls_json = obj_to_json(
        obj=urls,
        check_circular=False
    )
    if len(urls_json) > 0:
        urls_json_last_elem = urls_json[-1]

    # Create a summary of all data for this step
    model_step_summary = {
        # "website_html": website_html,
        # "website_screenshot": website_screenshot,
        "url": urls_json_last_elem,
        "model_thoughts": model_thoughts_last_elem,
        "model_outputs": model_outputs_json_last_elem,
        "model_actions": model_actions_json_last_elem,
        "extracted_content": extracted_content_json_last_elem
    }

    # print("--- MODEL STEP SUMMARY ---")
    # print(f"URL: {urls_json_last_elem}")
    
    # # Save the data
    # prettyprinter.cpprint(model_step_summary)

    # Ensure the "recordings" folder exists using pathlib
    recordings_folder = Path("recordings")
    recordings_folder.mkdir(exist_ok=True)

    # Determine the next file number by examining existing .json files
    existing_numbers = []
    for item in recordings_folder.iterdir():
        if item.is_file() and item.suffix == ".json":
            try:
                file_num = int(item.stem)
                existing_numbers.append(file_num)
            except ValueError:
                # In case the file name isn't just a number
                pass

    if existing_numbers:
        next_number = max(existing_numbers) + 1
    else:
        next_number = 1

    # Construct the file path
    file_path = recordings_folder / f"{next_number}.json"

    # Save the JSON data to the file
    with file_path.open("w") as f:
        json.dump(model_step_summary, f, indent=2)

    # Save screenshot if needed
    if website_screenshot:
        screenshot_folder = Path("screenshots")
        screenshot_folder.mkdir(exist_ok=True)
        # Convert and save the screenshot
        with (screenshot_folder / f"{next_number}.png").open("wb") as f:
            f.write(base64.b64decode(website_screenshot))

    logger.info(f"Successfully saved agent history step to {file_path}")