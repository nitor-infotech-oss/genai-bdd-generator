prompt_template=f"""
        You are an expert test case generator and your task is to generate test cases based on the given earlier and new requirements for software development.
        Earlier and new requirements are provided below in tripple backticks.

        Carefully analyze both the earlier and new requirements and generate test cases for the "new requirements" ONLY.
        Keep your answers technical and based on facts – do not hallucinate features.

        Make sure to strictly follow instructions given below for generating test cases:

        1. If you encountered any short form in the requirements context provided to you, first check if the long form is provided or not in the information. 
            If long form not provided then do not generate test cases and ask the user to provide full form'.
        3. Identify any dependencies of the new requirements on the functionality introduced in the earlier requirements. Take note of these dependencies.
        4. Include test cases that cover the interaction between the earlier and new requirements to ensure overall functionality is validated.
        5. Thoroughly review the given earlier and new requirements, paying close attention to any modifications or additions that have been introduced.
        6. Carefully analyze the role or the action owner mentioned in the requirements. Do not make assumptions; use the information provided.
        7. In case of conflicts or contradictions between the earlier and new requirements, prioritize the new requirements and generate test cases accordingly.
        8. Must Ensure that the test cases also handle invalid or incomplete data inputs.
        9. Also must pay close attention to metadata of the requirements and sagregate the test cases based on tag.
        10. If any one of the earlier and new requirements are not provided, consider the provided docs and accordingly generate test cases.
        11. MUST include the pre-requisite from earlier requirements in test cases i.e. overall flow starting from login in each test cases.
        12. Do not include documents from the earlier requirements that are irrelevant in both contextual and functional aspects when generating test cases for the new requirements.
        13. Organize the generated test cases in a clear, concise, and logical manner.
        14. Take your time to thoroughly understand all the requirements, think step by step before generating the test cases. MUST include each step
            right from login of user and based on role how user should navigate (each step) in details.

        Provide your response in the standard BDD (Behavior Driven Development) format. The key elements of test cases should be shown in bold format.
        e.g. Scenario 1: Title (in bold)
                    - **context**
                    - **actions**
                    - (if needed further actions) 
                    - **outcomes**  



        Earlier Requirements:
        ```%s```

        New Requirements:
        ```%s```

        Ensure that all the scenarios mentioned in the "new requirements" are covered in the test cases and while generating test\
        cases you MUST strictly follow the instructions given above.

    """

questions =[
    """
 Age Verification for Restricted Products
 1. The system should support the configuration of age restrictions for specific products or services.
 2. The admin user should have the ability to set the minimum age requirement for each restricted product/service based on the LDA settings.
 3. If a user's age does not meet the minimum age requirement for a specific product/service, they should be prevented from accessing or purchasing that product/service.
 4. The system should provide an option for users to provide additional age verification documents 

""",

"""
User should be able to login using username and password. Once user logged in successfully user should be redirected to home page where all the products will be visible to user with add to cart option.
Once user login to application with remember me checkbox as ticked. User login should be persisted for next 10 days from them unless user logged out manually.

""",
"""
1. The system must support only single-user authentication.
2. Data storage should be in a flat file format.
3. User interface should be text-based and command-line driven.
""",
"""
Login
"""
]

KEY_FEATURES = """
            🤖 Intelligent Test Case Generation

            ⏰ Time Efficiency

            🎯 Thorough Test Coverage

            🚀 Increased Accuracy
"""

AZURE_QUERY = f"""
                    select [System.Id],
                        [System.WorkItemType],
                        [System.Title],
                        [System.AreaPath],
                        [System.State],
                        [System.Description],
                        [System.Tags]
                    from WorkItems
                    where [System.WorkItemType] = 'User Story' 
                    and [System.AreaPath] = 'Dooze App'
                    and [System.TeamProject] = 'Dooze App'
                    order by [System.ChangedDate] desc"""

SIMILARITY_THRESHOLD = 0.90

new_prompt_template = f"""
        You have the expertise to generate test cases based on given earlier and new software development requirements.
        Earlier and new requirements are provided below in tripple backticks.

        Your task is to analyze the new requirements (and earlier requirements if given), following specific instructions below:

        1. Check for abbreviations, short forms, or clipped terms, and only proceed if the corresponding full forms are provided in the information.
        2. Request clarification on the full form of words only when the earlier or new requirements do not provide them.
        3. Identify dependencies of the new requirements on earlier functionalities.
        4. Develop test cases covering the interaction between earlier and new requirements for comprehensive validation.
        5. Thoroughly review both earlier and new requirements, focusing on modifications or additions.
        6. Analyze the roles or action owners mentioned in the requirements without making assumptions.
        7. In case of conflicts, prioritize the new requirements for test case generation.
        8. Ensure test cases handle invalid or incomplete data inputs.
        9. Generate test cases considering the absence of either earlier or new requirements.
        10. MUST include each step right from login of user and based on role how user should navigate (each step) in details in Actions.
        11. Exclude irrelevant documents from earlier requirements when creating test cases for new requirements.
        13. Take time to understand all requirements, thinking step by step before generating test cases.
        14. Provide your response in the standard BDD (Behavior Driven Development) format provided below in case of valid test case generation:
            e.g. Scenario x: Scenario Heading (in bold) with below sections starting with hyphen for each scenario
                        - **Context**
                            -
                        - **Actions**
                            -
                        - (if needed further actions) 
                        - **Outcomes** 
                            -

        Earlier Requirements:
        ```%s```

        New Requirements:
        ```%s```
        
        Only request clarification on the full form of words when the earlier or new requirements do not provide them.
        Ensure that all the scenarios mentioned in the "new requirements" are covered in the test casesand generate atleast 15 test cases.
    """
# Ask for full form clarification of words which require full form only if not provided in the information.
# Request clarification on the full form of words only when the earlier or new requirements do not provide them. 