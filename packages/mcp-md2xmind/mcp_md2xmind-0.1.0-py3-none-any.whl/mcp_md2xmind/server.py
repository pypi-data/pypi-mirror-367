# This is a sample Python script.
import os

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from mcp.server.fastmcp import FastMCP
import md2xmind as mx

mcp = FastMCP("md2xmind")


@mcp.tool()
def md2xmind(md_path: str):
    """
    markdown转为xmind
    md_path: markdown文件的绝对路径
    """
    dir_name = os.path.dirname(md_path)
    # xmind文件名和markdown文件名相同，后缀不同
    xmind_name = os.path.basename(md_path).split('.')[0] + ".xmind"
    # xmind文件和markdown文件在同一目录下
    xmind_path = os.path.join(dir_name, xmind_name)
    # topic_name为生成的思维导图的主题，和xmind文件名相同
    topic_name = xmind_name.split('.')[0]
    mx.start_trans_file(md_path, xmind_path, topic_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mcp.run(transport='stdio')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
