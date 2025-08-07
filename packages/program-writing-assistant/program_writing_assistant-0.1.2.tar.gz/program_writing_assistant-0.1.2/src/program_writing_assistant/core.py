'''
Author: 823042332@qq.com 823042332@qq.com
Date: 2025-08-07 17:25:12
LastEditors: 823042332@qq.com 823042332@qq.com
LastEditTime: 2025-08-07 17:48:48
FilePath: /program_writing_assistant/src/program_writing_assistant/core.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''


system_prompt = """
你是一个资深Python工程师，具备卓越的代码审查和优化能力。
我将为你提供一段现有Python源码。你的核心任务是基于这段源码进行修改，以实现我提出的功能需求。
请你绝对严格地遵循以下原则：
 极端最小化修改原则（核心）：
 在满足所有功能需求的前提下，只进行我明确要求的修改。
 即使你认为有更“优化”、“合理”或“简洁”的改动方式，只要我没有明确要求，也绝不允许进行任何未经指令的修改。
 优先考虑在现有行上直接修改或在极近的位置添加/删除，而不是改变代码的逻辑结构（如拆分if条件，除非明确要求）。
 目的就是尽可能地保留原有代码的字符不变，除非功能要求必须改变。
 严格遵循我的指令：
 你必须精确地执行我提出的所有具体任务和要求。
 绝不允许自行添加任何超出指令范围的功能、代码、重构、优化或注释。
 保持原有代码风格和结构：
 尽可能地与现有源码的缩进、命名约定和总体代码结构保持一致。
 不要改变不相关的代码行或其格式。
 只提供修改后的代码：
 直接输出修改后的完整Python代码。
 不要包含任何解释、说明或额外对话。
 在你开始之前，请务必确认你已理解并能绝对严格地遵守这些原则。任何未经明确指令的改动都将视为未能完成任务。

源码:
{source_code}

功能需求:
{function_requirement}
"""


from llmada.core import BianXieAdapter

import re

def extract_python_code(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```python([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        return ""  # 返回空字符串或抛出异常，此处返回空字符串



class EditCode:
    def __init__(self,py_path):
        self.py_path = py_path
        self.bx = BianXieAdapter()
        model_name = "gemini-2.5-flash-preview-05-20-nothinking"
        self.bx.model_pool.append(model_name)
        self.bx.set_model(model_name=model_name)


    def edit(self,function_requirement:str):
        # 最小改动代码原则
        with open(self.py_path,'r') as f:
            code = f.read()
        prompt = system_prompt.format(source_code=code,function_requirement=function_requirement)

        response = self.bx.product(prompt)
        response = extract_python_code(response)
        with open(self.py_path,'w') as f:
            f.write(response)
        print(f"代码已保存到{self.py_path}")
        # TODO 最好要git push一下
