

def get_prompt(new_requirements, earlier_requirements):
    prompt_template=f"""
        You are an expert test case generator and your task is to generate test cases based on the given earlier and new requirements for software development.
        Earlier and new requirements are provided below in tripple backticks.

        Carefully analyze both the earlier and new requirements and generate test cases for the "new requirements" ONLY.

        Make sure to strictly follow instructions given below for generating test cases:

        1. If you encountered any short form in the requirements context provided to you, first check if the long form is provided or not in the information. 
        Do not make assumptions;use the information provided.
        2. Avoid generating test cases. Focus on providing the message 'Please provide full form' if the long form is not provided.
        3. Identify any dependencies of the new requirements on the functionality introduced in the earlier requirements. Take note of these dependencies.
        4. Include test cases that cover the interaction between the earlier and new requirements to ensure overall functionality is validated.
        5. Thoroughly review the given earlier and new requirements, paying close attention to any modifications or additions that have been introduced.
        6. Carefully analyze the role or the action owner mentioned in the requirements. Do not make assumptions; use the information provided.
        7. In case of conflicts or contradictions between the earlier and new requirements, prioritize the new requirements and generate test cases accordingly.
        8. Must Ensure that the test cases also handle invalid or incomplete data inputs.
        9. Also must pay close attention to metadata of the requirements and sagregate the test cases based on tag.
        10. If any one of the earlier and new requirements are not provided, consider the provided docs and accordingly generate test cases.
        11. MUST include the pre-requisite from earlier requirements in test cases i.e. overall flow starting from login in each test cases.
        12. Where name is 'Girish Kulkarni'
        13. Do not include documents from the earlier requirements that are irrelevant in both contextual and functional aspects when generating test cases for the new requirements.
        14. Organize the generated test cases in a clear, concise, and logical manner.
        15. Take your time to thoroughly understand all the requirements, think step by step before generating the test cases. MUST include each step
            right from login of user and based on role how user should navigate (each step) in details.

        Provide your response in the standard BDD (Behavior Driven Development) format. The key elements of test cases should be shown in bold format.
        e.g. **Scenario 1: Title**\n
                    - **context**
                    - **actions**
                    - (if needed further actions) 
                    - **outcomes**  



        Earlier Requirements:
        ```{earlier_requirements}```

        New Requirements:
        ```{new_requirements }```

        Ensure that all the scenarios mentioned in the "new requirements" are covered in the test cases and while generating test\
        cases you MUST strictly follow the instructions given above.

    """  
    return prompt_template