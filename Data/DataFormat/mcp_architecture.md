current_strategy_plan = {
    "sp1" : "我想知道有哪些保守的投资策略",
    "sp2" : "我想知道股票投资的须知知识点",
    "sp3" : "我想知道德国某个具体券商的开户的方法和具体操作"
}

current_subgoal = {
    "sg1" : {"sp1" : "保守的投资策略有哪些"},
    "sg2" : {"sp1" : "它们亏钱的可能性为什么相对比较小，原理是什么"},
    "sg3" : {"sp2" : "股票投资相关的宏观经济学知识有哪些"},
    "sg4" : {"sp2" : "股票投资相关的微观经济学知识有哪些"},
    "sg5" : {"sp3" : "德国有哪些大型券商"},
    "sg6" : {"sp3" : "某一个具体券商的开户流程是什么"}
}

executable_command = {
    {
        "tools": [
            {
                "tool": "web_search",
                "params": {
                    "entries": [
                        {
                            “ec1” : "sg1",
                            "keywords": [
                                "保守",
                                "投资策略"
                            ],
                            "num_results": 5
                        },
                        {
                            “ec2” : "sg2",      
                            "keywords": [
                                "保守投资策略",
                                "亏损",
                                "最小化"
                            ],
                            "num_results": 5
                        },
                        {
                            “ec3” : "sg3",
                            "keywords": [
                                "股票投资",
                                "宏观经济学",
                                "知识"
                            ],
                            "num_results": 6
                        },
                        {
                            “ec4” : "sg4",
                            "keywords": [
                                "股票投资",
                                "微观经济学",
                                "知识"
                            ],
                            "num_results": 6
                        },
                        {
                            “ec5” : "sg5",
                            "keywords": [
                                "德国",
                                "大型可靠券商",
                            ],
                            "num_results": 2
                        },
                        {
                            “ec6” : "sg6",
                            "keywords": [
                                "德国券商",
                                "开户流程",
                            ],
                            "num_results": 2
                        },
                    ]
                }
            }
        ]
    }
}