import os
import re
import json
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import openai
from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

# 加载 .env 文件
load_dotenv()

def read_prompt(prompt_file: str, replacements: Dict[str, str]) -> str:
    """
    读取提示文件并替换占位符
    """
    with open(prompt_file, 'r', encoding='utf-8') as file:
        prompt = file.read()
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{key}}}", value)
    return prompt

class PuyuAPIClient:
    """处理与AI API的所有交互。"""

    def __init__(self, api_key, base_url, model_name):
        """初始化APIClient。"""
        api_key = os.getenv("PUYU_API_KEY")
        base_url = os.getenv("PUYU_BASE_URL")
        model_name = os.getenv("PUYU_MODEL_NAME")
        self.api_key = api_key
        self.api_url = base_url
        self.model_name = model_name

    def call_api(self, messages: List[Dict[str, str]], max_tokens: int = 4096) -> str:
        """调用AI API并返回生成的文本。

        Args:
            messages: 要发送给API的消息列表。
            max_tokens: 响应中的最大标记数。

        Returns:
            API返回的生成文本。

        Raises:
            requests.RequestException: 如果API调用失败。
        """
        client = openai.OpenAI(api_key=self.api_key, base_url=self.api_url)

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.7,
                frequency_penalty=0.5,
                n=1
            )

            for choice in response.choices:
                return choice.message.content.strip()

        except openai.OpenAIError as e:
            print(f"API调用失败: {e}")
            raise

def convert_latex_to_markdown(text):
    # 使用正则表达式替换公式开始和结束的 \[ 和 \]，但不替换公式内部的
    pattern = r'(?<!\\)\\\[((?:\\.|[^\\\]])*?)(?<!\\)\\\]'
    return re.sub(pattern, r'$$\1$$', text)


