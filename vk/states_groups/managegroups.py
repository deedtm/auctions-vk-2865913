from vkbottle import BaseStateGroup


class ManageGroupsSG(BaseStateGroup):
    WATERFALLS = "waiting_waterfalls"
    COMMISSIONS = "waiting_commissions"
    AT_GROUP = "waiting_auctions_template_group"
    AT = "waiting_auctions_template"
    
