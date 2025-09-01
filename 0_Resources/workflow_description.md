Complete System Workflow Description:

1. System Initialization
    1.1 Initialize LLM_Interface interface
    1.2 Initialize db_interface interface
    1.3 Initialize data classes such as mcp, working_memory, strategies, etc.
    1.4 Initialize questionnaire_designer, profile_drawer, strategy_planner and task_planner
    1.5 Initialize tool_registry, register currently available tools, get a registry but don't instantiate tools

2. Receive user's original input
3. User's original input is transmitted to questionnaire_designer, which generates potential questions based on the original input and requests user supplementation
4. The supplemented results are transmitted to profile_drawer, which analyzes user profiles based on the content and stores user original input + questionnaire supplementary content + user profile analysis results in the completion_requirement object of mcp
5. User information input is completed so far, start entering nested dual loops

6. strategy_planner reads completion_requirement information in mcp and cognition strategy information, then generates several strategic plans based on the current stage
    6.1 Role of strategic plans: For the information I currently know, what information do I need to query to help me further advance the task. It is strategic-level planning and content-oriented (What)
    6.2 Output to mcp's strategy_plans object according to specified format requirements

7. task_planner reads strategy_plans and execution_policy strategy information in mcp, then performs the following actions based on current stage information:
    7.1 Read tool_registry registry to know what tools are currently available
    7.2 Read strategy_plan one by one, combine with tool registry, break it down into several implementation-oriented (How) subgoals, these subgoals are how to obtain what strategy_plan wants to know, which tool to use to obtain
    7.3 Output subgoals to mcp's sub_goals object
    7.4 Based on sub_goals object, convert each subgoal into an executable_command that can be directly executed
    7.5 According to the format specification of the given executable_command, check whether the generated json object meets format requirements, if qualified, write it back to mcp's executable_commands object
    7.5 Instantiate an executor and start the execution phase


8. executor reads information from executable_commands object in mcp, then performs the following actions as required
    8.1 Instantiate corresponding tools from the registry, instantiate a redisclient object
    8.2 Pass executable_command parameters to corresponding tool instances, then wait for specific tool instances to return
    8.3 Package information returned by each specific tool instance in specified format and output to working_memory for recording

9. Specific tool implementation methods are not discussed for now
10. After executor executes all executable_commands, all tool return raw results will be stored in working_memory object. Then start the verification phase

11. First inner_verification will be instantiated, it first reads working_memory and sub_goals object in mcp and performs the following actions
    11.1 First this inner_verification is an LLM entity, it will browse and judge whether the content in working_memory meets the requirements of sub_goals
    11.2 If one is satisfied, mark it as status 1, and keep these status 1 data unchanged
    11.3 If requirements are not met, mark as status 0, then evaluate why the subgoal requirements were not met, generate a possible reason and improvement method, then output to execution_policy
    11.4 task_planner will re-receive these status 0 data items and re-plan according to execution_policy improvement requirements, then call executor to re-execute
    11.5 Until all sub_goals are satisfied, all data items have status 1, it will end this part of the inner loop.

12. This involves the mechanism of how inner_verification evaluates whether a data item is qualified. This mechanism must effectively help filter unqualified data items and be helpful for advancing subsequent work
13. Now the content in working_memory object is the result that meets all requirements, because inner_verification has already removed those unqualified results and replaced them with new qualified data through re-planning and re-execution

13. Then outer_verification will be instantiated, it will read the current working_memory object and cognition strategy object and perform the following actions:
    13.1 First it will evaluate whether the current content in working_memory meets the requirements of strategy_plans according to a mechanism, then it will summarize what deficiencies exist in the current data and store them in a data class object within itself
    13.2 Then it will review what new problems were generated in the data obtained in this cycle, then it will output to cognition strategy according to these evaluations to guide what should be done in the next cycle, what new content to query
    13.3 The cognition strategy object will include but not be limited to: current cycle deficiencies and limitations, new content that needs to be queried discovered in existing data and other information
    13.4 Then this cognition strategy object will be updated to guide strategy_planner to plan tasks for the next cycle
    13.5 Then here will store all current cycle information such as mcp, working_memory in json format in cycle_history object for persistent retention, then clear all non-global data classes, prepare to start the next outer loop
    13.6 There also needs to be a threshold mechanism to judge when the information is sufficient enough to well meet the requirements of completion_requirement, terminate the outer loop

14. After threshold terminates the outer loop, instantiate an LLM Analyzer to read the entire cycle_history record, then organize a complete reply information from it, then output to the user to complete this task