# VibeMovie

Your task is creating a simple python web application for listing and giving a text and star based review (0 - 5 stars). movies, ratings and comments should be stored in an azure cosmos db database running on the local emulator on my pc.  

<Goals>
the focus on this is less the output and more the tooling that went into creating it.  

in this case, we're using:

-  Visual Studio Code
-  GitHub Copilot Agent mode - gpt-5 model (preview)Azure Cosmos DB vNext Linux emulator - 
docs: https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux
-  Azure Cosmos DB VS Code extension
</Goals>

<Limitations>
- This will be for a conference talk, so it's important that steps be simple. 
</Limitations>

# VibeMovie

Your task is to create a simple Python web application for listing movies and giving a text and star-based review (0–5 stars). Movies, ratings, and comments should be stored in an Azure Cosmos DB database running on the local emulator on my PC.

<Goals>
The focus is less on the output and more on the tooling used to create it.

In this case, we're using:

- Visual Studio Code
- GitHub Copilot Agent mode — gpt-5 model (preview)
- Azure Cosmos DB vNext Linux emulator (docs: https://learn.microsoft.com/en-us/azure/cosmos-db/emulator-linux)
- Azure Cosmos DB VS Code extension
</Goals>

<Limitations>
- This will be for a conference talk, so steps must be simple.
</Limitations>

<WhatToAdd>

<HighLevelDetails>

- Use Flask as the framework.
- Create containers in the database for movie name, ratings, and comments.
</HighLevelDetails>

<BuildInstructions>

- For each of bootstrap, build, test, run, lint, and any other scripted step, document the sequence of steps to take to run it successfully as well as the versions of any runtime or build tools used.
- Each command should be validated by running it to ensure that it works correctly, including any preconditions and postconditions.
- Try cleaning the repo and environment and running commands in different orders; document errors and misbehavior observed, as well as any steps used to mitigate the problem.
- Run the tests and document the order of steps required to run the tests.
- Make a change to the codebase. Document any unexpected build issues as well as the workarounds.
- Document environment setup steps that seem optional but that you have validated are actually required.
- Document the time required for commands that failed due to timing out.
- When you find a sequence of commands that work for a particular purpose, document them in detail.
- Use language to indicate when something should always be done. For example: "always run npm install before building".
- Record any validation steps from documentation.
</BuildInstructions>

List key facts about the layout and architecture of the codebase to help the agent find where to make changes with minimal searching.

<ProjectLayout>

- A description of the major architectural elements of the project, including the relative paths to the main project files and the location of configuration files for linting, compilation, testing, and preferences.
- A description of the checks run prior to check-in, including any GitHub workflows, continuous integration builds, or other validation pipelines.
- Document the steps so that the agent can replicate these itself.
- Any explicit validation steps that the agent can consider to have further confidence in its changes.
- Dependencies that aren't obvious from the layout or file structure.
- Finally, fill in any remaining space with detailed lists of the following, in order of priority:
   - The list of files in the repo root.
   - The contents of the README.
   - The contents of any key source files.
   - The list of files in the next level down of directories, giving priority to the more structurally important files.
   - Snippets of code from key source files, such as the one containing the main method.
</ProjectLayout>
</WhatToAdd>

<StepsToFollow>
- Perform a comprehensive inventory of the codebase. Search for and view:
   - README.md, CONTRIBUTING.md, and all other documentation files.
   - Build steps and indications of workarounds like "HACK", "TODO", etc.
   - All scripts, particularly those pertaining to build and repo or environment setup.
   - All build and actions pipelines.
   - All project files.
   - All configuration and linting files.
- For each file:
   - Think: are the contents or the existence of the file information that the coding agent will need to implement, build, test, validate, or demo a code change?
   - If yes:
      - Document the command or information in detail.
      - Explicitly indicate which commands work and which do not and the order in which commands should be run.
      - Document any errors encountered as well as the steps taken to work around them.
- Document any other steps or information that the agent can use to reduce time spent exploring or trying and failing to run shell commands.
- Finally, explicitly instruct the agent to trust the instructions and only perform a search if the information in the instructions is incomplete or found to be in error.
</StepsToFollow>