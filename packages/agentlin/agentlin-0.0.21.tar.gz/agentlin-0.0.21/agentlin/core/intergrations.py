import os


def init_agentops(AGENTOPS_API_KEY=os.getenv("AGENTOPS_API_KEY"), **kwargs):
    """
    https://app.agentops.ai/get-started
    
    Initialize AgentOps with the API key from environment variables.
    Raises ValueError if AGENTOPS_API_KEY is not set.
    """
    if not AGENTOPS_API_KEY:
        raise ValueError("AGENTOPS_API_KEY is not set. Please set it in your environment variables.")
    import agentops

    agentops.init(
        api_key=AGENTOPS_API_KEY,
        default_tags=["AgentLin"],
        **kwargs,
    )
