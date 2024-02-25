

# import manage
# from mobile_api.models import *

# from utils import *
# import string, random, names
# from datetime import datetime, date, timedelta, timezone
# import time
# import os
# from utils import *
# import random, string
# import requests, json
# from utils import RegexPack

# from datetime import date

# withdraw = MobileUserWithdrawHistory.objects.get(id=1)
# withdraw.status = withdraw.Status.PROCESSING
# withdraw.save()

# obj = MobileExpertSchedule.objects.get(id = 4)
# obj.date = date.today()
# obj.save()

# user = MobileUserExpertExtra.objects.get(user_id = 1)
# user.balance = 5000
# user.save(force_update=True)

# MobileUserWithdrawHistory.objects.create(
#     user_id = 1,
#     bank_name = "Сбер",
#     card = "0000000000000000",
#     full_name = "Геннадий Красножопов",
# )



# user = MobileUserModel.objects.get(id=10)

# user.phone = "74444444444"

# user.save()

# client_ids = [i[0] for i in MobileUserClientExtra.objects.values_list("user")]

# for i in client_ids:
#     MobileClientReferalRelation(
#         user_id=i,
#         by_id = 11,
#         points = random.randint(100, 5000),
#     ).save(force_insert=True)



"""

for n in ["Гадание", "Медитация", "Аквапланирование", "Вознесение до небес", "Снятие с небес", "Уроки вождения бизнес-джета"]:
    MobileExpertServiceCategory(name=n).save(force_insert=True)

category_ids = [i[0] for i in MobileExpertServiceCategory.objects.values_list("id")]

for x in range(10):
    user = MobileUserModel(
        phone = "7" + generate_authtoken(10, string.digits),
        first_name = names.get_first_name(),
        last_name = names.get_last_name(),
        email = generate_authtoken(10) + "@mail.ru",
        role = MobileUserModel.Role.EXPERT
    )
    user.save(force_insert=True)
    
    expert = MobileUserExpertExtra(
        user = user,
        description = random.choice(FILL_TEXTS)
    )
    expert.save(force_insert=True)
    
    client = MobileUserClientExtra(user = user)
    client.save(force_insert=True)
    
    for x in range(random.randint(5, 10)):
        MobileExpertService(
            owner = expert,
            category_id = random.choice(category_ids),
            name = "Услуга " + generate_authtoken(10, string.digits),
            price = random.randint(20, 1000),
            telegram_link = random.choice([None, "+6561561564"])
        ).save(force_insert=True)
        
    for x in range(random.randint(5, 10)):
        MobileUserWithdrawHistory(
            user = user,
            count = random.randint(20, 1000),
            status = random.choice([
                MobileUserWithdrawHistory.Status.PROCESSING,
                MobileUserWithdrawHistory.Status.DONE,
                MobileUserWithdrawHistory.Status.FAIL
            ])
        ).save(force_insert=True)
    
    for i in range(5):
        schedule = MobileExpertSchedule(
            owner = expert,
            date = date.today() + timedelta(days=i)
        )
        schedule.save(force_insert=True)
        
        # for t in random.choices(range(1, 20), k=5):
        #     MobileExpertScheduleFreetime(
        #         date = schedule,
        #         hour = t,
        #     ).save(force_insert=True)


client_ids = [i[0] for i in MobileUserClientExtra.objects.values_list("user")]
services_ids = list(MobileExpertService.objects.values_list("id", "owner_id"))

for service in services_ids:
    schedules = [i[0] for i in MobileExpertSchedule.objects.filter(
        owner_id = service[1]
    ).values_list("id")]
    
    for schedule in schedules:
        for t in range(2, 10):
            MobileClientServicePurchase(
                client_id = random.choice(client_ids),
                service_id = int(service[0]),
                date_id = schedule,
                hour = t,
                price = 1500,
                feedback = random.choice(FILL_TEXTS),
                rating = random.randint(1, 5),
                status = MobileClientServicePurchase.Status.ARCHIVED_FEEDBACK
            ).save(force_insert=True)
    
    
for x in range(40):
    MobileNewsModel(
        title = "Новость " + generate_authtoken(10, string.digits),
        content = random.choice(FILL_TEXTS)
    ).save(force_insert=True)

"""
