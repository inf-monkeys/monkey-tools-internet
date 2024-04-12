from tavily import TavilyClient
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import yaml
import traceback


def load_config(filename):
    with open(filename, "r") as file:
        config = yaml.safe_load(file)
    return config


# Init tavily client
config_data = load_config("config.yaml")
tavily_apikey = config_data.get("tavily", {}).get("apikey")

if not tavily_apikey:
    raise ValueError("Tavily API key not found in config file")
tavily = TavilyClient(api_key=tavily_apikey)

# Init Flask app
app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Monkey Tools Tavily AI",
    description="API for Monkey Tools Tavily AI",
)


@app.before_request
def before_request():
    request.app_id = request.headers.get("x-monkeys-appid")
    request.user_id = request.headers.get("x-monkeys-userid")
    request.team_id = request.headers.get("x-monkeys-teamid")
    request.workflow_id = request.headers.get("x-monkeys-workflowid")
    request.workflow_instance_id = request.headers.get("x-monkeys-workflow-instanceid")


@api.errorhandler(Exception)
def handle_exception(error):
    traceback.print_exc()
    response = {"message": str(error)}
    response["code"] = 500
    return jsonify(response), response["code"]


@app.get("/manifest.json")
def get_manifest():
    return {
        "schema_version": "v1",
        "display_name": "Tavily AI",
        "namespace": "monkey_tools_tavily_ai",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "/swagger.json"},
        "contact_email": "dev@inf-monkeys.com",
    }


ns = api.namespace("", description="Tavily AI Api")


