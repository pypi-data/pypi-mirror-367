import requests
from typing import List, Dict, Union
from langchain.agents import Tool
import jsonschema
from jsonschema import ValidationError


class MeshSDK:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required and cannot be empty")
        self.api_key = api_key
        self.mesh_url = "https://d2rg0qhl0argzt.cloudfront.net"
        # self.mesh_url = "https://f6a97ab0c30b.ngrok-free.app/agent-mesh-api"
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def list_agents(self) -> List[Dict]:
        """Fetch all available agents."""
        response = requests.get(f"{self.mesh_url}/public/agents", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def call_agent(self, agent_id: str, inputs: Union[str, Dict], validate_inputs: bool = True) -> Dict:
        """Invoke a Mesh agent with given inputs, optionally validating them."""
        if validate_inputs and isinstance(inputs, dict):
            self._validate_agent_inputs(agent_id, inputs)

        payload = {
            "agentId": agent_id,
            "inputs": inputs
        }

        print(f"DEBUG: Sending to API: {payload}")
        response = requests.post(f"{self.mesh_url}/gateway/call", headers=self.headers, json=payload)
        print(f"DEBUG: API response status: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: API error response: {response.text}")
        response.raise_for_status()

        return response.json().get("data", {})

    def _validate_agent_inputs(self, agent_id: str, inputs: Dict) -> None:
        """Validate input dictionary against agent's input schema if present."""
        agents = self.list_agents()
        agent = next((a for a in agents if a["id"] == agent_id), None)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        schema = agent.get("inputSchema")
        if schema:
            try:
                jsonschema.validate(instance=inputs, schema=schema)
            except ValidationError as e:
                raise ValueError(f"Invalid inputs for agent {agent_id}: {e.message}")

    def _format_schema_description(self, agent: Dict) -> str:
        """Generate a tool description with parameter info from schema."""
        description = agent.get("description", "")
        schema = agent.get("inputSchema", {})
        if schema and "properties" in schema:
            required = schema.get("required", [])
            param_descriptions = [
                f"{name}: {prop.get('type', 'any')}{' (required)' if name in required else ' (optional)'}"
                for name, prop in schema["properties"].items()
            ]
            description += f"\n\nParameters: {', '.join(param_descriptions)}"
        elif "exampleInputs" in agent:
            description += f"\n\nExample inputs: {agent['exampleInputs']}"
        return description

    def to_langchain_tools(self) -> List[Tool]:
        """Wrap Mesh agents as LangChain tools."""
        tools = []
        agents = self.list_agents()

        for agent in agents:
            agent_id = agent["id"]
            name = agent["name"].replace(" ", "_")
            description = self._format_schema_description(agent)
            schema = agent.get("inputSchema")

            def make_tool_func(aid=agent_id, input_schema=schema):
                def tool_fn(query=None, **kwargs):
                    # If only a query is passed and nothing else, use it as raw string input
                    if query is not None and not kwargs:
                        inputs = query
                    else:
                        inputs = dict(kwargs)
                        if query is not None:
                            inputs["query"] = query

                    if isinstance(inputs, dict) and input_schema:
                        try:
                            jsonschema.validate(instance=inputs, schema=input_schema)
                        except ValidationError as e:
                            raise ValueError(f"Invalid inputs: {e.message}")

                    return self.call_agent(aid, inputs, validate_inputs=False)
                return tool_fn

            tools.append(Tool(
                name=name,
                func=make_tool_func(),
                description=description
            ))

        return tools