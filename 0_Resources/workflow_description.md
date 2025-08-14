系统工作流完整描述：

1. 系统初始化
    1.1 初始化LLM_nterface接口
    1.2 初始化db_interface接口
    1.3 初始化mcp、working_memory、strategies等等数据类
    1.4 初始化questionnaire_designer、profile_drawer、strategy_planner和task_planner
    1.5 初始化tool_registry，注册当前已有的各个工具，获取一个注册表，但不实例化工具

2. 接收用户原始输入
3. 用户原始输入传输给questionnaire_designer，其根据原始输入生成潜在问题然后请求用户补充
4. 补充完成的结果传输给profile_drawer，它会根据内容分析用户画像，并将 用户原始输入 + questionnaire补充内容 + 用户画像分析结果 存储在mcp的completion_requirement对象中
5. 到目前为止用户信息输入完成，开始进入嵌套双重循环

6. strategy_planner读取mcp中的completion_requirement信息 和 cognition策略信息，然后根据当前阶段来生成若干条战略计划
    6.1 战略计划的作用：对于当前我已知的信息来说，我需要查询什么信息来帮助我进一步推进任务。它是战略级规划，也是内容导向的(What)
    6.2 按照规定格式要求输出到mcp的strategy_plans对象中

7. task_planner读取mcp中的strategy_plans和execution_policy策略信息，然后根据当前阶段的信息做以下动作：
    7.1 读取tool_registry注册表，知道当前有哪些可用工具
    7.2 逐条读取strategy_plan，结合工具注册表，将其拆分为若干个实现方式导向的(How) subgoals，这些subgoals就是怎么样获取strategy_plan想知道的东西，用哪个工具获取
    7.3 输出subgoals到mcp的sub_goals对象中
    7.4 根据sub_goals对象，将里面每一条subgoal都转换为一个可以直接执行的executable_command
    7.5 根据给定的executable_command的格式规范，检查生成出来的json对象是否符合格式要求，如果合格就将其写回mcp的executable_commands对象中
    7.5 实例化一个executor，开始execution阶段


8. executor读取mcp中executable_commands对象的信息，然后按照要求做以下动作
    8.1 从注册表中实例化对应的工具，实例化一个redisclient对象
    8.2 将executable_command的参数传递给对应的工具实例中，然后等待具体的工具实例回传
    8.3 将每一个具体的工具实例回传的信息，包装为规定格式，输出到working_memory中记录

9. 具体的工具实现方式暂不讨论
10. 当executor执行完全部的executable_commands之后，所有的工具返回原始结果都会存储在working_memory对象中。然后开始verification阶段

11. 首先inner_verification将会被实例化，它首先读取working_memory和mcp中的sub_goals对象并且执行以下动作
    11.1 首先这个inner_verification是一个LLM实体，它会逐条浏览并判断working_memory中的内容是否满足了sub_goals的要求
    11.2 如果某一条满足了，就标注为状态1，并且保持这些状态1的数据不动
    11.3 如果要求未满足则标注为状态0，然后评估为什么没能满足subgoal的要求，生成一个可能的原因以及改进方法，然后输出到execution_policy中
    11.4 task_planner将会重新接收这些状态0的数据项，并且根据execution_policy的改进要求来重新规划，然后调用executor来重新执行
    11.5 直到所有的sub_goals全部都被满足，所有数据项状态都为1，它就会结束这一部份的内循环。

12. 这里涉及了inner_verification是如何评估一条数据项是否合格的机制，这个机制必须有效帮助筛选不合格数据项，并且对推进后续的工作有帮助
13. 现在working_memory对象中的内容就是全部满足要求的结果了，因为inner_verification已经剔除掉了那些不合格的结果并且通过重新规划和重新执行，用新的合格数据替换了它们

13. 接着outer_verification将会被实例化，它将会读取现在的working_memory对象以及cognition策略对象并且执行以下动作：
    13.1 首先它会根据一个机制评估现在的working_memory中的内容是否满足了strategy_plans的要求，然后它会总结现在有的数据还有哪些不足之处，存储在它自己内部的一个数据类对象中
    13.2 然后它会审阅这一次循环轮次所获取的数据中产生了哪些新的问题，然后它会根据这些评估输出到cognition策略中来指导下一循环应该做什么，查询什么新的内容
    13.3 cognition策略对象中将会包括但不局限于：当前轮次的不足和局限性、现有数据中发现的新的需要查询的内容等信息
    13.4 然后这个cognition策略对象将会被更新，用于指导strategy_planner来规划下一次循环的任务
    13.5 然后这里将会把mcp、working_memory等所有当前循环轮次的信息按照json格式存储在cycle_history对象中，做持久化保留，然后清空所有非全局数据类，准备开始下一次的外循环
    13.6 这里还需要有一个threshold机制，判断什么时候信息已经足够多了，可以很好地满足completion_requirement的要求的时候，终止外循环

14. 当threshold终止外循环之后，实例化一个LLM的Analyzer来读取整个cycle_history记录，然后从中整理出一份完整的回复信息，然后输出给用户，完成本次任务

