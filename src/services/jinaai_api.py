from flask import request
import requests
from flask_restx import Resource
from src.server.app import api
from src.config import config_data

jinaai_ns = api.namespace("jinaai", description="Jina.ai API")


@jinaai_ns.route("/reader")
class WeatherLookUpResource(Resource):
    @jinaai_ns.doc("reader")
    @jinaai_ns.vendor(
        {
            "x-monkey-tool-name": "jinaai_reader",
            "x-monkey-tool-categories": ["quert"],
            "x-monkey-tool-display-name": "Jinai.ai Reader",
            "x-monkey-tool-description": "Read and search the web using Jinai.ai",
            "x-monkey-tool-icon": "emoji:🌐:#ceefc5",
            "x-monkey-tool-input": [
                {
                    "displayName": "Mode",
                    "name": "mode",
                    "type": "options",
                    "default": "search",
                    "options": [
                        {
                            "name": "search",
                            "value": "search",
                        },
                        {
                            "name": "read",
                            "value": "read",
                        },
                    ],
                },
                {
                    "displayName": "Input",
                    "name": "input",
                    "type": "string",
                    "required": True,
                    "description": "Any urls or questions you want to search or read on the web.",
                },
                {
                    "displayName": "JSON Response",
                    "name": "enable_json_response",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
                {
                    "displayName": "Image Caption",
                    "name": "enable_image_caption",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                    "description": "Captions all images at the specified URL, adding 'Image [idx]: [caption]' as an alt tag for those without one. This allows downstream LLMs to interact with the images in activities such as reasoning and summarizing.",
                },
                {
                    "diaplayName": "Gather All Links At the End",
                    "name": "gather_all_links_at_the_end",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                    "description": 'A "Buttons & Links" section will be created at the end. This helps the downstream LLMs or web agents navigating the page or take further actions.',
                },
                {
                    "displayName": "Gather All Images At the End",
                    "name": "gather_all_images_at_the_end",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                    "description": 'An "Images" section will be created at the end. This gives the downstream LLMs an overview of all visuals on the page, which may improve reasoning.',
                },
            ],
            "x-monkey-tool-output": [
                {
                    "displayName": "Json Result for Search",
                    "name": "json_result_for_search",
                    "type": "array",
                    "properties": [
                        {
                            "displayName": "Url",
                            "name": "url",
                            "type": "string",
                        },
                        {
                            "displayName": "Title",
                            "name": "title",
                            "type": "string",
                        },
                        {
                            "displayName": "Content",
                            "name": "content",
                            "type": "string",
                        },
                        {
                            "displayName": "Description",
                            "name": "description",
                            "type": "string",
                        },
                    ],
                },
                {
                    "displayName": "Json Result for Read",
                    "name": "json_result_for_read",
                    "type": "json",
                    "properties": [
                        {
                            "displayName": "Url",
                            "name": "url",
                            "type": "string",
                        },
                        {
                            "displayName": "Title",
                            "name": "title",
                            "type": "string",
                        },
                        {
                            "displayName": "Content",
                            "name": "content",
                            "type": "string",
                        },
                        {
                            "displayName": "Description",
                            "name": "description",
                            "type": "string",
                        },
                    ],
                },
                {
                    "displayName": "Markdown Result",
                    "name": "markdown_result",
                    "type": "string",
                },
            ],
            "x-monkey-tool-extra": {
                "estimateTime": 5,
            },
        }
    )
    def post(self):
        json = request.json
        mode = json.get("mode", "search")
        input = json.get("input")
        if not input:
            raise Exception("Input is required")
        enable_json_response = json.get("enable_json_response", False)
        enable_image_caption = json.get("enable_image_caption", False)
        gather_all_links_at_the_end = json.get("gather_all_links_at_the_end", False)
        gather_all_images_at_the_end = json.get("gather_all_images_at_the_end", False)

        apikey = config_data.get("jinaai", {}).get("apikey")

        server = "https://s.jina.ai" if mode == "search" else "https://r.jina.ai"
        api = f"{server}/{input}"
        headers = {}
        if enable_json_response:
            headers["Accept"] = "application/json"
        if enable_image_caption:
            headers["X-With-Generated-Alt"] = "true"
        if gather_all_links_at_the_end:
            headers["X-With-Links-Summary"] = "true"
        if gather_all_images_at_the_end:
            headers["X-With-Images-Summary"] = "true"
        if apikey:
            headers["Authorization"] = f"Bearer {apikey}"

        r = requests.get(api, headers=headers)
        if enable_json_response:
            result = r.json()
            code = result.get("code", 200)
            if code != 200:
                raise Exception(result.get("readableMessage"))
            data = result.get("data", [])
            if mode == "read":
                return {"json_result_for_read": data}
            else:
                return {"json_result_for_search": data}
        else:
            return {"markdown_result": r.text}
