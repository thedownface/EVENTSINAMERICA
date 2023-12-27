from EIA_filter import filter_email
from EIA_sender import send_email
from EIA_sender import create_email
import os
import logging
from Variables import Variable
from alerts import alert_email
import pandas as pd


facts=Variable.get('EventsInAmerica')


if __name__=="__main__":


    sender_name='Liza perez'
    sender_email=''
    sender_password=''
    sender_company='Infonautics Data Solutions '
    sender_position='Delivery Manager'
    company_website='www.infonauticsdatasolutions.com'
    
    emails_directory=os.path.join(os.getcwd(),'Emails')
    files=os.listdir(emails_directory)


    for file in files:
        headers=['Email','PROVIDER']
        df=pd.read_csv()
        expo_name=file[:-4]

        subject,body=create_email(expo_name,sender_name,sender_company,sender_position,company_website)
        
        logging.info(f'filtering Emails')
        if facts[expo_name]['emails_verified']!=1:
            df=filter_email(file)
            facts[expo_name]['emails_verified']=1
            Variable.set('EventsInAmerica',facts)
            if facts[expo_name]['emails_sent']!=1:            
                for email in df['Email']:
                    send_email(sender_email,sender_password,email,subject,body)

            logging.info(f'Emails Succesfully Sent for {expo_name}')
            facts[expo_name]['emails_sent']=1
            Variable.set('EventsInAmerica',facts)
            alert_email(expo_name)