# Search endpoint
@ns.route("/search")
class TavilySearch(Resource):
    """Search By Tavily AI."""

    @ns.doc("search")
    @ns.vendor(
        {
            "x-monkey-tool-name": "search",
            "x-monkey-tool-categories": ["query"],
            "x-monkey-tool-display-name": "Tavily AI 搜索",
            "x-monkey-tool-description": "使用 Tavily AI 进行搜索",
            "x-monkey-tool-icon": "emoji:💿:#e58c3a",
            "x-monkey-tool-input": [
                {
                    "displayName": "搜索关键词",
                    "name": "query",
                    "type": "string",
                    "required": True,
                },
                {
                    "displayName": "搜索深度",
                    "name": "search_depth",
                    "type": "options",
                    "options": [
                        {
                            "name": "basic",
                            "value": "basic",
                        },
                        {
                            "name": "advanced",
                            "value": "advanced",
                        },
                    ],
                    "default": "basic",
                    "required": False,
                },
                {
                    "displayName": "搜索主题",
                    "name": "topic",
                    "type": "options",
                    "options": [
                        {
                            "name": "general",
                            "value": "general",
                        },
                        {
                            "name": "news",
                            "value": "news",
                        },
                    ],
                    "default": "general",
                    "required": False,
                },
                {
                    "displayName": "搜索天数",
                    "name": "days",
                    "type": "number",
                    "default": 2,
                    "required": False,
                },
                {
                    "displayName": "最大结果数",
                    "name": "max_results",
                    "type": "number",
                    "default": 5,
                    "required": False,
                },
                {
                    "displayName": "限制域名搜索范围",
                    "name": "include_domains",
                    "type": "string",
                    "required": False,
                    "default": "",
                    "description": "只在这些域名中搜索，用逗号分隔",
                },
                {
                    "displayName": "排除域名",
                    "name": "exclude_domains",
                    "type": "string",
                    "description": "排除域名，用逗号分隔",
                    "required": False,
                    "default": "",
                },
                {
                    "displayName": "是否包含答案",
                    "name": "string",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
                {
                    "displayName": "是否包含原始内容",
                    "name": "include_raw_content",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
                {
                    "displayName": "是否包含图片",
                    "name": "include_images",
                    "type": "boolean",
                    "required": False,
                    "default": False,
                },
            ],
            "x-monkey-tool-output": [
                {
                    "name": "name",
                    "displayName": "知识库唯一标志",
                    "type": "string",
                },
            ],
            "x-monkey-tool-extra": {
                "estimateTime": 5,
            },
        }
    )
    @ns.expect(
        ns.model(
            "Search",
            {
                "query": fields.String(required=True, description="Search query"),
                "search_depth": fields.String(
                    required=False, description="Search depth"
                ),
                "topic": fields.String(required=False, description="Search topic"),
                "days": fields.Integer(required=False, description="Search days"),
                "max_results": fields.Integer(
                    required=False, description="Search max results"
                ),
                "include_domains": fields.String(
                    required=False,
                    description="Only search in those domain, seperated by comma",
                    example="finance.yahoo.com,seekingalpha.com",
                ),
                "exclude_domains": fields.String(
                    required=False,
                    description="Exclude those domain, seperated by comma",
                    example="finance.yahoo.com,seekingalpha.com",
                ),
                "include_answer": fields.Boolean(
                    required=False, description="Include answer"
                ),
                "include_raw_content": fields.Boolean(
                    required=False, description="Include raw content"
                ),
                "include_images": fields.Boolean(
                    required=False, description="Include images"
                ),
            },
        )
    )
    @ns.response(
        200,
        "Success",
        ns.model(
            "SearchResponse",
            {
                "query": fields.String(required=True, description="Search query"),
                "follow_up_questions": fields.String(
                    required=False, description="Follow up questions"
                ),
                "answer": fields.String(required=False, description="Answer"),
                "images": fields.List(
                    fields.String, required=False, description="Images"
                ),
                "results": fields.List(
                    fields.Nested(
                        api.model(
                            "Result",
                            {
                                "title": fields.String(
                                    required=True, description="Result title"
                                ),
                                "url": fields.String(
                                    required=True, description="Result url"
                                ),
                                "content": fields.String(
                                    required=True, description="Result content"
                                ),
                                "score": fields.Float(
                                    required=True, description="Result score"
                                ),
                                "raw_content": fields.String(
                                    required=False, description="Result raw content"
                                ),
                            },
                        ),
                        required=True,
                        description="Results",
                    )
                ),
                "response_time": fields.Float(
                    required=True, description="Response time"
                ),
            },
        ),
    )
    def post(self):
        """
        Example response:
        {
            "query": "Why is Nvidia growing rapidly?\n",
            "follow_up_questions": null,
            "answer": "Nvidia is experiencing rapid growth primarily due to its significant role in the artificial intelligence (AI) boom. The demand for Nvidia's powerful graphics processing units (GPUs) in large computers that process data and power generative AI has propelled its growth. The company's stock value surged as it forecasted sales far exceeding Wall Street analysts' expectations, indicating strong market demand for its products. The AI boom has positioned Nvidia as one of the most valuable companies in the world, showcasing its pivotal role in driving technological advancements.",
            "images": [
                "https://static.seekingalpha.com/uploads/2022/2/53926820_16456042708305_rId4.png",
                "https://static.seekingalpha.com/uploads/2020/10/1/6965821-16016043051145468_origin.png",
                "https://static.seekingalpha.com/uploads/2019/8/12/26750043-15656195665233274_origin.jpg",
                "https://www.nasdaq.com/sites/acquia.prod/files/styles/710x400/public/Nvidia-Revenue.png?itok=nN_Nf_DY",
                "https://static.seekingalpha.com/uploads/2017/10/19/47572571-15084276550020583_origin.jpg"
            ],
            "results": [
                {
                    "title": "Explainer-Why are Nvidia's shares soaring and what is its role in the ...",
                    "url": "https://finance.yahoo.com/news/explainer-why-nvidias-shares-soaring-123531645.html",
                    "content": "S&P 500\nDow 30\nNasdaq\nRussell 2000\nCrude Oil\nGold\nSilver\nEUR/USD\n10-Yr Bond\nGBP/USD\nUSD/JPY\nBitcoin USD\nCMC Crypto 200\nFTSE 100\nNikkei 225\nExplainer-Why are Nvidia's shares soaring and what is its role in the AI boom?\n(Reuters) - Chip designer Nvidia closed Tuesday with a trillion-dollar market value for the first time, part of a steady climb in the stock's price in recent months on the back of the artificial intelligence (AI) boom.\n FROM GAMING TO AI: NVIDIA'S FOCUS SHIFT\nNvidia, known for its chips used in videogames, pivoted tothe data center market over the last few years.\n The data center chip business accounted for more than 50% of the company's revenue in the financial year ended Jan. 29.\n The two have raced toadd the technology to their search engines and productivitysoftware as they seek to dominate the industry.\n The company's business rapidly expanded during the pandemicwhen gaming took off, cloud adoption surged and cryptoenthusiasts turned to its chips for mining coins.\n",
                    "score": 0.97373,
                    "raw_content": null
                },
                {
                    "title": "Nvidia Stock Soars After-Hours On 265% Revenue Growth - Forbes",
                    "url": "https://www.forbes.com/sites/petercohan/2024/02/21/nvidia-stock-soars-after-hours-on-265-revenue-growth/",
                    "content": "“We are the lowest-cost solution in the world.”\nNvidia’s Competitive Advantages\nNvidia’s competitive advantages flow from its ability to adapt to new opportunities faster than rivals and a page it took from Apple\nAAPL\n— creating a community of programmers who happily build software to run on your hardware.\n Why Nvidia Leads The AI Chip Race\nNvidia dominates the AI chip market — with 80% to 95% of the AI chip market, according to The Globe and Mail — and has been building competitive advantages for more than 15 years to sustain its leadership position.\n “If the upgrade from the A100 to the H100 is any indication, the Total Cost of Ownership benefit for data center operators will be enticing enough to fuel the upgrade and make 2025 a growth year,” noted analyst Ben Reitzes according to CNBC.\n 10 Fantastic Series Returning To Netflix With New Seasons In 2024\n‘Shadow Of The Erdtree’ Trailer Release Time And Where To Watch — ‘Elden Ring’ DLC Reveal Incoming\nNvidia CEO Jensen Huang described AI as hitting “the tipping point” and indicated demand for the computing power that underlies it remained astronomical. Nvidia’s Differentiation Strategy\nIf a company wants to lead its industry, it must choose one of two strategies:\nAs I wrote last August, Nvidia is a differentiator as evidenced by customers’ willingness to pay a significant price premium and to wait for over a year to obtain its chips.",
                    "score": 0.96296,
                    "raw_content": null
                },
                {
                    "title": "Can Nvidia keep growing this quickly? Here's what Wall Street thinks.",
                    "url": "https://www.marketwatch.com/story/can-nvidia-keep-growing-so-quickly-heres-what-wall-street-thinks-a9e1636e",
                    "content": "While this list will exclude some of the newest or smallest industry players, it provides a reasonable point from which to look at sales estimates for the next few years, because S&P Global’s criteria for initial inclusion in the S&P Small Cap 600 Index includes positive earnings for the most recent quarter and for the sum of the most recent four quarters.\n Follow him on Twitter @PhilipvanDoorn.\nAdvertisement\nAdvertisement\nSearch Results\nAuthors\nSections\nColumns\nSymbols\nPrivate Companies\nRecently Viewed Tickers\nNo Recent Tickers\nVisit a quote page and your recently viewed tickers will be displayed here. In comparison, the forward price-to-earnings ratio for the S&P 500\nSPX\nwas 18.6 and the index’s forward price-to-sales estimate was 2.3 at the close on Tuesday.\n (The S&P 1500 Composite is made up of the S&P 500, the S&P 400 Mid Cap Index\nMID\nand the S&P Small Cap 600 Index\nSML\n).\n Earnings: Nvidia’s stock soars nearly 10% after hours as AI-chip giant reports record results\nTo set the stage, Nvidia reported sales of $13.5 billion for the second quarter of its fiscal 2024, ended July 30, which was an 88% increase from the previous quarter and a 101% increase from a year earlier.",
                    "score": 0.95868,
                    "raw_content": null
                },
                {
                    "title": "Why Nvidia is suddenly one of the most valuable companies in the world",
                    "url": "https://finance.yahoo.com/news/why-nvidia-suddenly-one-most-023006721.html",
                    "content": "S&P 500\nDow 30\nNasdaq\nRussell 2000\nCrude Oil\nGold\nSilver\nEUR/USD\n10-Yr Bond\nGBP/USD\nUSD/JPY\nBitcoin USD\nCMC Crypto 200\nFTSE 100\nNikkei 225\n Why Nvidia is suddenly one of the most valuable companies in the world\nSAN FRANCISCO - You may not have heard about Nvidia, but thanks to the artificial intelligence boom it's now one of the most valuable companies in history.\n This week the company reported earnings and explained the incredible surge in demand it has seen as the tech world races to create new versions of AI - prompting potentially the largest one-day increase in a company's value, ever.\n In a conference call with investors on Wednesday, Nvidia's Chief Financial Officer Colette Kress called ChatGPT's launch the technology's \"iPhone moment,\" marking the point at which the world realized the potential for the new tech.\n Nvidia's stock had already more than doubled this year as the AI boom took off, but the company blew past already-high expectations on Wednesday when it forecast that sales in the second quarter would be $11 billion, compared with the $7 billion that Wall Street analysts had forecast.\n",
                    "score": 0.94231,
                    "raw_content": null
                },
                {
                    "title": "Explainer: Why are Nvidia's shares soaring and what is its ... - Reuters",
                    "url": "https://www.reuters.com/technology/why-are-nvidias-shares-soaring-what-is-its-role-ai-boom-2023-05-25/",
                    "content": "WHAT IS NVIDIA'S ROLE IN THE AI BOOM? The large computers that process data and power generative AI run on powerful chips called graphics processing units (GPUs). Nvidia controls about 80% of the ...",
                    "score": 0.9255,
                    "raw_content": null
                }
            ],
            "response_time": 3.11
        }
        """
        data = request.get_json()
        query = data.get("query")
        search_depth = data.get("search_depth", "basic")
        topic = data.get("topic", "general")
        days = data.get("days", 2)
        max_results = data.get("max_results", 5)
        include_domains = data.get("include_domains", "")
        exclude_domains = data.get("exclude_domains", "")
        include_answer = data.get("include_answer", False)
        include_raw_content = data.get("include_raw_content", False)
        include_images = data.get("include_images", False)
        response = tavily.search(
            query=query,
            search_depth=search_depth,
            topic=topic,
            days=days,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
        )
        print(response)
        return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config_data.get("server", {}).get("port", 8890))
