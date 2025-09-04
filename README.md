# An Iterative and Reflective Framework for Agentic Reasoning with Structured Planning and Dynamic Self-Correction

## 1. Project Overview

Loop is a sophisticated and extensible framework for building autonomous AI agents. It is designed to understand complex user requirements, formulate a strategic plan, execute tasks using a variety of tools, and critically evaluate its own performance to ensure the final output meets the initial goals. The framework is built on a highly modular, entity-based architecture, making it ideal for academic research and advanced AI applications.

The core philosophy of Loop is to create a "closed-loop" system of **research, execution, and reflection**. This is achieved through a multi-layered planning process, a robust verification mechanism, and a unique central data protocol, enabling the agent to autonomously navigate complex problem spaces and learn from its interactions.

### Key Features:

*   **Autonomous End-to-End Workflow:** From requirement analysis to final verification, the entire process is automated.
*   **Multi-layered Planning:** Decomposes complex goals into high-level strategic plans and detailed, executable tasks.
*   **Dynamic Reflection and Replanning:** The agent can verify its progress against user requirements and re-plan its approach if the results are not satisfactory.
*   **Extensible Tool System:** Easily integrate new tools for the agent to use, such as web search, database queries, and API calls.
*   **Modular Entity-based Architecture:** The system is composed of specialized "entities," each responsible for a specific cognitive function (e.g., planning, user profiling, verification). This makes the framework highly maintainable and extensible.
*   **Centralized State Management:** Utilizes a novel **MCP (Memory-Context-Prompt)** protocol for efficient and lightweight state management throughout the agent's lifecycle.

## 2. Core Concepts and Architecture

The architecture of Loop is designed to be modular and scalable, separating the agent's cognitive functions from its execution capabilities.

### 2.1. The MCP (Memory-Context-Prompt) Protocol

The cornerstone of the Loop framework is the **MCP**, a central data object that acts as a "mission briefcase." It is a lightweight, Pydantic-based model that encapsulates all the necessary information for a given task, including:

*   User requirements
*   Strategic plans
*   Sub-goals
*   Executable commands
*   State of completion for each task

The MCP is passed between the different entities in the workflow, ensuring that each component has the context it needs to perform its function without being tightly coupled to the others. This design keeps the prompts sent to the Large Language Model (LLM) concise and relevant, focusing only on the information needed for the current step.

### 2.2. System Architecture

The system is composed of several key components that work together to form the agent's workflow:

*   **Workflow Entry (`AgentWorkflow`):** The main orchestrator that drives the entire process, from receiving the user's request to delivering the final result.
*   **LLM Entities (`BaseLLMEntity`):** These are specialized modules, each powered by an LLM, that perform specific cognitive tasks. The main entities include:
    *   **`QuestionnaireDesigner`**: Analyzes the initial user request and generates clarifying questions to ensure a deep understanding of the user's needs.
    *   **`ProfileDrawer`**: Constructs a detailed user profile based on the initial request and any supplementary information provided.
    *   **`LLMStrategyPlanner`**: Develops a high-level strategic plan to address the user's requirements.
    *   **`LLMTaskPlanner`**: Breaks down the strategic plan into a series of fine-grained, executable commands.
*   **Verification Entities (`BaseVerificationEntity`):** These entities are responsible for quality control and ensuring the agent stays on track.
    *   **`PredictionVerification`**: Assesses the outcome of each individual command to ensure it has executed as expected.
    *   **`RequirementsVerification`**: Performs a final check to confirm that the overall result satisfies all of the user's initial requirements.
*   **Tools (`BaseTool`):** A collection of functions that the agent can use to interact with its environment, such as searching the web or accessing a database.
*   **Tool Executor (`ToolExecutor`):** The component responsible for invoking the tools specified in the executable commands and managing the data they return.
*   **Interfaces:** A set of abstractions for interacting with external services, such as different LLM APIs (`LLMAPIInterface`) and databases (`DatabaseInterface`). This makes it easy to swap out underlying services without changing the core logic of the agent.

## 3. Workflow

The Loop agent operates in a cyclical workflow, divided into four distinct phases:

### Phase 1: User Input Processing

1.  **Requirement Analysis:** The workflow begins when a user submits a request. The `QuestionnaireDesigner` entity analyzes this request to identify any ambiguities or missing information.
2.  **Interactive Clarification:** It then generates a set of questions for the user to answer. This step ensures that the agent has a complete and accurate understanding of the task.
3.  **User Profiling:** The `ProfileDrawer` entity synthesizes the original request and the user's answers into a comprehensive user profile, which is then stored in the MCP.

### Phase 2: Planning

1.  **Strategic Planning:** The `LLMStrategyPlanner` uses the user profile to create a high-level strategic plan, outlining the major steps required to fulfill the request. This plan is added to the MCP.
2.  **Task Planning:** The `LLMTaskPlanner` takes the strategic plan and breaks it down into a list of specific, executable commands. Each command details the tool to be used and the parameters to be passed to it. These commands are also stored in the MCP.

### Phase 3: Execution

1.  **Command Execution:** The `ToolExecutor` iterates through the list of executable commands in the MCP. For each command, it invokes the specified tool with the given parameters.
2.  **Data Handling:** The results of each tool's execution are stored in a temporary `WorkingMemory` and summarized by the `LLMFilterSummary` entity.

### Phase 4: Verification and Reflection

1.  **Tactical Verification:** After each command is executed, the `PredictionVerification` entity checks if the output is consistent with the expected outcome.
2.  **Strategic Verification:** Once all commands have been executed, the `RequirementsVerification` entity assesses whether the collective results fully satisfy the user's original requirements.
3.  **Replanning Loop:** If the verification fails, the agent can clear the existing commands and re-run the planning phase to generate a new set of tasks. This creates a powerful "reflection" loop that allows the agent to correct its own mistakes and adapt its approach.

## 4. Technical Design

This section provides a more detailed look at the technical implementation of the key components in the Loop framework.

### `Data/mcp_models.py`

*   `class MCP(pydantic.BaseModel)`: The central data object that is passed throughout the entire workflow.
*   `class WorkingMemory(pydantic.BaseModel)`: A temporary data store for the outputs of tool executions.
*   `class StrategyPlan(pydantic.BaseModel)`, `class SubGoal(pydantic.BaseModel)`, `class ExecutableCommand(pydantic.BaseModel)`: Pydantic models that define the hierarchical structure of the agent's plan.

### `Interfaces/`

*   `class LLMAPIInterface(abc.ABC)`: An abstract base class for LLM API interactions, with concrete implementations for services like OpenAI, Google Cloud, and Anthropic.
*   `class DatabaseInterface(abc.ABC)`: An abstract base class for database interactions, with a concrete implementation for Redis (`RedisJSONInterface`).

### `Entities/`

*   `class BaseLLMEntity(abc.ABC)`: The base class for all LLM-powered entities.
*   `class BaseVerificationEntity(abc.ABC)`: The base class for all verification entities.

### `Tools/`

*   `class BaseTool(abc.ABC)`: The abstract base class for all tools.
*   `class ToolRegistry`: A class for managing and accessing all available tools.
*   `class ToolExecutor`: The class responsible for executing tools based on the commands in the MCP.

## 5. Getting Started

To get started with the Loop framework, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/loop.git
    cd loop
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up environment variables:**
    *   Create a `.env` file and add your API keys for the LLM and any other services you plan to use.
4.  **Run the workflow:**
    ```bash
    python Workflow_Entry.py
    ```

You can modify the `user_req` in `Workflow_Entry.py` to test the agent with different tasks.