class BookWriter:
    """管理剧本杀生成过程的主类。"""

    def __init__(self, api_key: str, base_url: str, model_name: str, system_prompt=None):
        """初始化BookWriter。"""
        # 使用openai的接口调用书生浦语模型

        self.api_key = os.getenv("API_KEY") if api_key is None else api_key
        self.base_url = os.getenv("BASE_URL") if base_url is None else base_url
        self.model_name = os.getenv("MODEL_NAME") if model_name is None else model_name

        if system_prompt is None:
            system_prompt = "你是一个专业的剧本杀剧本写作助手，正在帮助用户写一本剧本杀剧本。"
        self.assistant = self.create_assistant(self.model_name, self.api_key, self.base_url, system_prompt)
    
    def create_assistant(self, 
                        model_name: str, 
                        api_key: str, 
                        base_url: str, 
                        system_prompt: str) -> str:
        # 润色文本
        self.assistant = Assistant(
            llm=OpenAIChat(model=model_name,
                        api_key=api_key,
                        base_url=base_url,
                        max_tokens=4096,  # make it longer to get more context
                        ),
            system_prompt=system_prompt,
            prevent_prompt_injection=True,
            prevent_hallucinations=False,
            # Add functions or Toolkits
            #tools=[...],
            # Show tool calls in LLM response.
            # show_tool_calls=True
        )
        return self.assistant

    def generate_title_and_intro(self, book_theme, prompt_file = "prompts/script_info_writer.txt") -> Tuple[str, str]:
        """生成剧本杀剧本标题和主要内容介绍等。

        Args:
            prompt: 用于生成标题和介绍的提示。

        Returns:
            包含生成的标题和介绍的元组。
        """
        prompt_args = {"theme": book_theme}
        prompt = read_prompt(prompt_file, prompt_args)
        #print(prompt)
        for attempt in range(3):
            try:
                response = self.assistant.run(prompt, stream=False)
                # convert to json
                response = response.strip()
                if not response.startswith('{'):
                    response = '{' + response.split('{', 1)[1]
                if not response.endswith('}'):
                    response = response.split('}', 1)[0] + '}'

                book_title_and_intro = json.loads(response)

                #print(book_title_and_intro)

                return book_title_and_intro
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        return response

    def generate_outline(self, book_theme, book_title_and_intro: str, prompt_file= "prompts/character_outline_writer.txt") -> List[str]:
        """生成角色大纲。

        Args:
            prompt: 用于生成角色的提示。
            title: 剧本杀标题。
            intro: 剧本杀剧本介绍。

        Returns:
            人物简介列表列表。
        """
        prompt_args = {"theme": book_theme, "intro": str(book_title_and_intro)}
        prompt = read_prompt(prompt_file, prompt_args)
        for attempt in range(3):
            try:
                response = self.assistant.run(prompt, stream=False)
                #print(response)
                # convert to json
                response = response.strip()
                if not response.startswith('['):
                    response = '[' + response.split('[', 1)[1]
                if not response.endswith(']'):
                    response = response.split(']', 1)[0] + ']'
                chapters = json.loads(response.strip())
                #print(chapters)
                return chapters
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        return response

    def clean_json_response(self, response: str) -> str:
        """ 清理JSON格式，转换为人类易读的文本。 """
        # 假设已经解析JSON数据并转换为Python字典
        data = json.loads(response)
        
        # 提取有用信息
        book_title = data.get("intro", {}).get("title", "未定标题")
        book_intro = data.get("intro", {}).get("intro", "未提供简介")
        character_name = data.get("character", "未知角色")
        character_age = data.get("age", "未知年龄")
        character_profession = data.get("profession", "未知职业")
        character_secrets = data.get("secrets", {})
        
        # 拼接人类可读格式
        formatted_response = f"书名：{book_title}\n简介：{book_intro}\n\n"
        formatted_response += f"人物：{character_name} ({character_age}岁，职业：{character_profession})\n"
        
        if character_secrets:
            formatted_response += "人物秘密：\n"
            for secret_type, secret_desc in character_secrets.items():
                formatted_response += f"- {secret_type}: {secret_desc}\n"
        
        # 其他必要的字段
        return formatted_response
    def generate_chapter(self, book_content, chapter_intro, prompt_file= "prompts/character_info_writer.txt") -> str:
        """生成单个人物的内容。

        Args:
            chapter_title: 章节标题。
            book_title: 书籍标题。
            book_intro: 书籍介绍。
            outline: 完整的章节大纲。
            prompt: 用于生成章节的提示。

        Returns:
            生成的章节内容。
        """
        
        prompt_args = {"script_content": str(book_content), "character_intro": str(chapter_intro)}
        prompt = read_prompt(prompt_file, prompt_args)
        for attempt in range(3):
            try:
                response = self.assistant.run(prompt, stream=False)
                response.strip()
                if response.startswith('```json'):
                    # 删除第一行和最后一行
                    # lines = response.splitlines()
                    # response = '\n'.join(lines[1:-1])
                     response = self.clean_json_response(response)

                return response
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        response = convert_latex_to_markdown(response)
        return response
    
    def format_clue_search(self, discuss_content: dict) -> str:
        """将线索 JSON 格式转化为可读文本格式。"""
        
        formatted_response = ""
        
        for scene_key, scene_data in discuss_content.items():
            scene_name = scene_data["场景名称"]
            clues = scene_data["线索"]
            
            formatted_response += f"\n场景：{scene_name}\n"
            formatted_response += "线索：\n"
            
            for idx, clue in enumerate(clues, 1):
                formatted_response += f"  {idx}. {clue}\n"
        
        return formatted_response
    def generate_clue_search(self, intro, char_outline=None,char_info=None, prompt_file = "prompts/clue_search_writer.txt") -> Tuple[str]:
        """生成剧本杀线索收集阶段等。

        Args:
            prompt: 用于生成标题和介绍的提示。

        Returns:
            包含生成的标题和介绍的元组。
        """
        prompt_args = {"script_content": intro, "character_intro": char_outline, "character_content": str(char_info)}
        prompt = read_prompt(prompt_file, prompt_args)
        #print(prompt)
        for attempt in range(3):
            try:
                response = self.assistant.run(prompt, stream=False)
                # print("没有经过处理的线索搜证")
                # print(response)
                # convert to json
                response = response.strip()
                if not response.startswith('{'):
                    response = '{' + response.split('{', 1)[1]
                if not response.endswith('}'):
                    response = response.split('}', 1)[0] + '}'

                clue_search = json.loads(response)
                # clue_search = json.dumps(clue_search, ensure_ascii=False, indent=4)
                # print("经过处理的线索搜证")
                # print(clue_search)
                #print(book_title_and_intro)
                readable_content = self.format_clue_search(clue_search)

                return readable_content
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        return response

    def format_discuss(self, discuss_content: dict) -> str:
        """将生成的讨论内容转化为可读文本格式。"""
        formatted_response = ""

        # 处理“圆桌阶段”部分
        if "圆桌阶段" in discuss_content:
            formatted_response += "圆桌阶段：\n"
            for question, question_text in discuss_content["圆桌阶段"].items():
                formatted_response += f"  {question}: {question_text}\n"

        # 处理“真相解析”部分
        if "真相解析" in discuss_content:
            formatted_response += "\n真相解析：\n"
            
            # 圆桌答案
            if "圆桌答案" in discuss_content["真相解析"]:
                formatted_response += "  圆桌答案:\n"
                for answer in discuss_content["真相解析"]["圆桌答案"]:
                    formatted_response += f"    {answer}\n"

            # 整体背景故事和设定
            if "整体背景故事和设定" in discuss_content["真相解析"]:
                formatted_response += f"\n  整体背景故事和设定:\n    {discuss_content['真相解析']['整体背景故事和设定']}\n"
            
            # 推理思路和关键线索
            if "推理思路和关键线索" in discuss_content["真相解析"]:
                formatted_response += "\n  推理思路和关键线索:\n"
                for line in discuss_content["真相解析"]["推理思路和关键线索"]:
                    formatted_response += f"    - {line}\n"

            # 问题解答
            if "问题解答" in discuss_content["真相解析"]:
                formatted_response += "\n  问题解答:\n"
                for question, answer in discuss_content["真相解析"]["问题解答"].items():
                    formatted_response += f"    {question}: {answer}\n"
            
            # 总时间线
            if "总时间线" in discuss_content["真相解析"]:
                formatted_response += "\n  总时间线:\n"
                for day, event in discuss_content["真相解析"]["总时间线"].items():
                    formatted_response += f"    {day}: {event}\n"

        # 处理“故事结局”部分
        if "故事结局" in discuss_content:
            formatted_response += f"\n故事结局:\n  {discuss_content['故事结局']}\n"
        if formatted_response=="":
            return discuss_content

        return formatted_response
    def clean_response(self, response: str) -> str:
        """清理 JSON 字符串中的多余换行符和空白字符。"""
        response = response.replace("\n", " ").replace("\r", "")
        # 去除 JSON 中的多余空白字符
        response = " ".join(response.split())
        return response
    def generate_discuss(self, intro, char_outline,clue_search_content,char_info=None, prompt_file = "prompts/discuss_writer.txt") -> Tuple[str, str]:
        """生成剧本杀线索收集阶段等。

        Args:
            prompt: 用于生成标题和介绍的提示。

        Returns:
            包含生成的标题和介绍的元组。
        """
        prompt_args = {"script_content": intro, "character_intro": char_outline, "character_content": str(char_info), "clue": str(clue_search_content)}
        prompt = read_prompt(prompt_file, prompt_args)
        #print(prompt)
        for attempt in range(3):
            try:
                response = self.assistant.run(prompt, stream=False)
                # convert to json
                response = response.strip()
                response = self.clean_response(response)
                if not response.startswith('{'):
                    response = '{' + response.split('{', 1)[1]
                if not response.endswith('}'):
                    response = response.split('}', 1)[0] + '}'

                discuss_content = json.loads(response)

                # discuss_content = json.dumps(discuss_content, ensure_ascii=False, indent=4)

                print("格式化之前为\n：",discuss_content)
                readable_content = self.format_discuss(discuss_content)
                print("格式化之后为\n：",readable_content)
                return readable_content
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        return response
    
    def generate_book(self, custom_theme=None, save_file=False,save_path = "测试结果文件/") -> None:
        """生成整本书并将其保存到文件中。

        Args:
            custom_prompts: 自定义提示的字典。可以包括 'title_intro', 'outline' 和 'chapter' 键。
        """

        print("开始生成剧本杀标题和简介...")
        theme = custom_theme if custom_theme else "万圣节恐怖之夜"
        title_and_intro = self.generate_title_and_intro(theme)
        title = title_and_intro["title"]
        num = title_and_intro["num"]
        intro = title_and_intro["intro"]
        type = title_and_intro["type"]
        print(f"剧本杀标题、简介、人数和类型:\n {title_and_intro}")

        print("\n开始生成人物简介...")
        chapters = self.generate_outline(theme, title_and_intro)
        print("人物简介:")
        print(chapters)
        # print("chapters的数据类型是：",type(chapters))
        char_outline = " ".join(chapters)
        char_outline_enter = "\n".join(chapters)
        book_intro = title_and_intro
        book_content = "#剧本名：" + title +'\n#剧本人数：'+str(num)+'\n#剧本类型：'+type+'\n#剧本简介：'+intro +"\n\n#人物简介\n"+ char_outline_enter
        # 人物剧情保存
        char_info = str()
        # 使用线程池来并行生成人物情节
        print("\n开始创作人物情节内容，时间较长（约几分钟）请等待~")
        with ThreadPoolExecutor() as executor:
            chapter_contents = list(executor.map(self.generate_chapter, [book_intro]*len(chapters), chapters))

        for i, chapter in enumerate(chapters, 1):
            print(f"\n正在生成第{i}个人物：{chapter}")
            chapter_content = chapter_contents[i-1].strip()  # 获取已生成的人物剧情
            print(chapter_content)
            char_info += f"\n\n{str(chapter_content)}"
            book_content += f"\n\n{chapter_content}"
            print(f"第{i}个人物剧情已完成。")

        print("\n开始生成线索搜证...")
        clue_search_content = self.generate_clue_search(intro, char_outline)
        print("线索搜证:")

        # print(clue_search_content,"clue_search_content的数据类型是：",type(clue_search_content))
        book_content += f"\n\n\n#线索搜证\n{clue_search_content}"


        print("\n开始生成问题与解析...")
        discuss = self.generate_discuss(intro, char_outline,clue_search_content)


        print("圆桌与解析:")
        # print(discuss,"clue_search_content的数据类型是：",type(discuss))
        book_content += f"\n\n#圆桌与解析\n{discuss}"

        print("\n整个剧本已生成完毕。")
        if save_file:
            filename = f"{save_path}{title.replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(book_content)
            
            print(f"剧本内容已保存到 {filename} 文件中。")
        return book_content

def main():
    """主函数, 演示如何使用BookWriter类。"""
    book_theme = input("请输入剧本杀的主题(如：炙手可热的模特刀鱼哥在一次聚会后神秘死亡，心理医生林雪成为首要嫌疑人。随着调查深入，隐藏的秘密逐渐浮出水面，每个角色都有自己的动机和隐情。玩家们需要通过线索搜寻和推理，揭开这场谋杀背后的真相。): ")

    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name = os.getenv("MODEL_NAME")
    script_prompt = "你是一个专业的剧本杀创作助手，正在帮助用户写剧本杀剧本。"
    print(base_url, model_name)
    save_path = "books/"
    book_writer = BookWriter(api_key, base_url, model_name, system_prompt=script_prompt)
    book_writer.generate_book(custom_theme=book_theme, save_file=True,save_path=save_path)

if __name__ == "__main__":
    main()