import random

"""
按照给定的语法生成句子
"""


def generate(start):
    simple_grammar = """
        sentence => noun_phrase verb_phrase
        noun_phrase => Article Adj* noun
        Adj* => null | Adj Adj*
        verb_phrase => verb noun_phrase
        Article => 一个 | 这个
        noun => 女人 | 篮球 | 桌子 | 小猫
        verb => 看着 | 听着 | 看见
        Adj => 蓝色的 | 好看的 | 小小的 | 年轻的
    """

    # 语法词映射，元组类型表示从中随机取出一个
    grammar_dict = {
        'sentence': ['noun_phrase', 'verb_phrase'],
        'noun_phrase': ['Article', 'Adj*', 'noun'],
        'Adj*': ('', ['Adj', 'Adj*']),
        'verb_phrase': ['verb', 'noun_phrase'],
        'Article': ('一个', '这个'),
        'noun': ('女人', '篮球', '桌子', '小猫'),
        'verb': ('看着', '听着', '看见'),
        'Adj': ('蓝色的', '好看的', '小小的', '年轻的')
    }

    def random_list(l):
        """
        在列表中随机取一个元素
        :param l:
        :return:
        """
        return random.choice(l)

    # 结果词语列表
    exp_list = []

    def generate_sentence(word):
        """
        递归生成词语列表
        :param word: 语法词
        :return:
        """
        if word not in grammar_dict:
            # 不是语法词，添加词语
            exp_list.append(word)
            return
        words = grammar_dict[word]
        # 是否需要随机
        if isinstance(words, tuple):
            # 随机取一个
            item = random_list(words)
            if isinstance(item, str):
                # 随机取出的是词语
                generate_sentence(item)
                return
            else:
                # 随机取出的是列表
                words = item
        for item in words:
            generate_sentence(item)

    generate_sentence(start)
    return ''.join(exp_list)


for _ in range(10):
    print(generate('sentence'))
print(generate('noun_phrase'))
print(generate('111'))
