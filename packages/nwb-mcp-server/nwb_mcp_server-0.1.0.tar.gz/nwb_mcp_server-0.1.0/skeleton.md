# Talk to your data: agentic workflows for analyzing NWB data 

## state of the art
    - LLMs arguably better at writing generic code than humans
    - not so good when you have a very specific idea of how the code should be written (style,
      architecture, etc.)
        - better at starting from scratch, using common patterns, and focussing on delivering a
          result 
    - not good at generating truly novel ideas/hypotheses

    - goal: user asks for a report on X, agent delivers a report with summary,
      figures, tables, statistics, etc.
      - no guidance on how to do it (code style etc.), or the structure of the data, just high-level instructions

> if this works, imagine what it could look like
## sci-fi picture:
    - user can throw out a hypothesis in natural language (in Teams, say)
    - "agent farm" can execute many analyses in parallel, 24/7 in the cloud
        - they're fast, expert users of all the tools and techniques, they don't get tired
        - they're not very creative and not at all curious or ambitious!
    - explore unfamiliar datasets easily
    - can use voice alone (think users with no coding experience, or with disabilities)

> how close are we to this?
mention existing NWB efforts
## implementation
    - MCP server: provides agent with access to local or cloud NWB data and guides their actions
    - agent: plans, executes, debugs, iterates, delivers

    - mcp server uses lazynwb to scan a folder of NWB files, creating a virtual database of tables with efficient data access
    - mcp server provides functions for agent to get table names, schemas, preview values
        * this is the crux of the implementation: provides an easy way for LLM to interrogate the structure of the data 
    - prompts provided by mcp server guide agent behavior, rules etc.
    - (no-code mode only) mcp server executes SQL queries against the virtual database returning
      summary statistic (mean, std, min, max etc. for basic analyses without pre-processing; cannot produce visualizations)


> how does it work in practice (for a user)?
## workflows
    (videos or live demos)
    - add server config (NWB dir path, options) to json file
    - open Copilot Chat
    - customize the provided prompt to ask for a particular analysis

    - no-code not allowed to write code: provides a text report in the chat dialog
    - code mode generates Python files or notebooks that it runs
    - unattended mode tries to do everything without user interaction


> three analysis questions of varying complexity
## results 
    - time taken vs humans to produce a report (same prompt)
    - accuracy of report
    - quality, depth of analysis
    - how much guidance was needed
    - cost of running the agent


## observations
    - no info on experiment or metadata provided
    - some models not good at using the MCP server (o4 mini)
    - NWB files were well-structured, with good names of tables and columns, and consistency
      across files
    - NWB files are not ideally suited in general (no schema, poor read performance)
        ! we can actually make it work for any set of tabular data if filenames are descriptive

    - results are sensitive to the prompt and the instructions embedded in server
    - requirement of chatbot UI prevents headless mode required for "agent farm": Claude Code in terminal could be the solution
    - need to design context around API usage/cost
        - Copilot plan now has limited premium requests per month on the best models (Claude Sonnet)
        - session limits will restrict number of iterations

> poorly implemented, the agent "aims to please" and may cherry-pick, misrepresent, fabricate data
## how do we build trust in the results?
    - run multiple times, or with different models and generate a consensus?
    - manually check the output? (somewhat defeats the point)
    - get agent to write tests that demonstrate correctness of small building blocks
    - generate synthetic data with a known relationship, insert into the same NWB file structure then test agent's work on the test data


## conclusion
    - just a proof of concept, but it seems the goal is achievable (it's actually amazing, it just becomes "normal" very quickly)
    - completely autonomous analysis should be possible, but likely needs very detailed instructions with minimal ambiguity
    - I've primarily been developing the tool, not using it day-to-day for actual science:
        - encourage people to try it out and get a feel for the limitations
    - agents/MCP have an age measured in weeks/months and will only get better

    