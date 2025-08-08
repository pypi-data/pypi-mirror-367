from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp_google_mail.app import GoogleMailApp
import anyio
from pprint import pprint

app_instance = GoogleMailApp(integration=None)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.send_email)
print(tool_manager.list_tools(format="openai"))



    
  

