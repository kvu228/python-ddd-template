"""Application constants."""

# Cache keys
CACHE_KEY_USER_PREFIX = "user:"
CACHE_KEY_ORDER_PREFIX = "order:"

# Event types
EVENT_USER_REGISTERED = "user_registered"
EVENT_USER_UPDATED = "user_updated"
EVENT_USER_DEACTIVATED = "user_deactivated"
EVENT_ORDER_CREATED = "order_created"
EVENT_ORDER_CONFIRMED = "order_confirmed"
EVENT_ORDER_CANCELLED = "order_cancelled"

# Task names
TASK_SEND_WELCOME_EMAIL = "workers.users.tasks.send_welcome_email"
TASK_SEND_ORDER_CONFIRMATION = "workers.users.tasks.send_order_confirmation"
TASK_PROCESS_PAYMENT = "workers.orders.tasks.process_payment"
TASK_SYNC_ORDER_TO_READ_MODEL = "workers.orders.tasks.sync_order_to_read_model"

# Scheduled tasks
SCHEDULED_CLEANUP_EXPIRED_ORDERS = "workers.scheduled.periodic_tasks.cleanup_expired_orders"
SCHEDULED_GENERATE_DAILY_REPORT = "workers.scheduled.periodic_tasks.generate_daily_report"


