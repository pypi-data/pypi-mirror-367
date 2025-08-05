
from django.core.paginator import Paginator
# 根据页码分配数据
def get_page_data(page_num, page_size, queryset, shujuzhuanhuanqi):
    # 判断 page_num 或者 page_size 是否为空和是否不是数字
    # 先检查类型，再判断是否为有效数字
    if not isinstance(page_num, int) or page_num <= 0:
        # 处理无效页码的情况，比如返回错误信息或设置默认值
        page_num = 1  # 例如设置默认值为第一页
    if not isinstance(page_size, int) or page_size <= 0:
        page_size = 1
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.page(page_num)

    user_list = [shujuzhuanhuanqi(user) for user in page_obj]

    return {
        "data_list": user_list,
        "number": page_obj.number,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "num_pages": paginator.num_pages,
    }
