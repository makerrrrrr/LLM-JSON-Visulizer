import json
import platform
import matplotlib.patches as patches
import matplotlib.pyplot as plt

# 根据操作系统设置字体
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS',
                                       'PingFang SC', 'Hiragino Sans GB']
elif platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
else:  # Linux
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'WenQuanYi Micro Hei']


def visualize_ppt_layout(json_data):
    # 解析JSON数据
    page_size = json_data['page_size']
    page_width = page_size['width']
    page_height = page_size['height']  # 保存页面总高度，用于后续坐标转换
    elements = json_data['elements']

    # 创建图形和坐标轴
    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制PPT页面边界（此时仍用左下角坐标，但后续会翻转y轴）
    page_rect = patches.Rectangle(
        (0, 0),  # 初始左下角坐标，翻转y轴后会变成左上角
        page_width,
        page_height,
        linewidth=2,
        edgecolor='black',
        facecolor='white'
    )
    ax.add_patch(page_rect)

    # 定义不同类型元素的颜色
    color_map = {
        'title': 'lightblue',
        'text': 'lightgreen',
        'image': 'lightyellow',
        'table': 'pink'
    }

    # 绘制每个元素（核心修改：适配PPT左上角原点逻辑）
    for elem in elements:
        # 1. 计算元素在PPT逻辑中的关键坐标（左上角原点）
        elem_center_x = elem['center']['x']
        elem_center_y = elem['center']['y']  # PPT逻辑：中心y坐标（从左上角往下算）
        elem_width = elem['size']['width']
        elem_height = elem['size']['height']

        # 2. 转换为matplotlib需要的“左下角坐标”（适配翻转后的y轴）
        # PPT中元素的左上角y = 中心y - 高度/2；matplotlib需要左下角y = 页面高度 - (中心y + 高度/2)
        x = elem_center_x - elem_width / 2  # x轴逻辑一致，无需修改
        y = page_height - (elem_center_y + elem_height / 2)  # 关键转换：适配左上角原点

        # 选择颜色
        color = color_map.get(elem['type'], 'gray')

        # 绘制元素矩形
        rect = patches.Rectangle(
            (x, y),
            elem_width,
            elem_height,
            linewidth=1,
            edgecolor='black',
            facecolor=color,
            alpha=0.7
        )
        ax.add_patch(rect)

        # 添加元素内容标签（文本位置也需要转换y坐标）
        text_y = page_height - elem_center_y  # 文本中心y坐标转换
        plt.text(
            elem_center_x,
            text_y,  # 转换后的文本中心y坐标
            elem['content'],
            ha='center',
            va='center',
            fontsize=8
        )

        # 添加元素类型标签（类型标签在元素左上角，同样转换y坐标）
        label_x = x  # 元素左下角x = 左上角x（x轴一致）
        label_y = page_height - (elem_center_y - elem_height / 2)  # 元素左上角y转换
        plt.text(
            label_x + 0.1,
            label_y - 0.1,  # 稍微向上偏移一点，避免贴边
            elem['type'],
            ha='left',
            va='top',  # 改为top对齐，贴合左上角
            fontsize=6,
            color='darkred'
        )

    # 关键：翻转y轴，让左上角成为原点（符合PPT逻辑）
    ax.invert_yaxis()

    # 设置坐标轴范围和比例（x从0到页面宽度，y从0到页面高度）
    ax.set_xlim(0, page_width)
    ax.set_ylim(0, page_height)
    ax.set_aspect('equal')  # 保持宽高比，避免变形

    # 添加网格（辅助判断位置）
    ax.grid(True, linestyle='--', alpha=0.7)

    # 设置标题和标签（明确标注坐标逻辑）
    plt.title('PPT Layout Visualization (Origin: Top-Left Corner)')
    plt.xlabel('Width (inches) →')
    plt.ylabel('Height (inches) ↓')  # 标注y轴向下为正

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 读取本地JSON文件（确保example.json和代码在同一目录）
    try:
        with open('ppt_layout.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 可视化
        visualize_ppt_layout(data)
    except FileNotFoundError:
        print("提示：未找到example.json文件，请确保文件路径正确！")
