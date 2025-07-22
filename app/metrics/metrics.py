from prometheus_client import Counter, Gauge
from app.repository.pg import get_users_count, get_active_users_count
import asyncio

users_registered_total = Counter(
    'users_registered_total',
    'Total number of registered users'
)

users_current_total = Gauge(
    'users_current_total',
    'Total number of registered users in the database'
)

requests_total = Counter(
    'requests_total',
    'Total count of requests',
    ['endpoint']
)

active_users_percentage = Gauge(
    'active_users_percentage',
    'Percentage of users who are active (last_use - created_at <= 7 days)'
)

def update_total_users():
    count = get_users_count()
    users_current_total.set(count)


async def update_total_users():
    count = await get_users_count()
    users_current_total.set(count)

async def update_active_users_percentage():
    total_users = await get_users_count()
    active_users = await get_active_users_count()

    if total_users > 0:
        percentage = (active_users / total_users) * 100
        active_users_percentage.set(percentage)
    else:
        active_users_percentage.set(0)

async def start_internal_metrics_updating():
    while True:
        await update_total_users()
        await update_active_users_percentage()
        await asyncio.sleep(60)