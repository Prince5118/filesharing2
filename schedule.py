from crontab import CronTab

# Name of User for whom cronjob will be added
my_cron = CronTab(user='root')

# Actual CronJob command
job = my_cron.new(command=' /root/pjlogin/fus-2/script.py >> ~/pjlogin/fus-2/deletingfolders.txt 2>&1',comment='Deleting Folders')

# Time after which CronJob should run
# Repeat after every 5 minutes
job.minute.every(5)

# Adding the CronJob
my_cron.write()
