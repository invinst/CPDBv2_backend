from faq.models import FAQPage


def get_faq_parent_node():
    return FAQPage.get_root_nodes()[0].get_first_child()
