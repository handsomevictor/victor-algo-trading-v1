import os
import openai
import concurrent.futures
from tqdm import tqdm

"""
逻辑：
早上的时候爬虫新闻网站，然后把所有的句子，先判断长度，然后输入到openai，然后输出一个分数，然后输出一个分类，发表在grafana上

然后把它选出来的最具有影响力的新闻打印出来，写到某个地方
"""

openai.organization = 'org-A7bxp9mqlMdZnQHEtMCfkhus'
openai.api_key = os.getenv('OPENAI_API_KEY')


# print(openai.Model.list())


def chat_with_gpt35turbo(message, max_tokens=1500):
    """
    需要多跑几次，求平均值
    """
    conversation_history = []

    # Add the user's message to the conversation history
    conversation_history.append({"role": "user", "content": message})

    # Format the conversation history for the API call
    messages = [{"role": message["role"], "content": message["content"]} for message in conversation_history]

    # Make the API call to GPT-3.5-turbo
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.5,
    )

    # Extract the assistant's reply
    assistant_reply = response.choices[0].message['content']
    return assistant_reply


if __name__ == "__main__":
    key_sentences = []
    with open('cnbc.txt', 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            line = line.strip()
            # add index in front
            line = str(idx + 1) + '. ' + line + '\n'
            key_sentences.append(line)

    order = 'Act as a professional financial analyze in top hedge fund, ' \
            'analyze the following financial news titles, and give me a reply that contains two parts. ' \
            'In the first part, for each sentence, you give me 2 outputs: ' \
            'First output: You give a score to the news based on how good the news is. ' \
            'The score range is 0 to 10, ' \
            '0 means extremely negative, ' \
            '10 means extremely good, 5 means neutral. ' \
            'The scores you give to these news should approximately follow a normal distribution. ' \
            'Second output: you give a classification of the news, ' \
            'the classification can only be chosen from ' \
            'Politics, Energy, Real Estate, Consumer Finance, Macro Economy, ' \
            'Insurance, International Trade, Education, General Business, Tech, Financial Markets, ' \
            'Policy & Regulation, ESG, Health, Accidents, Disasters, Climate. ' \
            'The return format for first part is as follows: ' \
            'For one sentence in one line: ' \
            'my original news index: Score: only your score, no text, ' \
            'my original news index: Classification: only your choice from my classification. ' \
            'You should analyze the sentences according to their original order. ' \
            'In the second part, choose 5 news that you think are most influential ' \
            'among investors and traders, index them from 1 to 5 in the following format: ' \
            'Top 5 influential news: (new line) 1. first news. (new line) 2. second news. etc. ' \
            'Remember to remove the index before each news. ' \
            'Remember do not change the title of the news that I gave you. ' \
            'Remember to add an empty line between these 2 parts. ' \
            'Only reply what I asked, you should reply 34 lines. ' \
            'Target Sentences are as follows: '

    sentences = order + ' '.join(key_sentences)

    res = chat_with_gpt35turbo(sentences, max_tokens=1500)
    print(res)

    with open('cnbc_results8.txt', 'w', encoding='utf-8') as f:
        f.write(res)

    # read data
    with open('cnbc_results7.txt', 'r', encoding='utf-8') as f:
        # read all
        lines = f.read()
        lines1, lines2 = lines.split('Top 5 influential news:')

        # read line by line in line1
        lines1 = lines1.splitlines()
        lines1 = [line.strip() for line in lines1]
        lines1 = [line for line in lines1 if line != '']
        # read line by line in line2
        lines2 = lines2.splitlines()
        lines2 = [line.strip() for line in lines2]
        lines2 = [line for line in lines2 if line != '']

    print(lines1)
    print(lines2)
