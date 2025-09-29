

class AgentsGuidancePlugin:
    name = "repo.agents_guidance_present"

    def run(self, paths, ctx):
        return {"status": "ok", "message": "Agents guidance plugin"}
