import datetime
from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from sys_user.models import User, Department, Organisation

# Create your models here.


# class Vendor(models.Model):
#     name = models.CharField(max_length=80, unique=True)
#     email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
#     phone_regex = RegexValidator(regex=r'^(\+\d{1,3}[- ]?)?\d{9,13}$', message="Phone number must be entered in the format: '+234-0000000000'. Up to 13 digits allowed.")
#     phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True) 
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     date_created = models.DateTimeField(auto_now_add=True)
#     dateUpdated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.id}"

# #necesssary for vendors with multiple banks
# class VendorBank(models.Model):
#     vendorID = models.ForeignKey(Vendor, on_delete=models.CASCADE)
#     account_name = models.CharField(max_length=80)
#     account_bank = models.CharField(max_length=80)
#     account_number = models.IntegerField()
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE) #A staff different from the staff who created the vendor may want to add a new bank details for the vendor
#     date_created = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("account_bank", "account_number")

#standard table storing all formats
class Format(models.Model):
    orgID = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=80) #e.g consulting
    format = models.CharField(max_length=250)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

class Requisition(models.Model):
    def validate_date(date):
        if date < timezone.now():
            raise ValidationError("Date cannot be in the past")

    title = models.CharField(max_length=80)
    due_date = models.DateTimeField(null=True, blank=True) #If there's a deadline for the requisition
    schedule_send = models.DateTimeField(validators=[validate_date], null=True, blank=True) 
    SCHEDULE = [
        ('SP', 'Pending'), 
        ('SS', 'Sent'),
    ]
    scheduleStatus = models.CharField(max_length=3, choices=SCHEDULE, null=True, blank=True,default='SP')
    created_by = models.ForeignKey(User, related_name='req_user', on_delete=models.CASCADE)
    # approved_by = models.ForeignKey(User, related_name='req_staff', on_delete=models.CASCADE)
    purpose = models.TextField()
    #status is now determined by the reqApprover table
    Currency = [
        ('D', 'Dollar'), 
        ('N', 'Naira'),
        ('E', 'Euro'),
        ('P', 'Pound'),
        ('Y', 'Yen'),
    ]
    reqCurrency = models.CharField(max_length=2, choices=Currency, default='N')
    ### START - In case staff wants to copy another staff or an entire department. If dept, all users will receive notification, but can't perform any action except approvers.
    userinCopy = models.ForeignKey(User, related_name='req_staff2', on_delete=models.CASCADE, null=True, blank=True)
    deptinCopy = models.ForeignKey(Department, related_name='req_dept', on_delete=models.CASCADE, null=True, blank=True)
    ###### END
    date_created = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "-date_created" #return values based on date in descending order

    def __str__(self):
        return f"{self.id}"

#pivot table for created requisitions and formats
class ReqFormat(models.Model):
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    format_id = models.ForeignKey(Format, on_delete=models.CASCADE)
    req_number = models.PositiveSmallIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

class ReqItem(models.Model):
    reqID = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    itemName = models.CharField(max_length=80)
    itemDescription = models.CharField(max_length=250)
    itemQty = models.IntegerField()
    itemBaseCost = models.DecimalField(max_digits=25, decimal_places=2)
    itemTotalCost = models.DecimalField(max_digits=25, decimal_places=2)
    itemAttachment = models.URLField(null=True, blank=True) #store invoice or any file regarding the requisition
    # Vendor information 
    vendor_Name = models.CharField(max_length=80, null=True, blank=True)
    vendor_ACCTname = models.CharField(max_length=80, null=True, blank=True)
    vendor_ACCTbank = models.CharField(max_length=30, null=True, blank=True)
    vendor_ACCTnumber = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("itemName", "vendor_Name")

class ReqApprover(models.Model):
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    approver_id = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS = [
        ('P', 'Pending'), 
        ('A', 'Approved'),
        ('D', 'Declined'),
    ]
    reqStatus = models.CharField(max_length=2, choices=STATUS, default='P')
    dateUpdated = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "-dateUpdated" 
    
    def __str__(self):
        return f"{self.reqStatus}"

# class ReqReceiptFile(models.Model):
#     drive_receipt = models.URLField(max_length=200, null=True, blank=True) #url for receipt from any of the file storage, gdrive, odrive, etc.
#     local_receipt = models.FileField(upload_to='receipt-uploads/%Y/%m', null=True,  blank=True) #if local storage is selected, store files on server
#     date_uploaded = models.DateTimeField(auto_now=True)

class ReqFile(models.Model):
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # files = models.ManyToManyField(ReqReceiptFile)
    drive_receipt = models.URLField(max_length=200, null=True, blank=True) #url for file from any of the file storage, gdrive, odrive, etc.
    local_receipt = models.FileField(upload_to='file-uploads/%Y/%m', null=True,  blank=True) #if local storage is selected, store files on server
    date_uploaded = models.DateTimeField(auto_now_add=True)

# For recurring requisitions. This sends a new requisition and pushes data to the requisition table
class ReqRepeat(models.Model):
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    Frequency = [
        ('D', 'Date'), 
        ('W', 'Week'),
        ('M', 'Month'),
        ('Y', 'Year'),
        ('C', 'Custom'),
    ]
    reqFrequency = models.CharField(max_length=2, choices=Frequency)
    custom_repeat_day = models.PositiveSmallIntegerField(null=True, blank=True) #This is the number before the day or week
    custom_repeat_freq = models.CharField(max_length=2, choices=Frequency, null=True, blank=True)
    Days = [
        ('S', 'Sunday'), 
        ('M', 'Monday'),
        ('T', 'Tuesday'),
        ('W', 'Wednesday'),
        ('T', 'Thursday'),
        ('F', 'Friday'),
        ('S', 'Saturday'),
    ]
    custom_repeat_weekday = models.CharField(max_length=2, choices=Days)
    custom_repeat_EndDate = models.DateTimeField()
    next_send_date = models.DateTimeField(null=False, blank=False) #this is computed based on users set date; then updated after every successfull schedule-send. If last schedule is reached, set date to last date.
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

#for comments made on a requisition
class Comment(models.Model):
    comment = models.TextField()
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"

#for reminders on a requisition
class Reminder(models.Model):
    req_id = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    note = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}"

